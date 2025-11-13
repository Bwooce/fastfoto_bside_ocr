"""
Interactive processor for Claude Code sessions.

Helper functions for analyzing prepared FastFoto images using Claude Code's Read tool.
Coordinates with preprocessing results and generates/applies proposal files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Local imports
from file_discovery import FileDiscovery, PhotoPair
from claude_prompts import PHOTO_BACK_OCR_PROMPT, parse_claude_response
from date_parser import DateParser
from exif_writer import ExifWriter
from proposal_generator import ProposalGenerator, ProposalEntry

logger = logging.getLogger(__name__)


class AnalysisResult:
    """Represents the analysis result for one back scan."""

    def __init__(self, prepared_path: Path, original_path: Path,
                 claude_response: str, parsed_data: Optional[Dict],
                 extracted_metadata: Optional[Dict]):
        self.prepared_path = prepared_path
        self.original_path = original_path
        self.claude_response = claude_response
        self.parsed_data = parsed_data
        self.extracted_metadata = extracted_metadata
        self.error = None

    @property
    def is_successful(self) -> bool:
        """Check if analysis was successful."""
        return self.parsed_data is not None and self.extracted_metadata is not None

    @property
    def is_useful(self) -> bool:
        """Check if useful metadata was extracted."""
        return (self.parsed_data and
                self.parsed_data.get('is_useful', False) and
                self.extracted_metadata and
                len(self.extracted_metadata) > 0)

    @property
    def confidence(self) -> float:
        """Get confidence score."""
        if self.parsed_data:
            return self.parsed_data.get('confidence', 0.0)
        return 0.0


class InteractiveProcessor:
    """Helper for Claude Code interactive processing of FastFoto images."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize interactive processor.

        Args:
            config_path: Path to config.yaml (default: ../config.yaml)
        """
        # Load config if provided
        self.config = {}
        if config_path:
            import yaml
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)

        # Initialize components
        self.date_parser = DateParser(
            collection_date_range=(
                self.config.get('date_parsing', {}).get('min_year', 1960),
                self.config.get('date_parsing', {}).get('max_year', 2010)
            )
        )
        self.exif_writer = ExifWriter(
            exiftool_path=self.config.get('exiftool_path', 'exiftool')
        )

        # Analysis state
        self.mapping_data = None
        self.prepared_images = []
        self.analysis_results = []
        self.stats = {
            'total_prepared': 0,
            'analyzed': 0,
            'successful': 0,
            'useful': 0,
            'errors': 0,
            'avg_confidence': 0.0
        }

    def load_prepared_images(self, prepared_dir: Path) -> List[Path]:
        """
        Load prepared images from preprocessing output directory.

        Args:
            prepared_dir: Directory containing prepared images and mapping file

        Returns:
            List of prepared image paths

        Raises:
            FileNotFoundError: If mapping file not found
            ValueError: If mapping file is invalid
        """
        mapping_file = prepared_dir / "preprocessing_mapping.json"

        if not mapping_file.exists():
            raise FileNotFoundError(
                f"Preprocessing mapping file not found: {mapping_file}\n"
                "Make sure you ran the preprocessing step first:\n"
                f"python src/preprocess_images.py <source> --output {prepared_dir}"
            )

        # Load mapping
        with open(mapping_file, 'r') as f:
            self.mapping_data = json.load(f)

        logger.info(f"Loaded mapping for {self.mapping_data['total_files']} files")

        # Get list of prepared images
        self.prepared_images = []
        mapping = self.mapping_data['mapping']

        for original_path, prepared_path in mapping.items():
            prepared = Path(prepared_path)
            if prepared.exists():
                self.prepared_images.append(prepared)
            else:
                logger.warning(f"Prepared image not found: {prepared}")

        self.stats['total_prepared'] = len(self.prepared_images)

        logger.info(f"Found {len(self.prepared_images)} prepared images ready for analysis")

        return self.prepared_images

    def get_original_path_for_prepared(self, prepared_path: Path) -> Optional[Path]:
        """
        Get the original image path for a prepared image.

        Args:
            prepared_path: Path to prepared image

        Returns:
            Path to original image, or None if not found
        """
        if not self.mapping_data:
            return None

        prepared_str = str(prepared_path.resolve())
        mapping = self.mapping_data['mapping']

        # Reverse lookup
        for original_str, prep_str in mapping.items():
            if Path(prep_str).resolve() == Path(prepared_str).resolve():
                return Path(original_str)

        return None

    def analyze_image(self, prepared_path: Path, claude_response: str) -> AnalysisResult:
        """
        Process Claude's analysis of a prepared image.

        Args:
            prepared_path: Path to the prepared image that was analyzed
            claude_response: Raw response from Claude's Read tool

        Returns:
            AnalysisResult object
        """
        original_path = self.get_original_path_for_prepared(prepared_path)
        if not original_path:
            result = AnalysisResult(prepared_path, None, claude_response, None, None)
            result.error = "Could not find original path for prepared image"
            return result

        try:
            # Parse Claude's JSON response
            parsed_data = parse_claude_response(claude_response)

            # Extract metadata
            extracted_metadata = self.extract_metadata_from_analysis(parsed_data)

            result = AnalysisResult(
                prepared_path=prepared_path,
                original_path=original_path,
                claude_response=claude_response,
                parsed_data=parsed_data,
                extracted_metadata=extracted_metadata
            )

            self.analysis_results.append(result)
            self.stats['analyzed'] += 1

            if result.is_successful:
                self.stats['successful'] += 1

            if result.is_useful:
                self.stats['useful'] += 1

            logger.info(f"Analyzed {prepared_path.name}: "
                       f"useful={result.is_useful}, confidence={result.confidence:.2f}")

            return result

        except Exception as e:
            result = AnalysisResult(prepared_path, original_path, claude_response, None, None)
            result.error = str(e)
            self.stats['errors'] += 1
            logger.error(f"Error analyzing {prepared_path.name}: {e}")
            return result

    def extract_metadata_from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and format metadata from Claude's analysis.

        Args:
            analysis: Parsed JSON from Claude Vision response

        Returns:
            Dict with standardized metadata fields
        """
        metadata = {}

        # Extract all dates found
        all_dates = analysis.get('all_dates_found', [])
        if all_dates:
            # Use date parser to get best date
            parsed_date = self.date_parser.get_best_date(all_dates)
            if parsed_date:
                metadata['date'] = parsed_date

        # Extract location information
        zone4 = analysis.get('zone_4_handwritten', {})
        if zone4 and zone4.get('locations'):
            locations = zone4['locations']
            if locations and len(locations) > 0:
                # Take first location as primary
                metadata['location_name'] = locations[0]
                # TODO: Could add geocoding here to get coordinates

        # Extract people names for keywords
        keywords = []
        if zone4 and zone4.get('people'):
            keywords.extend(zone4['people'])

        # Extract events
        if zone4 and zone4.get('events'):
            keywords.extend(zone4['events'])

        if keywords:
            metadata['keywords'] = keywords

        # Extract descriptive text
        if zone4 and zone4.get('descriptive_text'):
            desc_text = zone4['descriptive_text']
            if desc_text and desc_text.strip():
                metadata['caption'] = desc_text[:1000]  # Limit length
                metadata['user_comment'] = desc_text[:2000]

        # Extract roll/frame information
        roll_info = {}

        # From zone 1 (bottom edge machine text)
        zone1 = analysis.get('zone_1_bottom_edge', {})
        if zone1 and zone1.get('found'):
            if zone1.get('roll_id'):
                roll_info['roll_id'] = zone1['roll_id']
            if zone1.get('frame'):
                roll_info['frame_number'] = zone1['frame']
            if zone1.get('lab_code'):
                roll_info['lab_code'] = zone1['lab_code']

        # From zone 2 (center APS data)
        zone2 = analysis.get('zone_2_center', {})
        if zone2 and zone2.get('found'):
            if zone2.get('roll_id'):
                roll_info['roll_id'] = zone2['roll_id']
            if zone2.get('frame'):
                roll_info['frame_number'] = zone2['frame']

        # Add roll info to metadata
        if roll_info:
            metadata.update(roll_info)

        # Add processing metadata
        metadata['confidence'] = analysis.get('confidence', 0.0)

        # Detect language
        if zone4 and zone4.get('language'):
            metadata['language'] = zone4['language']

        return metadata

    def generate_proposal(self, output_path: Path = None) -> ProposalGenerator:
        """
        Generate proposal file from analysis results.

        Args:
            output_path: Path for proposal file (default: /tmp/exif_updates_proposal.txt)

        Returns:
            ProposalGenerator object
        """
        if output_path is None:
            output_path = Path("/tmp/exif_updates_proposal.txt")

        generator = ProposalGenerator(output_path)

        logger.info(f"Generating proposal from {len(self.analysis_results)} analysis results...")

        for result in self.analysis_results:
            if result.error:
                # Add error entry
                generator.add_entry(ProposalEntry(
                    original_path=result.original_path,
                    back_path=result.prepared_path,
                    current_exif={},
                    proposed_updates={},
                    metadata={
                        'confidence': 0.0,
                        'warnings': [f'Analysis error: {result.error}']
                    }
                ))
                continue

            if not result.is_useful:
                # Add no-update entry
                generator.add_entry(ProposalEntry(
                    original_path=result.original_path,
                    back_path=result.prepared_path,
                    current_exif={},
                    proposed_updates={},
                    metadata={
                        'confidence': result.confidence,
                        'warnings': ['No useful metadata extracted']
                    }
                ))
                continue

            # Read current EXIF
            current_exif = self.exif_writer.read_exif(result.original_path)

            # Build proposed updates
            proposed_updates = self.exif_writer.build_metadata_dict(
                **result.extracted_metadata
            )

            # Create proposal entry
            entry = ProposalEntry(
                original_path=result.original_path,
                back_path=result.prepared_path,
                current_exif=current_exif,
                proposed_updates=proposed_updates,
                metadata={
                    'confidence': result.confidence,
                    'language': result.extracted_metadata.get('language', 'unknown'),
                    'warnings': []
                }
            )

            generator.add_entry(entry)

        # Write proposal file
        generator.write(group_by_directory=True)

        # Update statistics
        self._update_final_stats()

        return generator

    def apply_proposal(self, proposal_path: Path, source_dir: Path = None, dry_run: bool = False) -> int:
        """
        Apply approved changes from proposal file.

        Args:
            proposal_path: Path to proposal file
            source_dir: Directory containing original photos (for path resolution)
            dry_run: If True, don't actually write EXIF or move files

        Returns:
            Number of images updated
        """
        if not proposal_path.exists():
            logger.error(f"Proposal file not found: {proposal_path}")
            return 0

        logger.info(f"Applying proposal from: {proposal_path}")

        updated_count = 0
        organized_count = 0
        skipped_count = 0
        error_count = 0

        try:
            # Read and parse proposal file
            with open(proposal_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse entries from proposal file
            entries = self._parse_proposal_content(content)

            logger.info(f"Found {len(entries)} entries in proposal")

            for entry in entries:
                if entry.get('skip', False):
                    logger.info(f"Skipping {entry['original_path']} (marked as SKIP)")
                    skipped_count += 1
                    continue

                if not entry.get('proposed_updates'):
                    logger.info(f"No updates for {entry['original_path']}")
                    skipped_count += 1
                    continue

                # Resolve relative filename to full path
                filename = entry['original_path']
                if source_dir and not Path(filename).is_absolute():
                    # Search for the file in source directory (recursively)
                    original_path = self._find_file_in_directory(source_dir, filename)
                    if not original_path:
                        logger.error(f"Image file not found: {filename} in {source_dir}")
                        error_count += 1
                        continue
                else:
                    original_path = Path(filename)

                # Resolve back scan path similarly
                back_filename = entry.get('back_path')
                if back_filename and source_dir and not Path(back_filename).is_absolute():
                    back_path = self._find_file_in_directory(source_dir, back_filename)
                else:
                    back_path = Path(back_filename) if back_filename else None
                proposed_updates = entry['proposed_updates']

                try:
                    # Apply EXIF updates
                    if not dry_run:
                        success = self.exif_writer.write_exif(
                            original_path,
                            proposed_updates,
                            overwrite_original=True  # No backup files
                        )

                        if success:
                            updated_count += 1
                            logger.info(f"Updated EXIF for {original_path.name}")

                            # Move back scan to processed/ directory
                            if back_path and back_path.exists():
                                organized = self.exif_writer.organize_processed_back_scan(back_path)
                                if organized:
                                    organized_count += 1
                        else:
                            logger.error(f"Failed to update EXIF for {original_path.name}")
                            error_count += 1
                    else:
                        # Dry run - just log what would be done
                        logger.info(f"[DRY RUN] Would update {original_path.name} with {len(proposed_updates)} fields")
                        if back_path and back_path.exists():
                            logger.info(f"[DRY RUN] Would move {back_path.name} to processed/")
                        updated_count += 1

                except Exception as e:
                    logger.error(f"Error processing {original_path}: {e}")
                    error_count += 1

        except Exception as e:
            logger.error(f"Error reading proposal file: {e}")
            return 0

        # Print results
        print(f"\n{'='*80}")
        print(f"APPLY PROPOSAL RESULTS")
        print(f"{'='*80}")
        print(f"✅ Photos updated:        {updated_count}")
        print(f"📁 Back scans organized:  {organized_count}")
        print(f"⏭️  Entries skipped:       {skipped_count}")
        print(f"❌ Errors:               {error_count}")
        print(f"{'='*80}\n")

        if not dry_run and organized_count > 0:
            print(f"✨ Processed back scans moved to 'processed/' subdirectories")
            print(f"💡 Tip: To reprocess, move files back from processed/ directories\n")

        return updated_count

    def _parse_proposal_content(self, content: str) -> List[Dict]:
        """
        Parse proposal file content into structured entries.

        Args:
            content: Raw proposal file content

        Returns:
            List of proposal entries
        """
        entries = []
        current_entry = None

        for line in content.split('\n'):
            line = line.strip()

            # Skip empty lines and headers
            if not line or line.startswith('=') or line.startswith('SUMMARY:') or line.startswith('INSTRUCTIONS:'):
                continue

            # Check for SKIP marker
            if line.startswith('SKIP:'):
                if current_entry:
                    current_entry['skip'] = True
                continue

            # New entry
            if line.startswith('[') and '] ' in line:
                if current_entry:
                    entries.append(current_entry)

                # Extract original path from entry header
                parts = line.split('] ', 1)
                if len(parts) > 1:
                    original_path = parts[1].strip()
                    current_entry = {
                        'original_path': original_path,
                        'skip': False,
                        'proposed_updates': {},
                        'back_path': None
                    }
                continue

            if current_entry is None:
                continue

            # Extract back scan path
            if line.startswith('Back scan:'):
                current_entry['back_path'] = line.split(':', 1)[1].strip()
                continue

            # Parse EXIF field updates
            if ':' in line and not line.startswith('  ') and 'EXIF' not in line and 'METADATA' not in line:
                field, value = line.split(':', 1)
                field = field.strip()
                value = value.strip()

                # Skip descriptive fields
                if field in ['Confidence', 'Source', 'Language', 'Note', 'Zones with data']:
                    continue

                if value and value != '<not set>':
                    current_entry['proposed_updates'][field] = value

        # Add last entry
        if current_entry:
            entries.append(current_entry)

        return entries

    def print_statistics(self):
        """Print processing statistics."""
        print("\n" + "="*80)
        print("ANALYSIS STATISTICS")
        print("="*80)
        print(f"Total prepared images:       {self.stats['total_prepared']}")
        print(f"Successfully analyzed:       {self.stats['analyzed']}")
        print(f"Parsing successful:          {self.stats['successful']}")
        print(f"With useful metadata:        {self.stats['useful']}")
        print(f"Analysis errors:             {self.stats['errors']}")

        if self.stats['successful'] > 0:
            useful_rate = 100 * self.stats['useful'] / self.stats['successful']
            print(f"\nUseful metadata rate:        {useful_rate:.1f}%")
            print(f"Average confidence:          {self.stats['avg_confidence']:.2f}")

        print("="*80 + "\n")

    def _update_final_stats(self):
        """Update final statistics."""
        if self.stats['successful'] > 0:
            confidences = [r.confidence for r in self.analysis_results if r.is_successful]
            self.stats['avg_confidence'] = sum(confidences) / len(confidences)

    def _find_file_in_directory(self, directory: Path, filename: str) -> Optional[Path]:
        """
        Find a file by name in directory (recursive search).

        Args:
            directory: Directory to search in
            filename: Filename to find

        Returns:
            Full path to file if found, None otherwise
        """
        directory = Path(directory)
        filename = Path(filename).name  # Just the filename part

        # Search recursively for the file
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.name == filename:
                return file_path

        return None
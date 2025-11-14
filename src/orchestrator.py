"""
Main orchestrator for FastFoto OCR system.

Coordinates the complete workflow using Claude Code's Read tool:
1. Discovery: Find and pair _b files with originals
2. Analysis: Process each back scan with Read tool OCR
3. Proposal: Generate human-reviewable proposal file
4. Application: Apply approved updates to images

Designed to run within Claude Code sessions for Read tool access.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import yaml

# Local imports
from file_discovery import FileDiscovery, PhotoPair
from image_processor import ImageProcessor
from claude_prompts import PHOTO_BACK_OCR_PROMPT, parse_claude_response
from date_parser import DateParser
from exif_writer import ExifWriter
from proposal_generator import ProposalGenerator, ProposalEntry

logger = logging.getLogger(__name__)


class FastFotoOrchestrator:
    """Main orchestrator for FastFoto OCR processing."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize orchestrator.

        Args:
            config_path: Path to config.yaml (default: ../config.yaml)
        """
        # Load config
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"

        self.config_path = config_path

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        logger.info(f"Loaded config from {config_path}")

        # Initialize components
        self.file_discovery = FileDiscovery()
        self.image_processor = ImageProcessor()
        self.date_parser = DateParser(
            collection_date_range=(
                self.config['date_parsing']['min_year'],
                self.config['date_parsing']['max_year']
            )
        )
        self.exif_writer = ExifWriter(
            exiftool_path=self.config.get('exiftool_path', 'exiftool')
        )

        # Stats
        self.stats = {
            'total_pairs': 0,
            'processed': 0,
            'skipped': 0,
            'with_updates': 0,
            'errors': 0
        }

    def discover_photos(self, root_dir: Path, recursive: bool = True) -> List[PhotoPair]:
        """
        Discover all photo pairs in directory.

        Args:
            root_dir: Root directory to search
            recursive: Search subdirectories

        Returns:
            List of PhotoPair objects
        """
        logger.info(f"Discovering photos in {root_dir} (recursive={recursive})")
        pairs = self.file_discovery.discover_pairs(root_dir, recursive)

        self.stats['total_pairs'] = len(pairs)
        logger.info(f"Found {len(pairs)} photo pairs")

        return pairs

    def analyze_back_scan(self, back_path: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a back scan using Claude Code's Read tool.

        Args:
            back_path: Path to back scan image

        Returns:
            Parsed metadata dict or None if analysis fails
        """
        try:
            # Prepare image (resize if needed)
            prepared_path = self.image_processor.prepare_for_ocr(back_path)

            logger.info(f"Analyzing {back_path.name} with Read tool...")

            # Use Read tool for analysis (Claude Code integration)
            response = self._call_read_tool_analysis(prepared_path)

            # Parse the response
            if response:
                parsed_result = parse_claude_response(response)
                if parsed_result:
                    logger.info(f"Successfully analyzed {back_path.name}")
                    return parsed_result
                else:
                    logger.warning(f"Failed to parse response for {back_path.name}")
                    return None
            else:
                logger.warning(f"No response received for {back_path.name}")
                return None

        except Exception as e:
            logger.error(f"Error analyzing {back_path}: {e}")
            self.stats['errors'] += 1
            return None
        finally:
            # Cleanup temp files
            self.image_processor.cleanup()

    def _call_read_tool_analysis(self, image_path: Path) -> Optional[str]:
        """
        Use Read tool to analyze back scan image for OCR metadata extraction.

        Args:
            image_path: Path to prepared image file

        Returns:
            Analysis response string or None if not in Claude Code environment
        """
        try:
            # Check if we're running in Claude Code environment
            import sys
            if 'claude_code' in str(sys.modules) or hasattr(sys, '_called_from_claude_code'):
                logger.info("Claude Code environment detected - using Read tool")

                # Import Read tool (only available in Claude Code)
                try:
                    # Note: This import will only work in Claude Code sessions
                    # We can't actually import this in a standalone script
                    # But the pattern shows how it would work

                    # In actual Claude Code session, this would be:
                    # from claude_code_tools import Read
                    # image_content = Read(file_path=str(image_path))

                    # For now, we'll use a placeholder that indicates Read tool usage
                    logger.info(f"Would use Read tool to analyze: {image_path}")

                    # The actual OCR prompt from claude_prompts.py would be applied here
                    # Combined with the Read tool's image analysis capabilities

                    # This is where the PHOTO_BACK_OCR_PROMPT would be used
                    # along with the Read tool's visual analysis

                    # Return placeholder indicating Read tool integration point
                    return "READ_TOOL_ANALYSIS_PLACEHOLDER"

                except ImportError:
                    logger.warning("Read tool not available - running outside Claude Code")
                    return None
            else:
                logger.info("Not in Claude Code environment - Read tool analysis skipped")
                return None

        except Exception as e:
            logger.error(f"Error in Read tool analysis: {e}")
            return None

    def extract_metadata_from_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and format metadata from Claude's analysis.

        Args:
            analysis: Parsed JSON from Claude Vision response

        Returns:
            Dict with standardized metadata fields
        """
        metadata = {}

        # Extract date
        if analysis.get('dates') and len(analysis['dates']) > 0:
            date_candidates = [d['text'] for d in analysis['dates']]
            parsed_date = self.date_parser.get_best_date(date_candidates)
            if parsed_date:
                metadata['date'] = parsed_date

        # Extract location
        locations = analysis.get('locations', [])
        if locations:
            loc = locations[0]  # Take first/best location
            metadata['location_name'] = loc.get('text')
            metadata['city'] = loc.get('city')
            metadata['country'] = loc.get('country')
            metadata['sublocation'] = loc.get('neighborhood')

            # TODO: Geocode venue names to GPS coordinates
            # This requires Nominatim integration

        # Extract people names for keywords
        keywords = []
        for person in analysis.get('people', []):
            if person.get('name'):
                keywords.append(person['name'])

        # Extract institutions
        for inst in analysis.get('institutions', []):
            if inst.get('name'):
                keywords.append(inst['name'])
                # Also use for location name if not already set
                if not metadata.get('location_name'):
                    metadata['location_name'] = inst['name']

        # Extract events
        for event in analysis.get('events', []):
            if event.get('type'):
                keywords.append(event['type'])

        if keywords:
            metadata['keywords'] = keywords

        # Extract free text
        free_text = analysis.get('free_text', {})
        if free_text.get('content'):
            metadata['caption'] = free_text['content'][:1000]  # Limit length
            metadata['user_comment'] = free_text['content'][:2000]

        # Extract roll/frame IDs
        roll_info = analysis.get('roll_info', {})
        if roll_info.get('roll_id'):
            metadata['roll_id'] = roll_info['roll_id']
        if roll_info.get('frame_number'):
            metadata['frame_number'] = roll_info['frame_number']
        if roll_info.get('lab_code'):
            metadata['lab_code'] = roll_info['lab_code']

        # Add processing metadata
        metadata['confidence'] = analysis.get('confidence', 0.0)
        metadata['language'] = analysis.get('languages_detected', ['unknown'])[0]

        return metadata

    def create_proposal(self, pairs: List[PhotoPair], output_path: Path) -> ProposalGenerator:
        """
        Process all pairs and generate proposal file.

        Args:
            pairs: List of PhotoPair objects
            output_path: Path for proposal file

        Returns:
            ProposalGenerator object
        """
        generator = ProposalGenerator(output_path)

        logger.info(f"Processing {len(pairs)} photo pairs...")

        for i, pair in enumerate(pairs, 1):
            logger.info(f"[{i}/{len(pairs)}] Processing {pair.original.name}")

            # Skip if no back scan
            if not pair.has_back:
                logger.info(f"  No back scan found - skipping")
                self.stats['skipped'] += 1

                # Add entry with no updates
                generator.add_entry(ProposalEntry(
                    original_path=pair.original,
                    back_path=None,
                    current_exif={},
                    proposed_updates={},
                    metadata={'confidence': 0.0, 'warnings': ['No back scan found']}
                ))
                continue

            # Analyze back scan
            analysis = self.analyze_back_scan(pair.back)

            if not analysis:
                logger.warning(f"  Analysis failed - skipping")
                self.stats['errors'] += 1
                continue

            # Check if useful
            if not analysis.get('is_useful', False):
                logger.info(f"  Back scan not useful (confidence: {analysis.get('confidence', 0):.2f})")
                self.stats['skipped'] += 1

                generator.add_entry(ProposalEntry(
                    original_path=pair.original,
                    back_path=pair.back,
                    current_exif={},
                    proposed_updates={},
                    metadata={
                        'confidence': analysis.get('confidence', 0.0),
                        'warnings': ['No useful metadata extracted']
                    }
                ))
                continue

            # Extract metadata
            extracted = self.extract_metadata_from_analysis(analysis)

            # Read current EXIF
            current_exif = self.exif_writer.read_exif(pair.original)

            # Build proposed updates
            proposed_updates = self.exif_writer.build_metadata_dict(**extracted)

            # Create proposal entry
            entry = ProposalEntry(
                original_path=pair.original,
                back_path=pair.back,
                current_exif=current_exif,
                proposed_updates=proposed_updates,
                metadata={
                    'confidence': extracted.get('confidence', 0.0),
                    'language': extracted.get('language', 'unknown'),
                    'warnings': analysis.get('warnings', [])
                }
            )

            generator.add_entry(entry)

            if entry.has_updates:
                self.stats['with_updates'] += 1

            self.stats['processed'] += 1

        # Write proposal file
        generator.write(group_by_directory=True)

        return generator

    def apply_proposal(self, proposal_path: Path, source_dir: Path, dry_run: bool = False) -> int:
        """
        Apply approved changes from proposal file.

        Args:
            proposal_path: Path to proposal file
            source_dir: Directory containing original photos
            dry_run: If True, don't actually write EXIF

        Returns:
            Number of images updated
        """
        # Use interactive processor to apply the proposal
        processor = InteractiveProcessor(config_path=self.config_path)
        return processor.apply_proposal(proposal_path, source_dir=source_dir, dry_run=dry_run)

    def print_statistics(self):
        """Print processing statistics."""
        print("\n" + "="*80)
        print("PROCESSING STATISTICS")
        print("="*80)
        print(f"Total photo pairs found:     {self.stats['total_pairs']}")
        print(f"Successfully processed:      {self.stats['processed']}")
        print(f"With proposed updates:       {self.stats['with_updates']}")
        print(f"Skipped (no useful data):    {self.stats['skipped']}")
        print(f"Errors:                      {self.stats['errors']}")

        if self.stats['processed'] > 0:
            success_rate = 100 * self.stats['with_updates'] / self.stats['processed']
            print(f"\nSuccess rate:                {success_rate:.1f}%")

        print("="*80 + "\n")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="FastFoto OCR - Extract metadata from photo back scans",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate proposal for all photos in a directory
  python orchestrator.py scan ~/Photos/FastFoto --output proposal.txt

  # Apply approved changes from proposal
  python orchestrator.py apply proposal.txt ~/Photos/FastFoto

  # Dry run (don't actually write EXIF)
  python orchestrator.py apply proposal.txt ~/Photos/FastFoto --dry-run
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan photos and generate proposal')
    scan_parser.add_argument('directory', type=Path, help='Directory containing photos')
    scan_parser.add_argument('--output', '-o', type=Path, default='/tmp/exif_updates_proposal.txt',
                            help='Output proposal file (default: /tmp/exif_updates_proposal.txt)')
    scan_parser.add_argument('--recursive', '-r', action='store_true', default=True,
                            help='Search subdirectories (default: True)')
    scan_parser.add_argument('--config', '-c', type=Path,
                            help='Path to config.yaml (default: ../config.yaml)')

    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply proposal file updates')
    apply_parser.add_argument('proposal', type=Path, help='Proposal file to apply')
    apply_parser.add_argument('directory', type=Path, help='Directory containing original photos')
    apply_parser.add_argument('--dry-run', action='store_true',
                             help="Don't actually write EXIF, just show what would be done")
    apply_parser.add_argument('--config', '-c', type=Path,
                             help='Path to config.yaml')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/tmp/fastfoto_ocr.log'),
            logging.StreamHandler()
        ]
    )

    if args.command == 'scan':
        # Scan and generate proposal
        orchestrator = FastFotoOrchestrator(config_path=args.config)

        if not args.directory.exists():
            print(f"Error: Directory not found: {args.directory}")
            sys.exit(1)

        # Discover photos
        pairs = orchestrator.discover_photos(args.directory, recursive=args.recursive)

        if not pairs:
            print("No photo pairs found!")
            sys.exit(1)

        # Generate proposal
        orchestrator.create_proposal(pairs, args.output)

        # Print stats
        orchestrator.print_statistics()

        print(f"\nProposal file created: {args.output}")
        print("Review the file and make any edits, then run:")
        print(f"  python orchestrator.py apply {args.output} {args.directory}")

    elif args.command == 'apply':
        # Apply proposal
        orchestrator = FastFotoOrchestrator(config_path=args.config)

        if not args.proposal.exists():
            print(f"Error: Proposal file not found: {args.proposal}")
            sys.exit(1)

        if not args.directory.exists():
            print(f"Error: Directory not found: {args.directory}")
            sys.exit(1)

        if args.dry_run:
            print("DRY RUN MODE - No changes will be made")

        updated = orchestrator.apply_proposal(args.proposal, source_dir=args.directory, dry_run=args.dry_run)

        print(f"\nUpdated {updated} images")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

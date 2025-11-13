"""
Generates human-readable proposal files for EXIF updates.

Shows before/after comparison for user review before applying changes.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProposalEntry:
    """Represents a proposed EXIF update for one image."""

    def __init__(self, original_path: Path, back_path: Optional[Path],
                 current_exif: Dict[str, Any], proposed_updates: Dict[str, Any],
                 metadata: Dict[str, Any]):
        """
        Initialize proposal entry.

        Args:
            original_path: Path to original image
            back_path: Path to back scan (or None)
            current_exif: Current EXIF data
            proposed_updates: Proposed EXIF updates
            metadata: Extraction metadata (confidence, warnings, etc.)
        """
        self.original_path = original_path
        self.back_path = back_path
        self.current_exif = current_exif
        self.proposed_updates = proposed_updates
        self.metadata = metadata

    @property
    def has_updates(self) -> bool:
        """Check if there are any proposed updates."""
        return len(self.proposed_updates) > 0

    @property
    def confidence(self) -> float:
        """Get overall confidence score."""
        return self.metadata.get('confidence', 0.0)

    @property
    def warnings(self) -> List[str]:
        """Get list of warnings."""
        return self.metadata.get('warnings', [])


class ProposalGenerator:
    """Generates proposal files for EXIF updates."""

    def __init__(self, output_path: Path):
        """
        Initialize proposal generator.

        Args:
            output_path: Path to output proposal file
        """
        self.output_path = Path(output_path)
        self.entries: List[ProposalEntry] = []

    def add_entry(self, entry: ProposalEntry):
        """
        Add a proposal entry with validation.

        Args:
            entry: ProposalEntry object
        """
        # Validate filename doesn't contain incorrect patterns
        original_name = entry.original_path.name if entry.original_path else ""

        # Catch common filename bugs - ANY back scan suffix
        if (original_name.endswith('_a.jpg') or original_name.endswith('_a.jpeg') or
            original_name.endswith('_b.jpg') or original_name.endswith('_b.jpeg')):
            raise ValueError(
                f"BUG DETECTED: Proposal references back scan filename '{original_name}' "
                f"instead of front image. Remove back scan suffix (_a/_b) for front image filename."
            )

        # Log entry for debugging
        logger.debug(f"Adding proposal entry: {original_name}")

        self.entries.append(entry)

    def generate_header(self) -> str:
        """Generate proposal file header."""
        total = len(self.entries)
        with_updates = sum(1 for e in self.entries if e.has_updates)
        without_updates = total - with_updates

        # Calculate statistics
        avg_confidence = sum(e.confidence for e in self.entries) / total if total > 0 else 0
        high_conf = sum(1 for e in self.entries if e.confidence >= 0.8)
        med_conf = sum(1 for e in self.entries if 0.6 <= e.confidence < 0.8)
        low_conf = sum(1 for e in self.entries if e.confidence < 0.6)

        header = f"""{'='*80}
FastFoto OCR - EXIF Update Proposal
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

SUMMARY:
  Total files analyzed: {total}
  Files with proposed updates: {with_updates} ({100*with_updates/total:.1f}%)
  Files without updates: {without_updates}

CONFIDENCE DISTRIBUTION:
  High (≥0.8): {high_conf} files
  Medium (0.6-0.8): {med_conf} files
  Low (<0.6): {low_conf} files
  Average confidence: {avg_confidence:.2f}

INSTRUCTIONS:
  1. Review each proposed update below
  2. Check for accuracy of extracted dates, locations, and text
  3. To skip an update, add "SKIP:" at the start of that section
  4. To modify a value, edit it directly in this file
  5. Save and run with: fastfoto-ocr apply --proposal {self.output_path.name}

{'='*80}

"""
        return header

    def format_entry(self, index: int, entry: ProposalEntry) -> str:
        """
        Format a single proposal entry.

        Args:
            index: Entry number (1-based)
            entry: ProposalEntry object

        Returns:
            Formatted entry string
        """
        output = []

        # Header
        output.append(f"\n[{index:04d}] {entry.original_path.name}")

        if entry.back_path:
            output.append(f"  Back scan: {entry.back_path.name}")
        else:
            output.append("  No back scan found - skipped")
            return "\n".join(output) + "\n"

        output.append(f"  Confidence: {entry.confidence:.2f}")

        if not entry.has_updates:
            output.append("  Status: No useful metadata extracted")
            return "\n".join(output) + "\n"

        # Current EXIF values
        output.append("\n  CURRENT EXIF:")
        key_fields = [
            "DateTimeOriginal", "GPSLatitude", "GPSLongitude",
            "LocationCreatedCity", "LocationCreatedCountryName",
            "Caption-Abstract", "Keywords", "ImageUniqueID"
        ]

        for field in key_fields:
            current_val = entry.current_exif.get(field, "<not set>")
            if current_val and current_val != "<not set>":
                # Truncate long values
                if isinstance(current_val, str) and len(current_val) > 60:
                    current_val = current_val[:57] + "..."
                output.append(f"    {field}: {current_val}")

        # Proposed updates
        output.append("\n  PROPOSED UPDATES:")
        for field, value in sorted(entry.proposed_updates.items()):
            # Format value
            if isinstance(value, list):
                value_str = ", ".join(str(v) for v in value[:5])  # Limit to first 5
                if len(value) > 5:
                    value_str += f" ... (+{len(value)-5} more)"
            elif isinstance(value, str) and len(value) > 60:
                value_str = value[:57] + "..."
            else:
                value_str = str(value)

            output.append(f"    {field}: {value_str}")

        # Warnings
        if entry.warnings:
            output.append("\n  WARNINGS:")
            for warning in entry.warnings:
                output.append(f"    ⚠ {warning}")

        # Metadata
        output.append("\n  EXTRACTION METADATA:")
        if 'source' in entry.metadata:
            output.append(f"    Source: {entry.metadata['source']}")
        if 'language' in entry.metadata:
            output.append(f"    Language: {entry.metadata['language']}")
        if 'zones_found' in entry.metadata:
            zones = ", ".join(entry.metadata['zones_found'])
            output.append(f"    Zones with data: {zones}")

        output.append("")  # Blank line between entries
        return "\n".join(output)

    def generate_directory_summary(self, directory: Path, entries: List[ProposalEntry]) -> str:
        """
        Generate summary for a directory.

        Args:
            directory: Directory path
            entries: Entries in this directory

        Returns:
            Summary string
        """
        total = len(entries)
        with_updates = sum(1 for e in entries if e.has_updates)
        avg_conf = sum(e.confidence for e in entries) / total if total > 0 else 0

        summary = f"""
{'-'*80}
Directory: {directory}
  Files: {total} | With updates: {with_updates} | Average confidence: {avg_conf:.2f}
{'-'*80}
"""
        return summary

    def write(self, group_by_directory: bool = True):
        """
        Write proposal file.

        Args:
            group_by_directory: Group entries by directory
        """
        logger.info(f"Generating proposal file: {self.output_path}")

        with open(self.output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(self.generate_header())

            if group_by_directory:
                # Group entries by directory
                by_directory: Dict[Path, List[ProposalEntry]] = {}
                for entry in self.entries:
                    dir_path = entry.original_path.parent
                    if dir_path not in by_directory:
                        by_directory[dir_path] = []
                    by_directory[dir_path].append(entry)

                # Write each directory
                global_index = 1
                for directory in sorted(by_directory.keys()):
                    entries = by_directory[directory]

                    # Directory summary
                    f.write(self.generate_directory_summary(directory, entries))

                    # Entries
                    for entry in entries:
                        f.write(self.format_entry(global_index, entry))
                        global_index += 1

            else:
                # Write all entries sequentially
                for i, entry in enumerate(self.entries, 1):
                    f.write(self.format_entry(i, entry))

            # Footer
            f.write(f"\n{'='*80}\n")
            f.write("END OF PROPOSAL\n")
            f.write(f"{'='*80}\n")

        logger.info(f"Proposal file written: {self.output_path}")
        logger.info(f"  Total entries: {len(self.entries)}")
        logger.info(f"  With updates: {sum(1 for e in self.entries if e.has_updates)}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about proposals.

        Returns:
            Dict with statistics
        """
        total = len(self.entries)
        if total == 0:
            return {'total': 0}

        with_updates = sum(1 for e in self.entries if e.has_updates)

        # Count by field
        field_counts: Dict[str, int] = {}
        for entry in self.entries:
            for field in entry.proposed_updates.keys():
                field_counts[field] = field_counts.get(field, 0) + 1

        return {
            'total': total,
            'with_updates': with_updates,
            'without_updates': total - with_updates,
            'update_rate': with_updates / total if total > 0 else 0,
            'avg_confidence': sum(e.confidence for e in self.entries) / total,
            'field_counts': field_counts,
            'most_common_fields': sorted(field_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }


if __name__ == "__main__":
    # Test/demo
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        output_path = Path(sys.argv[1])
    else:
        output_path = Path("/tmp/test_proposal.txt")

    generator = ProposalGenerator(output_path)

    # Create a test entry
    test_entry = ProposalEntry(
        original_path=Path("/test/IMG_001.jpg"),
        back_path=Path("/test/IMG_001_b.jpg"),
        current_exif={
            "DateTimeOriginal": "2020:01:01 00:00:00",
        },
        proposed_updates={
            "DateTimeOriginal": "1999:06:07 11:32:00",
            "GPSLatitude": "52, 5, 30.0",
            "GPSLatitudeRef": "N",
            "LocationCreatedCity": "Utrecht",
            "Caption-Abstract": "Summer vacation"
        },
        metadata={
            'confidence': 0.92,
            'source': 'Zone 1 (bottom edge) + Zone 4 (handwritten)',
            'language': 'en',
            'zones_found': ['zone_1_bottom_edge', 'zone_4_handwritten'],
            'warnings': ['Filename suggests 2001, OCR date is 1999']
        }
    )

    generator.add_entry(test_entry)
    generator.write()

    print(f"\nProposal file created: {output_path}")
    print("\nStatistics:")
    stats = generator.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

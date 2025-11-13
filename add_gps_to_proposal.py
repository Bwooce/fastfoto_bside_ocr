#!/usr/bin/env python3
"""
Add GPS coordinates to existing EXIF proposal file.

Reads the proposal file, adds GPS coordinates for any locations that can be geocoded,
and writes an updated proposal file with GPS EXIF fields included.
"""

import re
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_geocoder import SimpleGeocoder
from exif_writer import ExifWriter


class ProposalGPSUpdater:
    """Updates proposal file with GPS coordinates."""

    def __init__(self):
        self.geocoder = SimpleGeocoder()
        self.exif_writer = ExifWriter()
        self.stats = {
            'total_entries': 0,
            'locations_found': 0,
            'gps_added': 0,
            'locations_geocoded': []
        }

    def extract_location_from_entry(self, entry_text: str) -> dict:
        """
        Extract location information from a proposal entry.

        Args:
            entry_text: Text of one proposal entry

        Returns:
            Dict with location components
        """
        location_data = {}

        # Extract location fields using regex
        patterns = {
            'city': r'LocationCreatedCity:\s*(.+)',
            'country': r'LocationCreatedCountryName:\s*(.+)',
            'sublocation': r'LocationCreatedSublocation:\s*(.+)',
            'province': r'LocationCreatedProvinceState:\s*(.+)'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, entry_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if value and value != "Unknown":
                    location_data[key] = value

        return location_data

    def add_gps_to_entry(self, entry_text: str) -> str:
        """
        Add GPS coordinates to a single proposal entry.

        Args:
            entry_text: Text of one proposal entry

        Returns:
            Updated entry text with GPS coordinates added
        """
        # Extract location data
        location_data = self.extract_location_from_entry(entry_text)

        if not location_data:
            return entry_text

        self.stats['locations_found'] += 1

        # Try to geocode
        coords = self.geocoder.geocode_from_metadata(location_data)

        if not coords:
            return entry_text

        latitude, longitude = coords
        self.stats['gps_added'] += 1

        # Create location description for stats
        if 'city' in location_data and 'country' in location_data:
            location_desc = f"{location_data['city']}, {location_data['country']}"
        elif 'city' in location_data:
            location_desc = location_data['city']
        elif 'country' in location_data:
            location_desc = location_data['country']
        else:
            location_desc = str(location_data)

        self.stats['locations_geocoded'].append(f"{location_desc} → {latitude:.4f}, {longitude:.4f}")

        # Format GPS coordinates for EXIF
        lat_data = self.exif_writer.format_gps_latitude(latitude)
        lon_data = self.exif_writer.format_gps_longitude(longitude)

        # Find the PROPOSED UPDATES section
        proposed_start = entry_text.find("PROPOSED UPDATES:")
        if proposed_start == -1:
            return entry_text

        # Find the end of proposed updates (before EXTRACTION METADATA)
        proposed_end = entry_text.find("EXTRACTION METADATA:", proposed_start)
        if proposed_end == -1:
            proposed_end = len(entry_text)

        # Extract the proposed updates section
        before_proposed = entry_text[:proposed_start]
        proposed_section = entry_text[proposed_start:proposed_end]
        after_proposed = entry_text[proposed_end:]

        # Add GPS fields to proposed updates
        gps_lines = []
        for field, value in {**lat_data, **lon_data}.items():
            gps_lines.append(f"    {field}: {value}")

        # Insert GPS coordinates after existing fields
        gps_text = "\n" + "\n".join(gps_lines)

        # Combine everything
        updated_entry = before_proposed + proposed_section + gps_text + "\n" + after_proposed

        return updated_entry

    def update_proposal_file(self, input_path: Path, output_path: Path = None):
        """
        Update proposal file with GPS coordinates.

        Args:
            input_path: Path to input proposal file
            output_path: Path for output (default: input_path with _with_gps suffix)
        """
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_with_gps{input_path.suffix}"

        print(f"📖 Reading proposal file: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into entries by [NNNN] markers
        entry_pattern = r'(\[0\d{3}\].*?)(?=\[0\d{3}\]|$)'
        entries = re.findall(entry_pattern, content, re.DOTALL)

        print(f"📊 Found {len(entries)} entries to process")

        # Update each entry
        updated_entries = []
        for i, entry in enumerate(entries):
            self.stats['total_entries'] += 1
            updated_entry = self.add_gps_to_entry(entry)
            updated_entries.append(updated_entry)

            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(entries)} entries...")

        # Reconstruct file with header
        header_end = content.find('[0001]')
        if header_end != -1:
            header = content[:header_end]
        else:
            header = content[:1000]  # Fallback

        # Combine updated content
        updated_content = header + ''.join(updated_entries)

        # Write output file
        print(f"💾 Writing updated proposal: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        # Print statistics
        print(f"\n📊 GPS Addition Statistics:")
        print(f"  Total entries processed: {self.stats['total_entries']}")
        print(f"  Entries with locations: {self.stats['locations_found']}")
        print(f"  GPS coordinates added: {self.stats['gps_added']}")
        print(f"  Success rate: {(self.stats['gps_added'] / self.stats['locations_found'] * 100):.1f}%")

        if self.stats['locations_geocoded']:
            print(f"\n🗺️  Locations geocoded:")
            for location in self.stats['locations_geocoded'][:10]:  # Show first 10
                print(f"    {location}")
            if len(self.stats['locations_geocoded']) > 10:
                print(f"    ... +{len(self.stats['locations_geocoded']) - 10} more")

        print(f"\n✅ Updated proposal file created: {output_path}")


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python add_gps_to_proposal.py <proposal_file>")
        print("Example: python add_gps_to_proposal.py exif_updates_proposal.txt")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    updater = ProposalGPSUpdater()
    updater.update_proposal_file(input_file)


if __name__ == "__main__":
    main()
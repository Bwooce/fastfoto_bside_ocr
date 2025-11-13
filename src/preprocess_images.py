#!/usr/bin/env python3
"""
Preprocessing script for FastFoto back scans.

Prepares images for Claude Code's Read tool by:
- Resizing images >3.5MB or >2000px to 1800px @ 85% quality
- Converting TIFF to JPEG
- Maintaining directory structure
- Creating mapping file for original → prepared paths

Run this BEFORE starting your Claude Code interactive session.
"""

import sys
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import argparse

# Try to import tqdm for progress bars
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Note: Install tqdm for progress bars (pip install tqdm)")

# Local imports
from file_discovery import FileDiscovery, PhotoPair
from image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class PreprocessingStats:
    """Track preprocessing statistics."""

    def __init__(self):
        self.total_files = 0
        self.resized = 0
        self.converted_tiff = 0
        self.copied = 0
        self.errors = 0
        self.total_size_before = 0
        self.total_size_after = 0

    def print_summary(self):
        """Print summary statistics."""
        print("\n" + "="*80)
        print("PREPROCESSING SUMMARY")
        print("="*80)
        print(f"Total back scans found:      {self.total_files}")
        print(f"Resized (too large):         {self.resized}")
        print(f"Converted (TIFF→JPEG):       {self.converted_tiff}")
        print(f"Copied as-is:                {self.copied}")
        print(f"Errors:                      {self.errors}")

        if self.total_size_before > 0:
            size_before_mb = self.total_size_before / (1024 * 1024)
            size_after_mb = self.total_size_after / (1024 * 1024)
            reduction_pct = 100 * (1 - size_after_mb / size_before_mb) if size_before_mb > 0 else 0

            print(f"\nTotal size before:           {size_before_mb:.1f} MB")
            print(f"Total size after:            {size_after_mb:.1f} MB")
            print(f"Size reduction:              {reduction_pct:.1f}%")

        print("="*80 + "\n")


def preprocess_images(
    source_dir: Path,
    output_dir: Path,
    recursive: bool = True,
    preserve_structure: bool = True
) -> Tuple[Dict[str, str], PreprocessingStats]:
    """
    Preprocess all FastFoto back scans for Read tool.

    Args:
        source_dir: Source directory containing photos
        output_dir: Output directory for prepared images
        recursive: Search subdirectories
        preserve_structure: Maintain directory structure in output

    Returns:
        Tuple of (mapping dict, statistics)
        Mapping: {original_path: prepared_path}
    """
    # Initialize components
    discovery = FileDiscovery()
    processor = ImageProcessor()
    stats = PreprocessingStats()
    mapping = {}

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover photo pairs
    print(f"Discovering photos in {source_dir} (recursive={recursive})...")
    pairs = discovery.discover_pairs(source_dir, recursive)

    back_scans = [pair for pair in pairs if pair.has_back_scan]
    stats.total_files = len(back_scans)

    if stats.total_files == 0:
        print("No back scans found!")
        return mapping, stats

    print(f"Found {stats.total_files} back scans to preprocess\n")

    # Process each back scan
    iterator = tqdm(back_scans, desc="Processing") if HAS_TQDM else back_scans

    for pair in iterator:
        try:
            back_scan = pair.back_scan

            # Calculate relative path for output
            if preserve_structure:
                rel_path = back_scan.relative_to(source_dir)
                output_path = output_dir / rel_path
            else:
                output_path = output_dir / back_scan.name

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Track original size
            original_size = back_scan.stat().st_size
            stats.total_size_before += original_size

            # Check if preprocessing needed
            needs_processing = processor._needs_processing(back_scan)

            if needs_processing:
                # Preprocess (resize/convert)
                prepared_path = processor.prepare_for_ocr(back_scan)

                # Copy to output with JPEG extension if converted
                if back_scan.suffix.lower() in ['.tif', '.tiff']:
                    output_path = output_path.with_suffix('.jpg')
                    stats.converted_tiff += 1

                if prepared_path != back_scan:
                    # Was resized or converted
                    shutil.copy2(prepared_path, output_path)
                    stats.resized += 1

                    # Clean up temp file if created
                    if prepared_path.parent == Path(processor.temp_dir):
                        prepared_path.unlink()
                else:
                    # Just copy
                    shutil.copy2(back_scan, output_path)
            else:
                # Copy as-is
                shutil.copy2(back_scan, output_path)
                stats.copied += 1

            # Track output size
            output_size = output_path.stat().st_size
            stats.total_size_after += output_size

            # Add to mapping
            mapping[str(pair.original.resolve())] = str(output_path.resolve())

            if not HAS_TQDM:
                print(f"✓ {back_scan.name}")

        except Exception as e:
            logger.error(f"Error processing {pair.back_scan}: {e}")
            stats.errors += 1
            if not HAS_TQDM:
                print(f"✗ {back_scan.name}: {e}")
            continue

    return mapping, stats


def save_mapping(mapping: Dict[str, str], output_dir: Path):
    """
    Save mapping file to JSON.

    Args:
        mapping: Dictionary of original → prepared paths
        output_dir: Output directory
    """
    mapping_file = output_dir / "preprocessing_mapping.json"

    mapping_data = {
        'created': datetime.now().isoformat(),
        'total_files': len(mapping),
        'mapping': mapping
    }

    with open(mapping_file, 'w') as f:
        json.dump(mapping_data, f, indent=2)

    print(f"Mapping saved to: {mapping_file}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Preprocess FastFoto back scans for Claude Code Read tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preprocess all photos in a directory
  python preprocess_images.py ~/Photos/FastFoto --output /tmp/fastfoto_prepared

  # Non-recursive (current directory only)
  python preprocess_images.py ~/Photos/FastFoto --output /tmp/prepared --no-recursive

  # Flatten directory structure
  python preprocess_images.py ~/Photos/FastFoto --output /tmp/prepared --no-preserve-structure
        """
    )

    parser.add_argument(
        'source_dir',
        type=Path,
        help='Source directory containing FastFoto photos'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        required=True,
        help='Output directory for prepared images'
    )

    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='Do not search subdirectories'
    )

    parser.add_argument(
        '--no-preserve-structure',
        action='store_true',
        help='Flatten directory structure (put all files in output root)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Validate source directory
    if not args.source_dir.exists():
        print(f"Error: Source directory not found: {args.source_dir}")
        sys.exit(1)

    if not args.source_dir.is_dir():
        print(f"Error: Source path is not a directory: {args.source_dir}")
        sys.exit(1)

    # Confirm if output directory exists and is not empty
    if args.output.exists() and any(args.output.iterdir()):
        response = input(f"Output directory {args.output} already exists and is not empty. Continue? [y/N] ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    print("\n" + "="*80)
    print("FastFoto Back Scan Preprocessor")
    print("="*80)
    print(f"Source:      {args.source_dir}")
    print(f"Output:      {args.output}")
    print(f"Recursive:   {not args.no_recursive}")
    print(f"Structure:   {'Preserved' if not args.no_preserve_structure else 'Flattened'}")
    print("="*80 + "\n")

    # Run preprocessing
    mapping, stats = preprocess_images(
        source_dir=args.source_dir,
        output_dir=args.output,
        recursive=not args.no_recursive,
        preserve_structure=not args.no_preserve_structure
    )

    # Save mapping file
    if mapping:
        save_mapping(mapping, args.output)

    # Print summary
    stats.print_summary()

    # Next steps
    if stats.errors == 0:
        print("✓ Preprocessing complete! Next steps:")
        print(f"  1. Review prepared images in: {args.output}")
        print(f"  2. Start Claude Code session and say:")
        print(f'     "Analyze the prepared FastFoto images in {args.output}"')
    else:
        print(f"⚠ Completed with {stats.errors} errors. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

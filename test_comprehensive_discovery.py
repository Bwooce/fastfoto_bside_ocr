#!/usr/bin/env python3
"""
Test script to demonstrate comprehensive back scan file discovery.

This script shows how the enhanced FileDiscovery class now detects
multiple naming patterns to avoid missing back scan files.

Usage:
    python test_comprehensive_discovery.py /path/to/photos
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from file_discovery import FileDiscovery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_comprehensive_discovery(photo_dir: Path):
    """Test comprehensive file discovery on a directory."""

    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE BACK SCAN DISCOVERY TEST")
    print(f"{'='*80}")
    print(f"Directory: {photo_dir}")
    print(f"{'='*80}\n")

    discovery = FileDiscovery()

    # Step 1: Analyze naming patterns
    print("🔍 STEP 1: Analyzing naming patterns...")
    patterns = discovery.analyze_naming_patterns(photo_dir)

    print(f"\n📊 PATTERN ANALYSIS RESULTS:")
    print(f"  Total image files found: {patterns['total_files']}")
    print(f"  Back scans identified: {patterns['back_scans']['total_back_scans']}")
    print(f"  Main photos: {len(patterns['main_photos'])}")
    print(f"  Coverage: {patterns['back_scan_percentage']:.1f}%")

    # Show patterns found
    print(f"\n📋 DETECTED PATTERNS:")
    for pattern_name, files in patterns['back_scans'].items():
        if isinstance(files, list) and files:
            print(f"  {pattern_name}: {len(files)} files")
            # Show first 3 examples
            examples = [f.name for f in files[:3]]
            if len(files) > 3:
                examples.append(f"... +{len(files)-3} more")
            print(f"    Examples: {examples}")

    # Show unrecognized patterns that might be missed
    if patterns['unrecognized_patterns']:
        print(f"\n⚠️  UNRECOGNIZED PATTERNS ({len(patterns['unrecognized_patterns'])} files):")
        print("  These files might be back scans with unusual naming:")
        for file_path in patterns['unrecognized_patterns'][:10]:  # Show first 10
            print(f"    {file_path.name}")
        if len(patterns['unrecognized_patterns']) > 10:
            print(f"    ... +{len(patterns['unrecognized_patterns'])-10} more")

    # Warn if coverage seems low
    if patterns['back_scan_percentage'] < 40:
        print(f"\n🚨 WARNING: Low back scan coverage ({patterns['back_scan_percentage']:.1f}%)")
        print("   Expected ~50% for typical FastFoto collections.")
        print("   Possible reasons:")
        print("   - Unusual naming patterns not detected")
        print("   - Mixed collection with non-FastFoto images")
        print("   - Check 'unrecognized_patterns' above for missed files")

    # Step 2: Traditional pair discovery
    print(f"\n🔗 STEP 2: Discovering photo pairs...")
    pairs = discovery.discover_pairs(photo_dir)

    with_backs = sum(1 for p in pairs if p.has_back)
    print(f"  Photo pairs created: {len(pairs)}")
    print(f"  Pairs with back scans: {with_backs}")
    print(f"  Pairs without back scans: {len(pairs) - with_backs}")

    # Verification
    print(f"\n✅ VERIFICATION:")
    if patterns['back_scans']['total_back_scans'] == with_backs:
        print(f"  ✅ Pattern analysis matches pair discovery ({with_backs} back scans)")
    else:
        print(f"  ⚠️  Mismatch detected!")
        print(f"     Pattern analysis found: {patterns['back_scans']['total_back_scans']}")
        print(f"     Pair discovery found: {with_backs}")

    print(f"\n{'='*80}")
    print(f"DISCOVERY TEST COMPLETE")
    print(f"{'='*80}\n")

    return patterns, pairs


def main():
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python test_comprehensive_discovery.py /path/to/photos")
        print()
        print("This script tests comprehensive back scan file discovery.")
        print("It will analyze naming patterns and verify complete coverage.")
        sys.exit(1)

    photo_dir = Path(sys.argv[1])

    if not photo_dir.exists():
        print(f"Error: Directory not found: {photo_dir}")
        sys.exit(1)

    if not photo_dir.is_dir():
        print(f"Error: Not a directory: {photo_dir}")
        sys.exit(1)

    try:
        patterns, pairs = test_comprehensive_discovery(photo_dir)

        # Summary
        print("🎯 SUMMARY:")
        print(f"  Use this enhanced FileDiscovery class to avoid missing files!")
        print(f"  Always run pattern analysis before processing.")
        print(f"  Verify coverage is around 50% for FastFoto collections.")

        if patterns['back_scan_percentage'] >= 40:
            print(f"  ✅ Discovery looks complete ({patterns['back_scan_percentage']:.1f}% coverage)")
        else:
            print(f"  ⚠️  Discovery may be incomplete ({patterns['back_scan_percentage']:.1f}% coverage)")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
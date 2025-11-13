#!/usr/bin/env python3
"""
Fix incorrect filenames in EXIF proposal file.

The proposal file incorrectly references back scan filenames (with _a suffix)
instead of the actual front image filenames that need EXIF updates.

Example fix:
- WRONG: [0001] FastFoto_0522_a.jpg
- CORRECT: [0001] FastFoto_0522.jpg
"""

import re
import sys
from pathlib import Path


def fix_proposal_filenames(input_file: Path, output_file: Path = None):
    """
    Fix incorrect filenames in proposal file.

    Args:
        input_file: Path to proposal file with wrong filenames
        output_file: Path for corrected file (default: adds _fixed suffix)
    """
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_fixed{input_file.suffix}"

    print(f"📖 Reading proposal file: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Track changes for reporting
    changes_made = []

    # Pattern 1: Fix entry headers [NNNN] FastFoto_XXXX_a.jpg -> [NNNN] FastFoto_XXXX.jpg
    def fix_entry_header(match):
        entry_num = match.group(1)
        filename = match.group(2)

        if filename.endswith('_a.jpg'):
            # Remove the _a suffix
            fixed_filename = filename.replace('_a.jpg', '.jpg')
            changes_made.append(f"Entry {entry_num}: {filename} → {fixed_filename}")
            return f"[{entry_num}] {fixed_filename}"

        return match.group(0)  # No change needed

    # Apply header fixes
    content = re.sub(r'\[(\d{4})\] (.+?_a\.jpg)', fix_entry_header, content)

    # Pattern 2: Fix any other references to FastFoto files with _a suffix
    def fix_fastfoto_reference(match):
        prefix = match.group(1)
        filename = match.group(2)
        suffix = match.group(3)

        if '_a.jpg' in filename:
            fixed_filename = filename.replace('_a.jpg', '.jpg')
            changes_made.append(f"Reference: {filename} → {fixed_filename}")
            return f"{prefix}{fixed_filename}{suffix}"

        return match.group(0)

    # Apply reference fixes (be careful not to change back scan references)
    # Only fix front image references, not back scan references
    content = re.sub(r'(\s+Original path:\s*)(FastFoto_\d+.*?\.jpg)(\s*)', fix_fastfoto_reference, content)

    # Pattern 3: Fix any path references that shouldn't have _a
    # But preserve actual back scan references (with _b)
    before_fixes = len(changes_made)

    # Count unique changes
    unique_changes = list(set(changes_made))

    print(f"💾 Writing corrected proposal: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    # Report results
    print(f"\n📊 Filename Fix Results:")
    print(f"  Total corrections made: {len(unique_changes)}")

    if unique_changes:
        print(f"\n🔧 Files corrected:")
        for change in unique_changes[:10]:  # Show first 10
            print(f"    {change}")

        if len(unique_changes) > 10:
            print(f"    ... +{len(unique_changes) - 10} more corrections")

    print(f"\n✅ Corrected proposal file: {output_file}")

    # Verify no _a.jpg references remain in entry headers
    with open(output_file, 'r', encoding='utf-8') as f:
        verification_content = f.read()

    remaining_issues = re.findall(r'\[\d{4}\] \S*_a\.jpg', verification_content)

    if remaining_issues:
        print(f"\n⚠️  WARNING: {len(remaining_issues)} entries still have _a.jpg in headers:")
        for issue in remaining_issues[:5]:
            print(f"    {issue}")
    else:
        print(f"\n✅ VERIFICATION PASSED: No _a.jpg references in entry headers")

    return output_file


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python fix_proposal_filenames.py <proposal_file>")
        print("Example: python fix_proposal_filenames.py exif_updates_proposal_with_gps.txt")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    fixed_file = fix_proposal_filenames(input_file)

    print(f"\n🎯 Next step: Use the corrected file for EXIF updates:")
    print(f"python src/interactive_processor.py apply --proposal {fixed_file.name}")


if __name__ == "__main__":
    main()
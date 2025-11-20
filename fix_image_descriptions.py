#!/usr/bin/env python3
"""
  Enhanced Image Metadata Fix Script
  1. Copies verbatim text from UserComment to ImageDescription for photo viewer compatibility
  2. Fixes keyword separators from semicolons to commas for Apple Photos compatibility

  Usage: python3 fix_image_descriptions.py [photo_directory]
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def get_exif_field(photo_path, field):
    """Get a specific EXIF field value using exiftool"""
    try:
        cmd = ["exiftool", f"-{field}", "-s3", photo_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip() if result.stdout.strip() else None
        return None
    except Exception:
        return None


def set_exif_field(photo_path, field, value):
    """Set a specific EXIF field value using exiftool"""
    try:
        cmd = ["exiftool", "-overwrite_original", f"-{field}={value}", photo_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False


def extract_verbatim_text(usercomment):
    """Extract verbatim text from UserComment field"""
    if not usercomment:
        return None

    # Remove language prefixes like "Spanish handwritten text: "
    verbatim_match = re.search(r"^[A-Za-z]+ handwritten text: (.+)$", usercomment)
    if verbatim_match:
        return verbatim_match.group(1).strip()

    # If no language prefix, check if it starts with "handwritten text:"
    simple_match = re.search(r"^handwritten text: (.+)$", usercomment, re.IGNORECASE)
    if simple_match:
        return simple_match.group(1).strip()

    # If UserComment appears to be verbatim text itself, return as-is
    # Skip if it looks like metadata or technical descriptions
    if not any(
        word in usercomment.lower()
        for word in ["machine-printed", "text:", "analysis", "processed"]
    ):
        return usercomment.strip()

    return None


def fix_keyword_separators(keywords):
    """Convert semicolon-separated keywords to comma-separated for Apple Photos compatibility"""
    if not keywords or ";" not in keywords:
        return keywords

    # Replace semicolons with comma-space for proper Apple Photos format
    return keywords.replace(";", ", ")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 fix_image_descriptions.py [photo_directory]")
        print(
            "Example: python3 fix_image_descriptions.py /Users/bruce/Pictures/MyPhotos"
        )
        return 1

    photo_dir = sys.argv[1]
    if not os.path.exists(photo_dir):
        print(f"Error: Directory not found: {photo_dir}")
        return 1

    print("Enhanced Image Metadata Fix Script")
    print(f"Processing directory: {photo_dir}")
    print()
    print("This script will:")
    print("1. Find all JPEG files in the directory")
    print("2. Fix ImageDescription: Copy verbatim text from UserComment")
    print("3. Fix Keywords: Convert semicolon separators to commas")
    print("4. Skip files that already have correct metadata")
    print()

    # Find all JPEG files
    jpeg_files = []
    for ext in ["*.jpg", "*.JPG", "*.jpeg", "*.JPEG"]:
        jpeg_files.extend(Path(photo_dir).glob(ext))

    if not jpeg_files:
        print("No JPEG files found in the directory.")
        return 0

    print(f"Found {len(jpeg_files)} JPEG files to process...")
    print()

    description_success = 0
    description_skip = 0
    keywords_success = 0
    keywords_skip = 0
    error_count = 0

    for i, photo_path in enumerate(jpeg_files, 1):
        photo_name = os.path.basename(photo_path)
        print(f"[{i:3d}/{len(jpeg_files)}] Processing: {photo_name}")

        changes_made = False

        # Fix ImageDescription field
        usercomment = get_exif_field(str(photo_path), "UserComment")
        current_description = get_exif_field(str(photo_path), "ImageDescription")

        if usercomment:
            verbatim_text = extract_verbatim_text(usercomment)
            if verbatim_text and (
                not current_description
                or current_description.strip() != verbatim_text.strip()
            ):
                if set_exif_field(str(photo_path), "ImageDescription", verbatim_text):
                    print(f"  -> Fixed ImageDescription: Set to verbatim text")
                    description_success += 1
                    changes_made = True
                else:
                    print(f"  -> Error: Failed to update ImageDescription")
                    error_count += 1
            else:
                description_skip += 1
        else:
            description_skip += 1

        # Fix keyword separators
        current_keywords = get_exif_field(str(photo_path), "IPTC:Keywords")
        if current_keywords and ";" in current_keywords:
            fixed_keywords = fix_keyword_separators(current_keywords)
            if set_exif_field(str(photo_path), "IPTC:Keywords", fixed_keywords):
                print(f"  -> Fixed Keywords: Converted semicolons to commas")
                keywords_success += 1
                changes_made = True
            else:
                print(f"  -> Error: Failed to update keywords")
                error_count += 1
        else:
            keywords_skip += 1

        if not changes_made and description_skip > 0 and keywords_skip > 0:
            print(f"  -> Skipped: No changes needed")

    print()
    print("=== ENHANCED METADATA FIX COMPLETE ===")
    print(f"ImageDescription updates: {description_success}")
    print(f"Keyword separator fixes:  {keywords_success}")
    print(f"Files skipped (no change): {description_skip + keywords_skip}")
    print(f"Errors:                   {error_count}")
    print(f"Total processed:          {len(jpeg_files)}")
    print()

    if description_success > 0 or keywords_success > 0:
        print("Image metadata has been enhanced for better compatibility with:")
        print("- Photo viewers (verbatim text in ImageDescription)")
        print("- Apple Photos (comma-separated keywords)")
        print("- Other photo management software")
    else:
        print("All files already have correct metadata formatting.")

    return 0


if __name__ == "__main__":
    sys.exit(main())

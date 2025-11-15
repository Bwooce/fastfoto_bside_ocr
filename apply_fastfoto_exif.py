#!/usr/bin/env python3
"""
FastFoto EXIF Application Script
Processes analysis files and applies EXIF metadata to original photos
"""

import os
import re
import subprocess
import glob
import sys
from pathlib import Path

def extract_exif_mappings(analysis_content):
    """Extract EXIF mappings from analysis file content"""
    mappings = {}

    # Find EXIF_MAPPINGS section (handle both markdown and plain formats)
    exif_section_match = re.search(r'\*\*EXIF_MAPPINGS:\*\*\s*\n(.*?)(?=\n\n|\Z)', analysis_content, re.DOTALL)
    if not exif_section_match:
        # Try plain format fallback
        exif_section_match = re.search(r'EXIF_MAPPINGS:\s*\n(.*?)(?=\n\n|\Z)', analysis_content, re.DOTALL)
        if not exif_section_match:
            return mappings

    exif_content = exif_section_match.group(1)

    # Parse each EXIF field (handle markdown format with ** and plain format)
    for line in exif_content.split('\n'):
        line = line.strip()

        # Skip notes and comments
        if line.startswith('*') or line.startswith('(Note:'):
            continue

        if ':' in line and not line.startswith('#'):
            # Handle markdown format: **Field:** value
            if line.startswith('**') and ':**' in line:
                key, value = line.split(':**', 1)
                key = key.strip('*').strip()
            # Handle plain format: Field: value
            else:
                key, value = line.split(':', 1)
                key = key.strip()

            value = value.strip().strip('[]')

            # Skip empty values or "None" values
            if value and value.lower() not in ['none', 'none visible', 'none generated']:
                mappings[key] = value

    return mappings

def find_original_photo(back_scan_filename, source_dir):
    """Find corresponding original photo for back scan"""
    # Remove _b suffix and extension
    base_name = back_scan_filename.replace('_b.jpg', '')

    # Try different extensions
    for ext in ['.jpg', '.JPG', '.jpeg', '.JPEG']:
        original_path = os.path.join(source_dir, base_name + ext)
        if os.path.exists(original_path):
            return original_path

    return None

def apply_exif_metadata(photo_path, exif_mappings):
    """Apply EXIF metadata using exiftool"""
    if not exif_mappings:
        return False, "No EXIF mappings found"

    # Build exiftool command
    cmd = ['exiftool', '-overwrite_original']

    # Map fields to exiftool syntax
    field_mapping = {
        'Caption-Abstract': '-Caption-Abstract',
        'UserComment': '-UserComment',
        'ImageDescription': '-ImageDescription',
        'DateTimeOriginal': '-DateTimeOriginal',
        'Software': '-Software',
        'ProcessingSoftware': '-ProcessingSoftware',
        'ImageUniqueID': '-ImageUniqueID',
        'IPTC:ObjectName': '-IPTC:ObjectName',
        'IPTC:Keywords': '-IPTC:Keywords',
        'XMP:Description': '-XMP:Description',
        'GPS:GPSLatitude': '-GPS:GPSLatitude',
        'GPS:GPSLongitude': '-GPS:GPSLongitude',
        'GPS:GPSLatitudeRef': '-GPS:GPSLatitudeRef',
        'GPS:GPSLongitudeRef': '-GPS:GPSLongitudeRef'
    }

    applied_fields = []
    for field, value in exif_mappings.items():
        if field in field_mapping and value.strip():
            cmd.extend([field_mapping[field] + '=' + value.strip()])
            applied_fields.append(field)

    if not applied_fields:
        return False, "No valid EXIF fields to apply"

    cmd.append(photo_path)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, f"Applied {len(applied_fields)} fields: {', '.join(applied_fields)}"
        else:
            return False, f"Exiftool error: {result.stderr}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def move_back_scan(back_scan_path, processed_dir):
    """Move back scan to processed directory"""
    try:
        os.makedirs(processed_dir, exist_ok=True)
        filename = os.path.basename(back_scan_path)
        dest_path = os.path.join(processed_dir, filename)

        if os.path.exists(back_scan_path):
            os.rename(back_scan_path, dest_path)
            return True, f"Moved to {dest_path}"
        else:
            return False, f"Back scan not found: {back_scan_path}"
    except Exception as e:
        return False, f"Move failed: {str(e)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python apply_fastfoto_exif.py <source_directory>")
        sys.exit(1)

    source_dir = sys.argv[1]
    analysis_dir = "/tmp/isolated_analysis"
    processed_dir = os.path.join(source_dir, "processed")

    if not os.path.exists(source_dir):
        print(f"Error: Source directory does not exist: {source_dir}")
        sys.exit(1)

    print(f"FastFoto EXIF Application Script")
    print(f"Source directory: {source_dir}")
    print(f"Analysis directory: {analysis_dir}")
    print(f"Processed directory: {processed_dir}")
    print()

    # Get all analysis files
    analysis_files = glob.glob(os.path.join(analysis_dir, "*_analysis.txt"))
    successful_files = []

    for analysis_file in analysis_files:
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Skip files with errors
            if 'ERROR:' in content or 'Session limit reached' in content:
                continue

            # Must have EXIF_MAPPINGS section (handle both markdown and plain formats)
            if 'EXIF_MAPPINGS:' in content or '**EXIF_MAPPINGS:**' in content:
                successful_files.append(analysis_file)
        except Exception:
            continue

    print(f"Found {len(successful_files)} successful analysis files to process")

    # Process statistics
    processed_count = 0
    success_count = 0
    error_count = 0
    moved_count = 0

    for i, analysis_file in enumerate(successful_files, 1):
        filename = os.path.basename(analysis_file)
        back_scan_filename = filename.replace('_analysis.txt', '.jpg')

        print(f"[{i}/{len(successful_files)}] Processing: {back_scan_filename}")

        try:
            # Read analysis file
            with open(analysis_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract EXIF mappings
            exif_mappings = extract_exif_mappings(content)

            # Find original photo
            original_photo = find_original_photo(back_scan_filename, source_dir)
            if not original_photo:
                print(f"  -> Original photo not found, skipping")
                error_count += 1
                continue

            # Apply EXIF metadata
            success, message = apply_exif_metadata(original_photo, exif_mappings)
            processed_count += 1

            if success:
                print(f"  -> EXIF applied: {message}")
                success_count += 1

                # Try to move back scan to processed directory
                back_scan_path = os.path.join(source_dir, back_scan_filename)
                move_success, move_message = move_back_scan(back_scan_path, processed_dir)
                if move_success:
                    print(f"  -> {move_message}")
                    moved_count += 1
                else:
                    print(f"  -> Move failed: {move_message}")
            else:
                print(f"  -> EXIF failed: {message}")
                error_count += 1

        except Exception as e:
            print(f"  -> Exception: {str(e)}")
            error_count += 1

    # Final report
    print()
    print("="*60)
    print("FASTFOTO EXIF APPLICATION COMPLETED")
    print("="*60)
    print(f"Analysis files found: {len(analysis_files)}")
    print(f"Successful analyses: {len(successful_files)}")
    print(f"Photos processed: {processed_count}")
    print(f"EXIF applications successful: {success_count}")
    print(f"EXIF applications failed: {error_count}")
    print(f"Back scans moved to processed/: {moved_count}")
    print(f"Success rate: {(success_count/processed_count*100):.1f}%" if processed_count > 0 else "N/A")
    print()
    print(f"Enhanced photos remain in: {source_dir}")
    print(f"Processed back scans moved to: {processed_dir}")
    print(f"Analysis files preserved in: {analysis_dir}")

if __name__ == "__main__":
    main()
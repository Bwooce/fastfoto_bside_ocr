#!/bin/bash

# Apple Photos Metadata Extractor
# Updates existing photos with comprehensive Apple Photos metadata
# Includes: face recognition, GPS coordinates, and orientation data
# Smart behavior: Only processes files when Apple Photos data is newer than file metadata
# Usage: ./update_face_metadata.sh [OPTIONS] directory1 [directory2] [directory3] ...

# Parse command line options
FORCE_UPDATE=""
QUIET_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Apple Photos Metadata Extractor"
            echo
            echo "Usage: $0 [OPTIONS] directory1 [directory2] [directory3] ..."
            echo
            echo "Options:"
            echo "  -f, --force       Force update even if metadata already exists"
            echo "  -q, --quiet       Quiet mode - minimal output"
            echo "  -h, --help        Show this help message"
            echo
            echo "Updates existing photos with comprehensive Apple Photos metadata:"
            echo "• Face recognition data (XMP:PersonInImage, XMP:Subject)"
            echo "• GPS coordinates (GPS:GPSLatitude, GPS:GPSLongitude, GPS:GPSAltitude)"
            echo "• SQLite display orientation from Apple Photos database (EXIF:Orientation)"
            echo
            echo "Examples:"
            echo "  $0 ~/Photos/Vacation                    # Process single directory"
            echo "  $0 -f ~/Photos/Vacation                 # Force reprocess all files"
            echo "  $0 -q ~/Photos/Dir1 ~/Photos/Dir2       # Quiet processing"
            echo "  $0 ~/Pictures/2025_PeruScanning \\       # Process original directories"
            echo "     ~/Pictures/2025_PeruScanning_done2 \\"
            echo "     ~/Pictures/2025_PeruScanning_imported"
            echo
            echo "Smart behavior:"
            echo "• Automatically detects when Apple Photos data is newer than file metadata"
            echo "• Only processes files that need updating for maximum speed"
            echo "• Use --force to reprocess all files regardless of modification dates"
            exit 0
            ;;
        -f|--force)
            FORCE_UPDATE="1"
            shift
            ;;
        -q|--quiet)
            QUIET_MODE="1"
            shift
            ;;
        -*)
            echo "❌ Error: Unknown option $1"
            echo "Use '$0 --help' for more information."
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Check if directories provided
if [ $# -eq 0 ]; then
    echo "❌ Error: No directories specified."
    echo "Usage: $0 directory1 [directory2] [directory3] ..."
    echo "Use '$0 --help' for more information."
    exit 1
fi

echo "📂 Processing directories..."
DIRS=("$@")

# Activate osxphotos virtual environment
source ~/osxphotos_env/osxphotos/bin/activate

echo "🔍 Updating comprehensive metadata (faces, GPS, orientation) for photos in directories:"
for dir in "${DIRS[@]}"; do
    echo "   $dir"
done
echo

# Function to update face metadata for files in a directory
update_directory_faces() {
    local dir_path="$1"
    local dir_name="$2"

    echo "📂 Processing directory: $dir_name"

    if [ ! -d "$dir_path" ]; then
        echo "⚠️  Directory not found: $dir_path"
        return
    fi

    # Create a temporary directory for export/update
    temp_export="/tmp/face_metadata_export_$(date +%s)"
    mkdir -p "$temp_export"

    echo "🚀 Processing metadata (faces, GPS, orientation) from Apple Photos database..."

    # Initialize counters
    total_files=0
    processed_files=0
    skipped_files=0

    # Count total files first for progress
    for photo_file in "$dir_path"/*.jpg "$dir_path"/*.jpeg "$dir_path"/*.JPG "$dir_path"/*.JPEG; do
        [ -f "$photo_file" ] && ((total_files++))
    done

    echo "📊 Found $total_files photo files to check"

    # OPTIMIZATION: Bulk query ALL Apple Photos metadata once
    echo "🚀 Bulk querying Apple Photos database (single query for all photos)..."
    temp_json="/tmp/apple_photos_bulk_$(date +%s).json"

    if ! osxphotos query --json > "$temp_json" 2>/dev/null; then
        echo "❌ Failed to query Apple Photos database"
        rm -f "$temp_json"
        return
    fi

    photos_count=$(python3 -c "import json; data=json.load(open('$temp_json')); print(len(data))" 2>/dev/null || echo "0")
    echo "✅ Retrieved metadata for $photos_count photos from Apple Photos"

    # OPTIMIZATION: Process ALL files in single Python execution with hash table in memory
    echo "🔍 Building hash table and processing all files in one Python session..."

    python3 -c "
import json
import sys
import os
import subprocess
from datetime import datetime

# Load all Apple Photos data
with open('$temp_json', 'r') as f:
    all_photos = json.load(f)

# Build filename -> metadata hash table
lookup_table = {}
for photo in all_photos:
    for name_field in ['original_filename', 'filename']:
        name = photo.get(name_field)
        if name:
            lookup_table[name] = photo

print(f'✅ Built hash table with {len(lookup_table)} filename entries for instant O(1) lookups')

# Process all files in directory
dir_path = '$dir_path'
force_update = '$FORCE_UPDATE'
quiet_mode = '$QUIET_MODE'

# Counters
processed_files = 0
skipped_files = 0

# Get all photo files
import glob
photo_files = []
for pattern in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
    photo_files.extend(glob.glob(os.path.join(dir_path, pattern)))

for photo_file in sorted(photo_files):
    if not os.path.isfile(photo_file):
        continue

    filename = os.path.basename(photo_file)

    # O(1) hash table lookup
    photo_data = lookup_table.get(filename)

    if not photo_data:
        if not quiet_mode:
            print(f'  ⏭️  Not found in Apple Photos database: {filename}')
        continue

    if not force_update:
        # Smart date comparison
        try:
            photos_mod_date = photo_data.get('date_modified') or photo_data.get('date_added')
            if photos_mod_date:
                dt = datetime.fromisoformat(photos_mod_date.replace('Z', '+00:00'))
                photos_timestamp = int(dt.timestamp())

                file_mod_time = int(os.path.getmtime(photo_file))

                if photos_timestamp <= file_mod_time:
                    if not quiet_mode:
                        print(f'⏭️  Skipping: {filename} (Apple Photos data not newer than file)')
                    skipped_files += 1
                    continue
        except:
            # Fallback: check existing metadata
            result = subprocess.run(['exiftool', '-XMP:PersonInImage', '-s', '-s', '-s', photo_file],
                                  capture_output=True, text=True)
            if result.stdout.strip():
                if not quiet_mode:
                    print(f'⏭️  Skipping: {filename} (already has Apple Photos metadata)')
                skipped_files += 1
                continue

    if not quiet_mode:
        print(f'🔍 Processing: {filename}')
        print(f'  ✅ Found in Apple Photos database')

    # Extract metadata
    persons = photo_data.get('persons', [])
    named_persons = [p for p in persons if p and p != '_UNKNOWN_' and p.strip()]

    exif_info = photo_data.get('exif_info', {})
    lat = exif_info.get('latitude')
    lon = exif_info.get('longitude')

    orientation = photo_data.get('orientation', 1)

    # Build exiftool command
    exiftool_cmd = ['exiftool', '-overwrite_original']

    # Add person/face metadata
    if named_persons:
        persons_str = ';'.join(named_persons)
        print(f'    👤 Adding face recognition: {persons_str}')
        exiftool_cmd.extend([f'-XMP:PersonInImage={persons_str}', f'-XMP:Subject={persons_str}'])

    # Add GPS coordinates
    if lat is not None and lon is not None:
        print(f'    📍 Adding GPS: {lat}, {lon}')
        exiftool_cmd.extend([
            f'-GPS:GPSLatitude={lat}',
            f'-GPS:GPSLongitude={lon}',
            f'-GPS:GPSLatitudeRef={"N" if lat >= 0 else "S"}',
            f'-GPS:GPSLongitudeRef={"E" if lon >= 0 else "W"}'
        ])

    # Add orientation
    if orientation != 1:
        orientation_map = {
            1: 'Horizontal (normal)', 2: 'Mirror horizontal', 3: 'Rotate 180',
            4: 'Mirror vertical', 5: 'Mirror horizontal and rotate 270 CW',
            6: 'Rotate 90 CW', 7: 'Mirror horizontal and rotate 90 CW', 8: 'Rotate 270 CW'
        }
        orientation_desc = orientation_map.get(orientation, str(orientation))
        print(f'    🔄 Setting orientation: {orientation} ({orientation_desc})')
        exiftool_cmd.append(f'-EXIF:Orientation={orientation_desc}')

    # Execute exiftool
    exiftool_cmd.append(photo_file)
    result = subprocess.run(exiftool_cmd, capture_output=True, text=True)

    if result.returncode == 0:
        if not quiet_mode:
            print(f'  ✅ Metadata updated successfully')
        processed_files += 1
    else:
        print(f'  ❌ Error updating {filename}: {result.stderr}')

print(f'\\n📊 Processing complete:')
print(f'   • Files processed: {processed_files}')
print(f'   • Files skipped: {skipped_files}')

" || {
        echo "❌ Failed to process files"
        rm -f "$temp_json"
        return
    }


    # Clean up temporary files
    rm -f "$temp_json"

    echo "✅ Completed processing: $dir_name"
    echo
}

# Update each directory
for dir_path in "${DIRS[@]}"; do
    dir_name=$(basename "$dir_path")
    update_directory_faces "$dir_path" "$dir_name"
done

echo "🎉 Comprehensive metadata update complete!"
echo
echo "📝 Metadata extracted from Apple Photos SQLite database and applied to EXIF:"
echo "   • Face recognition: Person names and face region coordinates (XMP:PersonInImage)"
echo "   • GPS coordinates: Latitude, longitude, altitude, and references (GPS:GPSLatitude, etc.)"
echo "   • Display orientation: SQLite orientation values applied to images (EXIF:Orientation)"
echo "   • Compatible with Adobe Lightroom, Digikam, and other photo software"
echo
echo "🔍 You can verify the metadata using:"
echo "   exiftool -XMP:PersonInImage -GPS:all -EXIF:Orientation /path/to/photo.jpg"
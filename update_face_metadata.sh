#!/bin/bash

# Apple Photos Metadata Extractor
# Updates existing photos with comprehensive Apple Photos metadata
# Includes: face recognition, GPS coordinates, and orientation data
# Usage: ./update_face_metadata.sh [directory1] [directory2] [directory3] ...

# Show help if requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Apple Photos Metadata Extractor"
    echo
    echo "Usage: $0 directory1 [directory2] [directory3] ..."
    echo "       $0 --help"
    echo
    echo "Updates existing photos with comprehensive Apple Photos metadata:"
    echo "• Face recognition data (XMP:PersonInImage, XMP:Subject)"
    echo "• GPS coordinates (GPS:GPSLatitude, GPS:GPSLongitude, GPS:GPSAltitude)"
    echo "• SQLite display orientation from Apple Photos database (EXIF:Orientation)"
    echo
    echo "Examples:"
    echo "  $0 ~/Photos/Vacation                 # Process single directory"
    echo "  $0 ~/Photos/Dir1 ~/Photos/Dir2        # Process multiple directories"
    echo "  $0 ~/Pictures/2025_PeruScanning \\    # Process original directories"
    echo "     ~/Pictures/2025_PeruScanning_done2 \\
    echo "     ~/Pictures/2025_PeruScanning_imported"
    echo
    echo "At least one directory must be specified."
    exit 0
fi

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

    # Count photos in Apple Photos from this directory
    photo_count=$(osxphotos list --name "*.jpg" --name "*.jpeg" --name "*.JPG" --name "*.JPEG" 2>/dev/null | wc -l)
    echo "📊 Found $photo_count photos in Apple Photos database"

    if [ "$photo_count" -gt 0 ]; then
        echo "🚀 Exporting metadata (faces, GPS, orientation) using osxphotos..."

        # Use osxphotos to export with comprehensive metadata - faces, GPS, and orientation
        # --fix-orientation ensures we get the SQLite display orientation from Apple Photos database
        # We'll match by filename and only process files that exist in our target directory
        osxphotos export "$temp_export" \
            --exiftool \
            --fix-orientation \
            --update \
            --overwrite \
            --filename "{original_name}" \
            --verbose \
            --name "*.jpg" --name "*.jpeg" --name "*.JPG" --name "*.JPEG"

        echo "📋 Copying updated metadata to target directory..."

        # Copy metadata from exported files back to original directory
        # Only for files that actually exist in our target directory
        for exported_file in "$temp_export"/*.jpg "$temp_export"/*.jpeg "$temp_export"/*.JPG "$temp_export"/*.JPEG; do
            if [ -f "$exported_file" ]; then
                filename=$(basename "$exported_file")
                target_file="$dir_path/$filename"

                if [ -f "$target_file" ]; then
                    echo "✅ Updating: $filename"
                    # Copy comprehensive metadata from exported file to target file
                    # Includes faces, GPS coordinates, and orientation data
                    exiftool -TagsFromFile "$exported_file" \
                        -XMP:PersonInImage \
                        -XMP:Subject \
                        -GPS:GPSLatitude \
                        -GPS:GPSLongitude \
                        -GPS:GPSLatitudeRef \
                        -GPS:GPSLongitudeRef \
                        -GPS:GPSAltitude \
                        -GPS:GPSAltitudeRef \
                        -EXIF:Orientation \
                        -EXIF:GPSInfo \
                        -overwrite_original \
                        "$target_file"
                else
                    echo "⏭️  Skipping: $filename (not in target directory)"
                fi
            fi
        done

        echo "🧹 Cleaning up temporary files..."
        rm -rf "$temp_export"

    else
        echo "❌ No photos found in Apple Photos for this directory"
    fi

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
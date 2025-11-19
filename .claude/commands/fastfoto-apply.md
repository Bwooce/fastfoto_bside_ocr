# Apply FastFoto EXIF Metadata

Apply extracted handwritten metadata to original photo files using exiftool with enhanced compatibility for Google Photos and Apple Photos.

**Usage:** `/fastfoto-apply [source_directory]`

## Prerequisites

You must have completed `/fastfoto-analyze [source_directory]` first. This command reads the analysis results from `/tmp/isolated_analysis/` (398 analysis files) and applies the extracted metadata to your original photo files.

## What This Does

1. **Reads all 398 analysis files** from `/tmp/isolated_analysis/`
2. **Extracts EXIF mappings** from each markdown analysis file
3. **Maps back scan files** to original photo files in source directory
4. **Applies comprehensive EXIF metadata** to each original photo using exiftool
5. **Handles GPS coordinates, dates, and transcriptions** properly
6. **Automatically organizes processed files** - moves `_b.jpg` files to `processed/` subdirectory
7. **Generates comprehensive report** showing successes, failures, and statistics

## Enhanced EXIF Fields Applied (2024 Standards)

For each analyzed back scan, applies metadata to the corresponding original photo:

### **Core EXIF Fields:**
- **Caption-Abstract**: Verbatim handwritten text
- **UserComment**: Language-tagged verbatim transcription
- **ImageDescription**: Brief event/location context
- **DateTimeOriginal**: ISO format (YYYY:MM:DD HH:MM:SS)
- **Software**: APS codes and processing data
- **ImageUniqueID**: Unique identifier from analysis

### **Apple Photos Compatibility:**
- **IPTC:ObjectName**: Handwritten text for Apple Photos title
- **IPTC:Keywords**: Semicolon-separated (dates;names;locations;events)

### **Cross-Platform Compatibility:**
- **XMP:Description**: Event/location context
- **GPS:GPSLatitude/Longitude**: Coordinates with hemisphere refs
- **GPS:GPSLatitudeRef/LongitudeRef**: Direction references (N/S, E/W)

## Process Flow

The Task tool will:
1. Process each of the 398 analysis files sequentially
2. For each analysis file:
   - Extract filename and EXIF mappings from analysis text
   - Find corresponding original photo in source directory
   - Skip if original photo not found (continues processing)
   - Apply extracted EXIF fields using exiftool
   - Attempt to move processed back scan to `processed/` subdirectory
3. Generate detailed report with:
   - Total files processed
   - Successful applications
   - Failed applications
   - Skipped files (with reasons)
   - Back scans moved to processed/
   - Success rate percentage

## Safety Features

- **Continues on missing back scans** - file moves are optional, processing never stops
- **Exiftool auto-backup** - creates .jpg_original backup files
- **Validation** ensures filename mapping correctness
- **Error handling** - processes all 398 files even if some fail
- **Comprehensive reporting** - detailed statistics and sample results

## Metadata Quality Filtering

**CRITICAL:** The apply system MUST filter out low-quality or problematic metadata:

### **Skip/Exclude Fields Containing:**
❌ **Useless Keywords:**
- "degraded", "no readable text", "None extractable"
- "no dates, names, or locations identified"
- "[empty", "[leave empty", "no extractable metadata"

❌ **Generic Descriptions:**
- "None - no clear context visible"
- "None - insufficient context"
- "Photo lab back scan with degraded processing data"
- "Photo back scan with machine-printed processing strip"

❌ **Problematic Titles:**
- "[uncertain: vertical text]"
- "[uncertain: machine-printed processing data"
- Any Caption-Abstract starting with "[uncertain:" and no clear content

❌ **Watermark-Only ProcessingSoftware:**
- Skip if only contains: "Kodak Royal Paper", "Fuji Color", "photo lab watermarks"
- Apply only if contains actual APS/processing codes with data

### **Quality Threshold Rules:**
✅ **Apply Field IF:**
- Contains meaningful personal content (names, locations, events)
- Contains specific dates or times
- Contains identifiable technical data (APS codes with IDs/timestamps)
- Contains clear handwritten transcriptions

❌ **Skip Field IF:**
- Only contains generic lab/watermark information
- Contains uncertainty markers without substantive content
- Describes technical limitations ("too faded", "unclear", "degraded")
- Uses placeholder language ("None", "empty", "no clear")

## File Organization

After applying EXIF metadata:
- **Original photos** remain in source directory with enhanced metadata
- **Successfully processed back scans** moved to `[source_directory]/processed/`
- **Failed back scans** stay in original location for manual review
- **Analysis files** remain in `/tmp/isolated_analysis/` for reference

## Expected Results

Processing 398 analysis files typically yields:
- 300+ original photos with successfully applied EXIF metadata
- Back scans organized to processed/ subdirectory
- Comprehensive statistics showing success rate
- Detailed report of any failures or skipped files

**Provide your source directory path to begin applying extracted metadata to all 398 analyzed photos.**

**Runs the FastFoto EXIF application script to process all analysis files and apply metadata to original photos.**

Execute: `python apply_fastfoto_exif.py [source_directory]`

This script will:
- Process all successful analysis files from `/tmp/isolated_analysis/`
- Extract EXIF mappings from each markdown analysis file
- Find corresponding original photos in the source directory
- Apply comprehensive EXIF metadata using exiftool
- Move processed back scan files to `processed/` subdirectory
- Generate detailed statistics and processing summary
- Continue processing even if individual files fail

The script handles all 362+ successful analysis files automatically and provides a comprehensive report of successes, failures, and file organization.
# FastFoto Apply - Quick Start Guide

## One-Line Usage

```bash
/fastfoto-apply ~/Pictures/2025_PeruScanning
```

That's it! This single command will:

1. Process all 398 analysis files from `/tmp/isolated_analysis/`
2. Extract EXIF metadata from each analysis
3. Apply metadata to the corresponding original photos
4. Move processed back scans to `processed/` subdirectory
5. Generate a comprehensive report with statistics

## What Happens

The `/fastfoto-apply` command uses the Task tool to:

- **Read** all 398 analysis files (no scripts created)
- **Extract** EXIF mappings from each file
- **Apply** metadata using exiftool command-line
- **Organize** processed back scans automatically
- **Report** detailed statistics: success rate, failures, skipped files

## Prerequisites

Before running `/fastfoto-apply`:

1. Run `/fastfoto-analyze ~/Pictures/2025_PeruScanning` first
2. Wait for 398 analysis files to be generated in `/tmp/isolated_analysis/`
3. Make sure exiftool is installed: `brew install exiftool`

## Expected Results

Processing 398 analysis files typically yields:

- **300+ photos** with successfully applied EXIF metadata
- **Back scans** organized to `processed/` subdirectory
- **Success rate** typically 85-90%
- **Processing time** 2-3 hours (30-45 seconds per file)

## What Gets Applied

For each original photo, the command applies:

**Descriptive Fields:**
- Caption-Abstract: Verbatim handwritten text
- UserComment: Language-tagged transcription
- ImageDescription: Event/location context

**Photo Management Fields:**
- DateTimeOriginal: ISO date format
- IPTC:Keywords: Semicolon-separated tags
- IPTC:ObjectName: Title for Apple Photos

**Location Fields:**
- GPS:GPSLatitude/Longitude: Coordinates
- GPS:GPSLatitudeRef/LongitudeRef: Direction references

**Processing Data:**
- Software: APS codes if present
- ImageUniqueID: Unique identifier

## File Organization

After running the command:

```
~/Pictures/2025_PeruScanning/
├── 1966_Prom_0001.jpg (EXIF updated)
├── 1966_Prom_0002.jpg (EXIF updated)
├── 1978_Location_0001.jpg (EXIF updated)
├── ...
└── processed/
    ├── 1966_Prom_0001_b.jpg
    ├── 1966_Prom_0002_b.jpg
    ├── 1978_Location_0001_b.jpg
    └── ... (all processed back scans)
```

- **Original photos** stay in root directory with updated EXIF
- **Back scans** moved to `processed/` subdirectory
- **Unprocessed back scans** remain in root for manual review

## Viewing Results

After applying EXIF metadata, view results in Apple Photos or Google Photos:

**Apple Photos:**
- Photos now show handwritten text as titles (IPTC:ObjectName)
- Keywords appear in photo info
- Dates are recognized from DateTimeOriginal

**Google Photos:**
- GPS coordinates appear on map view
- Dates are recognized correctly
- Descriptions appear in photo details
- Keywords available for searching

## Checking Applied Metadata

To verify metadata was applied correctly:

```bash
# View metadata for one photo
exiftool ~/Pictures/2025_PeruScanning/1966_Prom_0001.jpg | head -30

# Check for specific fields
exiftool ~/Pictures/2025_PeruScanning/1966_Prom_0001.jpg | grep -E "Caption|UserComment|Keywords|DateTimeOriginal|GPSLatitude"

# Count back scans moved to processed/
ls ~/Pictures/2025_PeruScanning/processed/ | wc -l
```

## If Something Goes Wrong

The process is designed to be resilient:

- **Missing original photos?** Skipped gracefully, processing continues
- **Empty EXIF mappings?** File skipped, processing continues
- **Back scan move fails?** Metadata still applied, back scan stays in place
- **Interrupted mid-process?** Re-run command, duplicate applications are safe

Check the final report for details on any failures.

## For More Details

See `./FASTFOTO_APPLY_IMPLEMENTATION.md` for:

- Complete implementation details
- EXIF field mappings
- Error handling strategy
- File format specifications
- Performance expectations

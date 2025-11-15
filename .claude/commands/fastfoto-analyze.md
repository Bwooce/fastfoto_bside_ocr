# FastFoto OCR Analysis

Extract handwritten metadata from photo back scans using isolated Claude CLI analysis.

**Usage:** `/fastfoto-analyze [source_directory]`

## What This Does

1. **Prepares back scans** from your source directory
2. **Processes each photo individually** using isolated Claude CLI analysis
3. **Extracts comprehensive OCR data**:
   - Verbatim handwritten text with uncertainty markers
   - APS technical codes (processing timestamps, roll IDs, equipment data)
   - Orientation assessment (rotation corrections needed)
   - Dates, locations, people, events from handwritten notes
   - GPS coordinates for definitively identifiable places only
   - Multi-language support (Spanish, English, Dutch, German, etc.)

## Enhanced EXIF Compatibility (2024 Standards)

Compatible with **Google Photos** and **Apple Photos**:
- **IPTC Keywords** (semicolon-separated for Apple Photos)
- **XMP Description** (broad compatibility)
- **EXIF DateTimeOriginal** (YYYY:MM:DD HH:MM:SS format with time when available)
- **GPS coordinates** (decimal degrees with hemisphere references)
- **Multiple title fields** (Caption-Abstract, ObjectName, ImageDescription)

## Process

Please provide your source directory path (e.g., `~/Pictures/PhotoCollection` or `/path/to/photos`).

I'll run:
1. `python src/preprocess_images.py [SOURCE_DIR] --output /tmp/fastfoto_prepared --force`
2. `./isolated_ocr_analysis.sh` (processes all back scan files individually)

## Anti-Hallucination Protection

- **Complete photo isolation** - each analysis in fresh Claude instance with zero context
- **No fabrication** - no geographic guessing or cross-photo pattern building
- **Verbatim transcription only** - preserves original spelling, marks uncertain text as [uncertain: word?]
- **Real GPS coordinates** - generated only for definitively recognizable locations

## Output

Results saved to `/tmp/isolated_analysis/` with individual analysis files for each back scan.
- **Cost**: ~1¢ per photo for comprehensive OCR analysis
- **Accuracy**: Authenticated results with anti-hallucination protection

**Provide your source directory path to begin analysis.**
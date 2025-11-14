# FastFoto OCR Analysis

Complete FastFoto OCR analysis: extract handwritten metadata and identify rotation issues.

**Usage:** Specify your source directory as a parameter when running this command.

## Overview

This is the complete FastFoto workflow that will:

1. **Analyze** your photo collection for orientation issues and extract handwritten metadata
2. **Process** each back scan individually using Read tool
3. **Extract** verbatim handwritten text and generate EXIF metadata

## Step 1: Specify Source Directory

Please provide your source directory path (e.g., ~/Pictures/2025_PeruScanning or /path/to/your/photos).

Let me know your source directory and I'll run:

```bash
# Prepare back scans for OCR (replace SOURCE_DIR with your path)
python src/preprocess_images.py [SOURCE_DIR] --output /tmp/fastfoto_prepared --force
```

Now I'll process all back scans using Read tool for OCR metadata extraction. **I'll skip the broken batch orientation script** and do real orientation analysis using Read tool directly. This will:

- Analyze each back scan individually using Read tool
- Extract verbatim handwritten text in multiple languages
- Parse dates, locations, people names, and events
- **Generate GPS coordinates** for recognized locations (Lima, Bogotá, Dallas, etc.)
- Identify rotation issues by visual inspection of actual image content
- Generate a comprehensive proposal file for EXIF updates

**Processing all back scan files now...**

## Step 2: Process Back Scans with Read Tool

After preparation completes, I'll analyze each back scan file individually using Read tool:
- Extract verbatim handwritten text in multiple languages
- Parse dates, locations, people names, and events
- Generate GPS coordinates for recognized locations
- Create metadata proposals for EXIF updates

**Note:** This uses Read tool directly on each image - no automated scripts or simulations.

## Step 3: Apply EXIF Updates

After analysis, apply extracted metadata using exiftool directly:

**Manual EXIF updates based on extracted text:**
```bash
# Example commands for specific files (generated during analysis)
exiftool -Caption-Abstract="Extracted handwritten text" -GPS:GPSLatitude="4.7110" -GPS:GPSLongitude="-74.0721" image.jpg
```

## Expected Results

After completion, your photos will have:
- **Caption-Abstract:** Verbatim handwritten text from photo backs
- **UserComment:** Language-tagged transcriptions
- **Description:** Event and location context
- **Keywords:** Parsed dates, names, places
- **DateTimeOriginal:** Corrected dates when found
- **GPS Coordinates:** Latitude/longitude for recognized locations (Lima, Bogotá, etc.)
- **Orientation:** Fixed rotation issues based on visual content analysis

Let me start the analysis process now...
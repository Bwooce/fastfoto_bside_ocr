# Apply FastFoto EXIF Updates

Apply extracted metadata to original image files using exiftool commands.

**Usage:** Specify your source directory path where the original photos are located.

## Prerequisites

You should have completed FastFoto analysis using Read tool to extract metadata from back scans.

## Step 1: Apply Extracted Metadata

Based on the verbatim text extracted from each back scan, apply EXIF metadata:

```bash
# Template command for applying extracted metadata:
exiftool -Caption-Abstract="[Verbatim handwritten text]" \
         -UserComment="[Language] handwritten text: [transcription]" \
         -Description="[Event/location context]" \
         -Keywords="[parsed dates, names, locations]" \
         -DateTimeOriginal="[YYYY-MM-DD HH:MM:SS]" \
         -GPS:GPSLatitude="[latitude]" \
         -GPS:GPSLongitude="[longitude]" \
         [original_image.jpg]
```

## Step 2: Example Applications

Based on common findings from back scan analysis:

```bash
# Example: Based on extracted handwritten text
exiftool -Caption-Abstract="[actual extracted text]" \
         -UserComment="Spanish handwritten text: [actual transcription]" \
         -Description="[actual event context]" \
         -Keywords="[actual parsed elements]" \
         -DateTimeOriginal="[actual date in ISO format]" \
         -GPS:GPSLatitude="[actual coordinates if location identified]" \
         -GPS:GPSLongitude="[actual coordinates if location identified]" \
         original_photo.jpg
```

## Step 3: Batch Processing for Similar Content

For multiple files with similar metadata:

```bash
# Apply GPS coordinates to photos from identified location
find [SOURCE_DIR] -name "[location_pattern]_*.jpg" -exec exiftool \
  -GPS:GPSLatitude="[actual_latitude]" \
  -GPS:GPSLongitude="[actual_longitude]" \
  -Keywords+="[actual_location]" {} \;
```

## Step 4: Verify Updates

After application, you can verify the updates were applied:

```bash
exiftool ~/Pictures/2025_PeruScanning/[sample_filename.jpg]
```

The EXIF data should now include the extracted handwritten metadata from the back scans.
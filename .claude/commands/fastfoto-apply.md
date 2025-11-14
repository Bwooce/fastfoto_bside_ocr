# Apply FastFoto EXIF Updates

Apply extracted metadata to original image files using exiftool commands.

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
# Example: Bogotá photos with Spanish text
exiftool -Caption-Abstract="Hotel Tequendama, Marzo 1981" \
         -UserComment="Spanish handwritten text: Hotel Tequendama, Marzo 1981" \
         -Description="Hotel stay in Bogotá" \
         -Keywords="Bogotá, hotel, 1981, March" \
         -DateTimeOriginal="1981-03-01 00:00:00" \
         -GPS:GPSLatitude="4.7110" \
         -GPS:GPSLongitude="-74.0721" \
         original_photo.jpg
```

## Step 3: Batch Processing for Similar Content

For multiple files with similar metadata:

```bash
# Apply GPS coordinates to all Bogotá photos
find ~/Pictures/2025_PeruScanning -name "Bogota_*.jpg" -exec exiftool \
  -GPS:GPSLatitude="4.7110" \
  -GPS:GPSLongitude="-74.0721" \
  -Keywords+="Bogotá" {} \;
```

## Step 4: Verify Updates

After application, you can verify the updates were applied:

```bash
exiftool ~/Pictures/2025_PeruScanning/[sample_filename.jpg]
```

The EXIF data should now include the extracted handwritten metadata from the back scans.
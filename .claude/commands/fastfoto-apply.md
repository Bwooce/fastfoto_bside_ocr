# Apply FastFoto EXIF Metadata

Apply extracted handwritten metadata to original photo files using exiftool with enhanced compatibility for Google Photos and Apple Photos.

**Usage:** `/fastfoto-apply [source_directory]`

## Prerequisites

You must have completed `/fastfoto-analyze [source_directory]` first. This command reads the analysis results from `/tmp/isolated_analysis/` and applies the extracted metadata to your original photo files.

## Enhanced EXIF Fields Applied (2024 Standards)

For each analyzed back scan, applies comprehensive metadata to the corresponding original photo:

### **Core EXIF Fields:**
- **Caption-Abstract**: Verbatim handwritten text
- **UserComment**: Language-tagged verbatim transcription
- **ImageDescription**: Brief event/location context when clear
- **DateTimeOriginal**: EXIF format (YYYY:MM:DD HH:MM:SS) with time when available
- **ProcessingSoftware**: APS codes and lab processing data
- **ImageUniqueID**: APS roll+frame combination for true uniqueness per photo

### **Apple Photos Compatibility:**
- **IPTC:ObjectName**: Handwritten text for Apple Photos title field
- **IPTC:Keywords**: Semicolon-separated (dates;names;locations;events)

### **Cross-Platform Compatibility:**
- **XMP:Description**: Event/location context for broad application support
- **GPS coordinates**: Decimal degrees with hemisphere references
- **Orientation corrections**: Rotation metadata when needed

### **Example Commands Generated:**
```bash
# Enhanced metadata application for maximum compatibility
exiftool -Caption-Abstract="Hotel [uncertain: name?] March [uncertain: 1984?]" \
         -UserComment="Spanish handwritten text: Hotel [uncertain: name?] March [uncertain: 1984?]" \
         -ImageDescription="Hotel visit March 1984" \
         -IPTC:ObjectName="Hotel [uncertain: name?] March [uncertain: 1984?]" \
         -IPTC:Keywords="hotel;March;1984;travel" \
         -XMP:Description="Hotel visit March 1984" \
         -DateTimeOriginal="1984:03:01 00:00:00" \
         -ProcessingSoftware="APS ID123-456 <5>" \
         -ImageUniqueID="ID123-456-05" \
         -GPS:GPSLatitude="40.7128" \
         -GPS:GPSLongitude="-74.0060" \
         -GPS:GPSLatitudeRef="N" \
         -GPS:GPSLongitudeRef="W" \
         [original_photo.jpg]
```

## Process

1. **Reads analysis results** from `/tmp/isolated_analysis/`
2. **Maps back scan files** to original photo files
3. **Generates enhanced exiftool commands** with cross-platform compatibility
4. **Applies comprehensive EXIF metadata** for optimal photo management
5. **Handles orientation corrections** and time zone considerations

## Safety Features

- **Automatic backup** of original files (exiftool creates .jpg_original files)
- **File mapping validation** ensures correct metadata application
- **Existing EXIF preservation** while adding extracted metadata
- **Processing status reports** for each photo with error handling
- **Dry-run option** to preview commands before execution

## Compatibility Benefits

- **Apple Photos**: Recognizes IPTC keywords and ObjectName titles
- **Google Photos**: Reads GPS coordinates and DateTimeOriginal
- **Adobe Applications**: Full XMP compatibility
- **Professional workflows**: Complete IPTC standard compliance

**Provide your source directory path to begin applying extracted metadata to your photos.**
# EXIF Fields Used by FastFoto OCR

## Overview

This document lists all EXIF/IPTC/XMP fields written by the FastFoto OCR system, organized by category.

## Date/Time Fields

| Field | Standard | Purpose | Example |
|-------|----------|---------|---------|
| `DateTimeOriginal` | EXIF | Primary photo date/time | `1999:06:07 11:32:00` |
| `CreateDate` | EXIF | Creation date (set to same as DateTimeOriginal) | `1999:06:07 11:32:00` |
| `ModifyDate` | EXIF | Modification date (set to same as DateTimeOriginal) | `1999:06:07 11:32:00` |
| `OffsetTimeOriginal` | EXIF | Timezone offset for original time | `+12:00` or `-05:00` |
| `OffsetTime` | EXIF | Timezone offset (duplicate) | `+12:00` |
| `GPSDateStamp` | EXIF | GPS date | `1999:06:07` |
| `GPSTimeStamp` | EXIF | GPS time | `11:32:00` |

**Note**: All date fields set consistently to avoid confusion. Timezone calculated from GPS coordinates when available.

## GPS Location Fields

| Field | Standard | Purpose | Example |
|-------|----------|---------|---------|
| `GPSLatitude` | EXIF | Latitude coordinate | `52, 5, 30.0` |
| `GPSLatitudeRef` | EXIF | North/South | `N` or `S` |
| `GPSLongitude` | EXIF | Longitude coordinate | `5, 7, 15.0` |
| `GPSLongitudeRef` | EXIF | East/West | `E` or `W` |

**Format**: Degrees, Minutes, Seconds (DMS)

## Location Text Fields (IPTC Extension)

| Field | Standard | Purpose | Example |
|-------|----------|---------|---------|
| `LocationCreatedLocationName` | IPTC | Venue/landmark name | `Hotel Dimitry Dallas` |
| `LocationCreatedCity` | IPTC | City name | `Dallas` |
| `LocationCreatedProvinceState` | IPTC | State/province | `Texas` |
| `LocationCreatedCountryName` | IPTC | Full country name | `United States` |
| `LocationCreatedCountryCode` | IPTC | ISO 3166 country code | `US` |
| `LocationCreatedSublocation` | IPTC | Neighborhood/district | `San Isidro` |

**Usage**: Hotels, institutions (schools, churches), landmarks from OCR text

## Descriptive Text Fields

| Field | Standard | Purpose | Max Length | Example |
|-------|----------|---------|------------|---------|
| `Caption-Abstract` | IPTC | Photo caption/summary | 1000 chars | `Family vacation at beach` |
| `Description` | XMP | Description (duplicate) | 1000 chars | Same as Caption-Abstract |
| `UserComment` | EXIF | Full OCR text + metadata | 2000 chars | `Complete OCR text... [Language: es] [Confidence: 0.92]` |
| `Keywords` | IPTC | Searchable keywords | N/A (array) | `["vacation", "beach", "1999"]` |
| `Subject` | XMP | Subject keywords (duplicate) | N/A (array) | Same as Keywords |

**Keywords include**: People names, institutions, events, locations, dates

## Film Roll & Processing Fields

| Field | Standard | Purpose | Example |
|-------|----------|---------|---------|
| `ImageUniqueID` | EXIF | Film roll ID | `352-417` or `ID529-981` |
| `CameraSerialNumber` | EXIF | Backup location for roll ID | Same as ImageUniqueID |
| `ImageNumber` | EXIF | Frame number on roll | `24` |
| `Make` | EXIF | Processing lab | `Processed by VIKD` or `Processed by CHIOM` |

**Usage**: Consumer processing format (###-###) and APS format (ID###-###)

## Processing Metadata Fields

| Field | Standard | Purpose | Example |
|-------|----------|---------|---------|
| `Software` | EXIF | Processing software | `FastFoto OCR v1.0` |
| `ImageDescription` | EXIF | OCR metadata summary | `OCR Confidence: 0.92 \| Language: es` |

## Field Priority & Rules

### Primary Priority (Always Set if Available)
1. `DateTimeOriginal` - Most important field
2. `GPSLatitude` / `GPSLongitude` - If location identified
3. `Caption-Abstract` - If descriptive text found
4. `UserComment` - Always includes full OCR text

### Secondary Priority (Set When Relevant)
1. Roll/Frame IDs - If machine-printed metadata found
2. Location text fields - If location names extracted
3. Keywords - Extracted from all text sources

### Preservation Rules
- **Existing EXIF preserved** unless explicitly overwriting
- User reviews all changes via proposal file before application
- Backup created automatically (unless `--overwrite-original` flag used)

## ExifTool Command Examples

### Write date only:
```bash
exiftool -DateTimeOriginal="1999:06:07 11:32:00" IMG_001.jpg
```

### Write GPS coordinates:
```bash
exiftool -GPSLatitude="52, 5, 30.0" -GPSLatitudeRef="N" \
         -GPSLongitude="5, 7, 15.0" -GPSLongitudeRef="E" IMG_001.jpg
```

### Write location text:
```bash
exiftool -LocationCreatedCity="Dallas" \
         -LocationCreatedCountryName="United States" \
         -LocationCreatedCountryCode="US" IMG_001.jpg
```

### Write multiple keywords:
```bash
exiftool -Keywords="vacation" -Keywords="1999" -Keywords="beach" IMG_001.jpg
```

## Compatibility

### Software Compatibility
- ✅ **Lightroom**: Reads all IPTC and EXIF fields
- ✅ **Photos (macOS/iOS)**: Reads DateTimeOriginal, GPS, Keywords
- ✅ **Google Photos**: Reads DateTimeOriginal, GPS
- ✅ **ExifTool**: Full read/write support for all fields
- ⚠️ **Windows Explorer**: Limited to basic EXIF (date, GPS)

### File Format Support
- ✅ **JPEG**: Full support for all fields
- ✅ **TIFF**: Full support for all fields
- ⚠️ **Other formats**: Not tested, likely work but verify first

## Data Sources by Field

| Field Category | Primary Source | Secondary Source |
|----------------|----------------|------------------|
| Dates | Zone 1 (bottom edge machine print) | Zone 4 (handwritten Spanish) |
| GPS Coordinates | Geocoded from location names | Known location database |
| Location Names | Zone 4 (handwritten) | Venue/institution names |
| Roll/Frame IDs | Zone 1 (consumer) or Zone 2 (APS) | - |
| Descriptive Text | Zone 4 (handwritten) | All zones combined |
| Keywords | Extracted from all text | Institution/people names |

## Limitations & Notes

1. **GPS Precision**: Coordinates from venue names are approximate (city/building level)
2. **Date Ambiguity**: Two-digit years converted using 1966-2030 range
3. **Text Length**: Caption and UserComment fields have length limits
4. **Keywords**: Automatically extracted, user should review for relevance
5. **Timezone**: Calculated from GPS coordinates, may not reflect actual photo timezone
6. **Backup Files**: ExifTool creates `*_original` backup files unless disabled

## Reference Standards

- **EXIF 2.3**: Core date, GPS, and technical fields
- **IPTC Core 1.3**: Caption, keywords, creator fields
- **IPTC Extension 1.5**: Location created fields (venue, city, country)
- **XMP**: Duplicate/supplementary descriptive fields

## See Also

- [ExifTool Documentation](https://exiftool.org/)
- [EXIF 2.3 Specification](http://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf)
- [IPTC Photo Metadata Standard](https://www.iptc.org/std/photometadata/specification/)

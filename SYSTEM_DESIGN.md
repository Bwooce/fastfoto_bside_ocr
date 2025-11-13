# FastFoto Back-Side OCR System Design

## Architecture Overview

**Solution Type**: Python-based LLM Agent with Claude Vision API

**Core Components**:
1. **File Scanner**: Recursive directory traversal and file pairing
2. **OCR Engine**: Claude Vision API with structured prompting
3. **Metadata Parser**: Extract and validate dates, locations, film IDs
4. **EXIF Writer**: ExifTool integration for metadata updates
5. **Review System**: Human-readable proposal file generation
6. **Batch Orchestrator**: Multi-process coordination

## System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: Discovery                           │
│  Scan directory tree → Pair _b files with originals            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Phase 2: Analysis (Non-destructive)          │
│  For each _b file:                                              │
│    1. Check if useful (not just damage/marks)                   │
│    2. OCR with Claude Vision (all orientations)                 │
│    3. Extract: dates, locations, film IDs, free text            │
│    4. Validate and normalize data                               │
│    5. Append to proposal file                                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Phase 3: Review                              │
│  Human reviews proposal.txt and makes any corrections           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    Phase 4: Application                         │
│  For each approved change:                                      │
│    1. Read current EXIF from original photo                     │
│    2. Update with new metadata via ExifTool                     │
│    3. Move _b file to processed/ subdirectory                   │
│    4. Log all changes                                           │
└─────────────────────────────────────────────────────────────────┘
```

## EXIF Field Mapping

### Date/Time Information

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| Photo date/time | `DateTimeOriginal` | EXIF | Primary field: YYYY:MM:DD HH:MM:SS |
| | `CreateDate` | EXIF | Set to same value |
| | `ModifyDate` | EXIF | Set to same value for consistency |
| | `SubSecTimeOriginal` | EXIF | If HH:MM includes seconds |
| OCR confidence | `ImageDescription` | EXIF | Store confidence score + source |
| Date source note | `UserComment` | EXIF | e.g., "From OCR: handwritten text" |

### Geolocation Information

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| GPS Latitude | `GPSLatitude` + `GPSLatitudeRef` | EXIF | Decimal degrees converted to DMS |
| GPS Longitude | `GPSLongitude` + `GPSLongitudeRef` | EXIF | Decimal degrees converted to DMS |
| Location name | `LocationCreatedLocationName` | IPTC Extension | Human-readable location |
| City | `LocationCreatedCity` | IPTC Extension | City name |
| State/Province | `LocationCreatedProvinceState` | IPTC Extension | Province/state |
| Country | `LocationCreatedCountryName` | IPTC Extension | Full country name |
| Country Code | `LocationCreatedCountryCode` | IPTC Extension | ISO 3166 code |
| Sublocation | `LocationCreatedSublocation` | IPTC Extension | Specific place within city |
| GPS timestamp | `GPSTimeStamp` + `GPSDateStamp` | EXIF | Match photo date/time |

### Timezone Information

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| Offset from UTC | `OffsetTimeOriginal` | EXIF | e.g., "+12:00", "-05:00" |
| | `OffsetTime` | EXIF | Same as OffsetTimeOriginal |

### Film Roll Information (APS/Kodak)

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| Film roll ID | `ImageUniqueID` | EXIF | Store as NNN-NNN format |
| Frame number | `ImageNumber` | EXIF | Frame on roll (e.g., 16, 10) |
| Film type/notes | `Make` | EXIF | "Kodak APS" or similar |
| Additional film info | `CameraSerialNumber` | EXIF | Store roll ID here as alternative |
| | `InternalSerialNumber` | EXIF | Backup location for roll ID |

### Free Text / Handwritten Notes

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| Caption/description | `Caption-Abstract` | IPTC | Primary free text field |
| | `Description` | XMP | Duplicate for compatibility |
| Keywords from text | `Keywords` | IPTC | Extract locations, names, events |
| | `Subject` | XMP | Same as Keywords |
| Full OCR text | `UserComment` | EXIF | Complete extracted text |
| OCR language | `ImageDescription` | EXIF | Append: "Language: en/es" |

### Processing Metadata

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| Processing software | `Software` | EXIF | "FastFoto OCR Processor v1.0" |
| Processing date | `ProcessingSoftware` | EXIF | When OCR was performed |
| Source file | `RelatedImageFileFormat` | EXIF | Reference to _b file |

### Filename Discrepancy Warnings

| Data Type | EXIF Field(s) | Standard | Notes |
|-----------|--------------|----------|-------|
| Warning flag | `Rating` | XMP | Use 1-star to flag discrepancies |
| Discrepancy note | `Instructions` | IPTC | Describe filename vs OCR date difference |

## Configuration File Design

**File**: `config.yaml`

```yaml
# FastFoto OCR Configuration
version: "1.0"

# Claude API Configuration
api:
  provider: "anthropic"  # or "openai" for GPT-4o
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"  # Read from environment
  max_retries: 3
  timeout_seconds: 30

# Processing Configuration
processing:
  max_workers: 4  # Concurrent processes (adjust for CPU count)
  min_confidence_threshold: 0.6  # Minimum OCR confidence to accept
  max_processing_time_per_image: 300  # 5 minutes in seconds

# File Patterns
files:
  input_extensions: [".jpg", ".jpeg", ".tif", ".tiff", ".JPG", ".JPEG", ".TIF", ".TIFF"]
  back_suffixes: ["_b", "_B"]
  processed_directory: "processed"
  proposal_file: "exif_updates_proposal.txt"
  log_file: "fastfoto_ocr.log"

# Date Format Recognition
date_formats:
  # Format definitions with regex patterns
  - name: "DD/MM/YY"
    pattern: '(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2})'
    example: "25/12/99"
    priority: 1

  - name: "DD/MM/YYYY"
    pattern: '(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})'
    example: "25/12/1999"
    priority: 1

  - name: "APS_YYYY_MMM_D"
    pattern: '(\d{4})[/\-\.]([A-Za-z]{3})[/\-\.](\d{1,2})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?'
    example: "1999/DEC/25 3:45PM"
    priority: 2
    indicators: ["Kodak", "APS", "Advanced Photo System"]

  - name: "APS_YY_MM_DD"
    pattern: '(\d{2})\.(\d{2})\.(\d{2})\s+(\d{1,2}):(\d{2})\s*(AM|PM)?'
    example: "99.12.25 3:45PM"
    priority: 2
    indicators: ["Kodak", "APS", "Advanced Photo System"]

  - name: "English_Month_Name"
    pattern: '(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})'
    example: "25 December 1999"
    priority: 3

  - name: "Spanish_Month_Name"
    pattern: '(\d{1,2})\s+(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\s+(\d{4})'
    example: "25 Diciembre 1999"
    priority: 3
    language: "es"

  - name: "ISO_8601"
    pattern: '(\d{4})-(\d{2})-(\d{2})'
    example: "1999-12-25"
    priority: 4

# Month name translations
month_names:
  english: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
  spanish: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# APS Film Roll ID Recognition
aps_patterns:
  - name: "Film_Roll_ID"
    pattern: '(ID\s*)?(\d{3})-(\d{3})'
    example: "ID352-419 or 529-901"

  - name: "Frame_Number"
    pattern: '<\s*(?:No\.\s*)?(\d{1,2})\s*>'
    example: "<No. 16> or <10>"

# Location Mapping & Geocoding
locations:
  # Predefined common locations (avoids repeated geocoding API calls)
  known_locations:
    - names: ["Lima", "Peru", "Perú", "Miraflores", "San Isidro"]
      coordinates: [-12.0464, -77.0428]
      timezone: "America/Lima"
      city: "Lima"
      country: "Peru"
      country_code: "PE"

    - names: ["Auckland", "New Zealand", "NZ"]
      coordinates: [-36.8485, 174.7633]
      timezone: "Pacific/Auckland"
      city: "Auckland"
      country: "New Zealand"
      country_code: "NZ"

    - names: ["Wellington", "New Zealand"]
      coordinates: [-41.2865, 174.7762]
      timezone: "Pacific/Auckland"
      city: "Wellington"
      country: "New Zealand"
      country_code: "NZ"

    - names: ["Utrecht", "Netherlands", "Nederland"]
      coordinates: [52.0907, 5.1214]
      timezone: "Europe/Amsterdam"
      city: "Utrecht"
      country: "Netherlands"
      country_code: "NL"

    - names: ["New York", "NYC", "Manhattan"]
      coordinates: [40.7128, -74.0060]
      timezone: "America/New_York"
      city: "New York"
      country: "United States"
      country_code: "US"

    - names: ["San Francisco", "SF"]
      coordinates: [37.7749, -122.4194]
      timezone: "America/Los_Angeles"
      city: "San Francisco"
      country: "United States"
      country_code: "US"

  # Geocoding API (for unknown locations)
  geocoding:
    enabled: true
    provider: "nominatim"  # Free OpenStreetMap geocoding
    cache_file: ".geocoding_cache.json"
    rate_limit_seconds: 1  # Respect Nominatim usage policy
    country_bias: ["PE", "NZ", "NL", "US"]  # Prioritize these countries

# OCR Filtering
ocr_filtering:
  # Ignore these phrases (not useful metadata)
  ignore_phrases:
    - "Kodak Advanced Photo System"
    - "APS"
    - "Professional Photo"
    - "Quality Lab"
    - "Printed in USA"
    - "© Kodak"

  # Minimum text length to consider (filter out noise)
  min_text_length: 3

  # Maximum text length for free text field (prevent giant OCR dumps)
  max_freetext_length: 500

# Filename Analysis
filename_analysis:
  enabled: true
  date_discrepancy_threshold_days: 365  # Flag if OCR date differs by more than 1 year
  extract_date_patterns:
    - pattern: '(\d{4})[-_](\d{2})[-_](\d{2})'
      format: "YYYY-MM-DD"
    - pattern: '(\d{8})'  # YYYYMMDD
      format: "YYYYMMDD"

# Image Quality Assessment
quality_checks:
  # Determine if _b file is useful or just damage/marks
  min_text_density: 0.01  # Minimum ratio of text to image area
  min_distinct_chars: 5    # Must have at least 5 different characters
  max_similar_chars_ratio: 0.8  # If 80%+ same character, likely noise

# Output Format
output:
  proposal_format: "compact"  # or "detailed"
  include_confidence_scores: true
  include_original_ocr_text: true
  group_by_directory: true

# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "fastfoto_ocr.log"
  console: true
  include_timestamps: true
```

## Claude Vision Prompt Template

```python
CLAUDE_VISION_PROMPT = """
You are analyzing the back side of a scanned photograph. Your task is to extract structured information that will be used to update the photo's EXIF metadata.

**Image Context:**
- This is the reverse side of a photograph
- It may contain handwritten notes, printed text from photo labs, or be mostly blank
- Text may be in any orientation (rotated 90°, 180°, 270°, or mixed)
- Text may be in English or Spanish
- Some backs only show damage, marks, or uninformative text

**Extract the following information if present:**

1. **DATES**: Look for dates in these formats:
   - DD/MM/YY or DD/MM/YYYY (e.g., "25/12/99")
   - YYYY/MMM/D HH:MM AM/PM (e.g., "1999/DEC/25 3:45PM") - Kodak APS format
   - YY.MM.DD HH:MM AM/PM (e.g., "99.12.25 3:45PM") - APS format
   - English month names (e.g., "25 December 1999")
   - Spanish month names (e.g., "17 Noviembre 2002")
   - Any other date formats you recognize

2. **FILM ROLL INFORMATION** (if Kodak APS):
   - Roll ID in format NNN-NNN (e.g., "352-419" or "ID529-901")
   - Frame number (e.g., "<No. 16>" or "<10>")

3. **LOCATION INFORMATION**:
   - City names, countries, landmarks, addresses
   - Any geographic references in English or Spanish

4. **FREE TEXT**:
   - Handwritten notes or captions
   - Any descriptive text about the photo content
   - Names, events, or other context
   - EXCLUDE boilerplate like "Kodak Advanced Photo System", "Professional Photo", lab names

5. **IMAGE QUALITY ASSESSMENT**:
   - Is this back side useful? (Has meaningful text vs. just damage/marks)
   - Estimated text orientation(s)
   - Language(s) detected

**Return your analysis as JSON:**
```json
{
  "is_useful": true/false,
  "confidence": 0.0-1.0,
  "dates": [
    {
      "text": "25/12/99",
      "format": "DD/MM/YY",
      "parsed": "1999-12-25",
      "time": null,
      "confidence": 0.95,
      "is_aps": false
    }
  ],
  "aps_info": {
    "roll_id": "352-419",
    "frame_number": 16,
    "confidence": 0.90
  },
  "locations": [
    {
      "text": "Lima, Peru",
      "type": "city_country",
      "confidence": 0.88
    }
  ],
  "free_text": {
    "content": "Family vacation at the beach",
    "language": "en",
    "orientation": 0,
    "confidence": 0.75
  },
  "raw_ocr": "Complete transcription of all text found...",
  "orientations_detected": [0, 90],
  "languages_detected": ["en"]
}
```

**Important:**
- Return ONLY the JSON, no other text
- Use null for missing fields
- Confidence scores: 0.0 (uncertain) to 1.0 (certain)
- Orientations: 0, 90, 180, 270 degrees
- Be conservative with is_useful: true only if there's actionable metadata
- Parse dates carefully considering various formats
- Distinguish between photo dates and development dates if both present
"""
```

## Proposal File Format

**File**: `exif_updates_proposal.txt`

```
================================================================================
FastFoto OCR EXIF Update Proposal
Generated: 2025-11-13 14:30:15
Total files analyzed: 1,247
Useful backs found: 892 (71.5%)
Dates extracted: 756 (84.8%)
Locations extracted: 234 (26.2%)
================================================================================

Directory: /photos/2000/family_vacation/

[001] IMG_5423.jpg (from: IMG_5423_b.jpg) [Confidence: 0.92]
  Current:
    DateTimeOriginal: <not set>
    GPSLatitude: <not set>
    Caption-Abstract: <not set>

  Proposed:
    DateTimeOriginal: 1999-12-25 14:30:00
    OffsetTimeOriginal: +12:00
    GPSLatitude: -36.8485 S
    GPSLongitude: 174.7633 E
    LocationCreatedCity: Auckland
    LocationCreatedCountryName: New Zealand
    LocationCreatedCountryCode: NZ
    Caption-Abstract: Family at beach house
    ImageUniqueID: 352-419
    ImageNumber: 16
    Make: Kodak APS
    UserComment: OCR[0.92]: "352-419 <No. 16> 1999/DEC/25 2:30PM. Family at beach house"

  Warnings: Filename suggests 2001, OCR date is 1999 (730 days difference)
  Source: Handwritten + APS print (English)

[002] IMG_5424.jpg (from: IMG_5424_b.jpg) [Confidence: 0.65]
  Current:
    DateTimeOriginal: 2000-01-01 00:00:00 (filesystem)

  Proposed:
    DateTimeOriginal: 2000-07-17 <no change - low confidence>
    Caption-Abstract: Birthday party

  Warnings: Low confidence date (0.65), handwriting unclear
  Source: Handwritten (English)

[003] IMG_5425.jpg
  Status: No _b file found - skipped

[004] IMG_5426_b.jpg (original: IMG_5426.jpg)
  Status: Not useful (only development lab marks, no informative text)
  Action: Will move to processed/ without EXIF changes

--------------------------------------------------------------------------------
Summary for directory: 4 files processed, 2 updates proposed, 1 skipped, 1 marked not useful
================================================================================
```

## Processing Phases Implementation

### Phase 1: Discovery
```python
def discover_photo_pairs(root_dir, config):
    """
    Recursively scan directory and pair originals with _b files
    Returns: List[PhotoPair]
    """
    pairs = []
    back_files = {}
    originals = []

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in config['files']['input_extensions']:
                continue

            full_path = os.path.join(root, file)

            # Check if it's a back file
            is_back = any(file.endswith(f"{suffix}{ext}")
                         for suffix in config['files']['back_suffixes'])

            if is_back:
                # Find corresponding original
                for suffix in config['files']['back_suffixes']:
                    if file.endswith(f"{suffix}{ext}"):
                        original_name = file[:-len(f"{suffix}{ext}")] + ext
                        back_files[os.path.join(root, original_name)] = full_path
            else:
                originals.append(full_path)

    # Pair them up
    for original in originals:
        back = back_files.get(original)
        pairs.append(PhotoPair(original, back))

    return pairs
```

### Phase 2: Analysis with Multiprocessing

```python
def analyze_batch(photo_pairs, config, num_workers=None):
    """
    Process multiple photos in parallel using multiprocessing
    """
    if num_workers is None:
        num_workers = min(config['processing']['max_workers'],
                         multiprocessing.cpu_count())

    # Sort pairs by file size (larger files first for better load balancing)
    photo_pairs.sort(key=lambda p: os.path.getsize(p.back) if p.back else 0,
                     reverse=True)

    with multiprocessing.Pool(num_workers) as pool:
        results = pool.starmap(
            process_single_photo,
            [(pair, config) for pair in photo_pairs]
        )

    return results
```

### Phase 3: Proposal Generation

```python
def generate_proposal(results, config):
    """
    Create human-readable proposal file
    Update if exists, otherwise create new
    """
    proposal_path = config['files']['proposal_file']

    # Group by directory
    by_directory = {}
    for result in results:
        dir_name = os.path.dirname(result.original)
        if dir_name not in by_directory:
            by_directory[dir_name] = []
        by_directory[dir_name].append(result)

    # Generate formatted output
    output = generate_header(results)

    for directory in sorted(by_directory.keys()):
        output += format_directory_results(directory, by_directory[directory])

    # Write or update
    with open(proposal_path, 'w', encoding='utf-8') as f:
        f.write(output)
```

### Phase 4: Application (with ExifTool)

```python
def apply_updates(proposal_file, config):
    """
    Read approved proposal and apply EXIF updates
    """
    updates = parse_proposal_file(proposal_file)

    for update in updates:
        if not update.approved:
            continue

        try:
            # Read current EXIF
            current = read_exif(update.original_file)

            # Build ExifTool command
            exiftool_args = build_exiftool_args(update, config)

            # Execute update
            result = subprocess.run(
                ['exiftool'] + exiftool_args + [update.original_file],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                log_error(f"Failed to update {update.original_file}: {result.stderr}")
                continue

            # Move _b file to processed/
            if update.back_file:
                move_to_processed(update.back_file, config)

            log_success(f"Updated {update.original_file}")

        except Exception as e:
            log_error(f"Error processing {update.original_file}: {e}")
```

## Hybrid Approach (Cost Optimization)

For budget-conscious processing:

```python
def hybrid_ocr_strategy(image_path, config):
    """
    Try PaddleOCR first, fallback to Claude for complex cases
    """
    # Step 1: Quick PaddleOCR scan
    paddle_result = paddleocr_extract(image_path)

    # Step 2: Assess if PaddleOCR is sufficient
    if (paddle_result.confidence > 0.85 and
        paddle_result.has_machine_print and
        not paddle_result.has_handwriting):
        return paddle_result

    # Step 3: Use Claude for complex cases
    claude_result = claude_vision_extract(image_path, config)
    return claude_result
```

**Cost estimation with hybrid**:
- Assume 40% are machine-print only → use PaddleOCR (free)
- 60% need Claude → 1,800 images × $0.025 = $45
- Total savings: ~40-50%

## Testing Strategy

### Phase 0: Test File Analysis

Before full implementation, analyze sample files:

```python
def analyze_test_set(test_dir, config):
    """
    Non-destructive analysis of test files to refine design
    """
    pairs = discover_photo_pairs(test_dir, config)
    sample_size = min(50, len(pairs))
    samples = random.sample([p for p in pairs if p.back], sample_size)

    findings = {
        'date_formats_found': {},
        'languages_detected': {},
        'orientation_distribution': {},
        'aps_count': 0,
        'handwriting_count': 0,
        'useful_ratio': 0.0,
        'unexpected_patterns': []
    }

    for pair in samples:
        result = claude_vision_extract(pair.back, config)
        update_findings(findings, result)

    # Generate refinement recommendations
    recommendations = generate_recommendations(findings)

    return findings, recommendations
```

## Technology Stack

**Core Language**: Python 3.10+

**Key Libraries**:
- `anthropic` - Claude API client
- `Pillow (PIL)` - Image loading and preprocessing
- `python-magic` - File type detection
- `pyexiftool` - ExifTool Python wrapper
- `pyyaml` - Configuration file parsing
- `python-dateutil` - Date parsing flexibility
- `geopy` - Geocoding for Nominatim
- `tqdm` - Progress bars
- `colorama` - Terminal colors
- `pytest` - Testing framework

**External Tools**:
- `exiftool` - EXIF metadata manipulation (must be installed)

**Optional**:
- `paddleocr` - For hybrid cost optimization
- `opencv-python` - Advanced image preprocessing

## Installation Requirements

```bash
# macOS
brew install exiftool

# Linux (Debian/Ubuntu)
apt-get install libimage-exiftool-perl

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install anthropic pillow python-magic pyexiftool pyyaml python-dateutil geopy tqdm colorama

# Optional for hybrid mode
pip install paddlepaddle paddleocr opencv-python
```

## CLI Interface Design

```bash
# Discovery and analysis (non-destructive)
fastfoto-ocr analyze /path/to/photos --config config.yaml

# Re-run analysis with updated configuration
fastfoto-ocr analyze /path/to/photos --update-proposal

# Apply approved changes
fastfoto-ocr apply /path/to/photos --proposal exif_updates_proposal.txt

# Test file analysis (before full implementation)
fastfoto-ocr test-analyze /path/to/photos --sample-size 50

# Dry run (show what would be done without doing it)
fastfoto-ocr apply /path/to/photos --dry-run

# Process single file for debugging
fastfoto-ocr process-one IMG_5423_b.jpg --debug
```

## Next Steps

1. **User Clarification**: Answer questions in RESEARCH_FINDINGS.md
2. **Test File Analysis**: Run Phase 0 on sample directory
3. **Configuration Refinement**: Update config.yaml based on real data
4. **Prototype**: Build MVP with core OCR → EXIF flow
5. **Iteration**: Refine prompts and parsing logic
6. **Full Implementation**: Complete all features
7. **Validation**: Process test set and review results
8. **Production Run**: Process full 2000-3000 photo collection

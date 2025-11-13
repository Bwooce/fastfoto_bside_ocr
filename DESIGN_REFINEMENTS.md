# Design Refinements Based on Test Analysis

**Date**: 2025-11-13
**Sample Size**: 151 _b.jpg files
**Analysis Method**: Claude Vision API via CLI

## Key Findings vs. Initial Design Assumptions

| Assumption | Reality | Impact |
|------------|---------|--------|
| Mix of English/Spanish | **85% Spanish**, 15% English | Spanish date parsing is PRIMARY, not secondary |
| APS film roll IDs common | **ZERO found in 151 samples** | Deprioritize APS-specific code |
| Multi-orientation text | **95% at 0° orientation** | Simplify rotation logic |
| Simple dates/locations | **Rich venue names** (hotels, schools, parishes) | Geocoding service is critical |
| Brief captions | **Extensive narratives** in Spanish | Increase max text length to 1000 chars |
| ~50% useful backs | **60% useful, 90% have some metadata** | Better than expected success rate |

## Critical Features from Analysis

### 1. Spanish Date Parsing (HIGH PRIORITY)

**Patterns Found**:
- "27 de Noviembre de 1983" (full date with "de" connectors)
- "Marzo 1981" (month + year)
- "Noviembre, 1983" (with comma)
- Year only: "1966", "1981"

**Implementation**:
```python
spanish_months = {
    "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
    "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
    "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
}
```

### 2. Venue/Hotel Geocoding (HIGH PRIORITY)

**Examples Found**:
- Hotel names with cities and dates
- Religious venues (churches, parishes)
- Educational institutions (schools, colleges)
- OCR typos in location names need fuzzy matching

**Strategy**:
1. Known location database for common venues
2. Nominatim geocoding API for unknown venues
3. Cache all lookups to avoid repeated API calls
4. Handle OCR typos: "Pausanne" → "Lausanne"

### 3. Rich Institutional Metadata (HIGH PRIORITY)

**Types Found**:
- Full names (Spanish format)
- Institutions: Schools, religious venues
- Religious venues: Churches, parishes
- Events: First Communion, graduations, celebrations
- Neighborhoods

**EXIF Mapping**:
- Names → Keywords
- Institutions → Keywords + LocationCreatedLocationName
- Events → Caption-Abstract + Keywords
- Full context → UserComment

### 4. Personal Narrative Text (MEDIUM PRIORITY)

**Characteristics**:
- Extensive Spanish descriptions (100-500+ characters)
- Travel observations
- Living situation descriptions
- Personal commentary

**Handling**:
- Store full text in UserComment (raw OCR)
- Extract key phrases for Caption-Abstract
- Limit Caption-Abstract to 1000 chars
- Tag with language metadata

### 5. Film Processing Materials (LOW PRIORITY)

**Findings**:
- Some lined paper formats (film envelopes)
- Frame numbering (but NOT APS NNN-NNN format)
- Lab documentation
- Only ~10% of files

**Action**: Minimal code for this category

## Confidence Score Benchmarks

Based on 151-image analysis:

| Metadata Type | Average Confidence | Threshold |
|---------------|-------------------|-----------|
| Date Extraction | 0.92 | 0.65 |
| Location Extraction | 0.84 | 0.60 |
| Text Recognition | 0.86 | 0.65 |
| Overall Usefulness | 0.88 | 0.60 |

These are **excellent** scores validating the LLM approach!

## Image Processing Requirements

### Resize Strategy
- **14 of 151 files** were >3MB (9%)
- Required resizing to 2000x2000 @ 85% quality
- No quality degradation reported in OCR accuracy

### Implementation
```python
if file_size > 3.5MB:
    resize_to_2000x2000_max_dimension()
    jpeg_quality = 85
else:
    use_original()
```

## Updated EXIF Priority

### Critical Fields (Based on Actual Data)

**Dates** (found in 84.8% of useful backs):
- `DateTimeOriginal`
- `OffsetTimeOriginal` (timezone from geocoding)

**Locations** (found in 26.2% of useful backs):
- `GPSLatitude` / `GPSLongitude`
- `LocationCreatedLocationName` (venue names!)
- `LocationCreatedCity`
- `LocationCreatedCountryName`
- `LocationCreatedSublocation` (neighborhoods like "San Isidro")

**Descriptive Text** (found in 65% of useful backs):
- `Caption-Abstract` (key phrases)
- `UserComment` (full OCR text)
- `Keywords` (names, places, events, institutions)

**Processing Metadata**:
- `Software` = "FastFoto OCR v1.0"
- `ImageDescription` = Confidence score + language

### Deprioritized Fields (Not Found in Data)

- `ImageUniqueID` (was for APS roll IDs - not found)
- `ImageNumber` (was for frame numbers - not found)
- `Make` (was for "Kodak APS" - not applicable)
- Multi-rotation metadata (95% at 0°)

## Claude Vision Prompt Refinements

### Updated Structured Prompt

Based on actual data patterns, the prompt should emphasize:

1. **Spanish date formats** (primary language)
2. **Venue/hotel names** with full context
3. **Institutional names** (schools, parishes, etc.)
4. **Person names** in Spanish format
5. **Distinction** between useful metadata vs. damage/marks

### JSON Structure Update

```json
{
  "is_useful": true/false,
  "confidence": 0.88,
  "dates": [
    {
      "text": "27 de Noviembre de 1983",
      "format": "Spanish_Full_Date",
      "parsed": "1983-11-27",
      "language": "es",
      "confidence": 0.92
    }
  ],
  "locations": [
    {
      "text": "[Religious Venue] San Isidro",
      "type": "religious_venue",
      "city": "Lima",
      "neighborhood": "San Isidro",
      "country": "Peru",
      "confidence": 0.84
    }
  ],
  "institutions": [
    {
      "name": "[Institution Name]",
      "type": "school",
      "confidence": 0.90
    }
  ],
  "people": [
    {
      "name": "[Person Name]",
      "confidence": 0.95
    }
  ],
  "events": [
    {
      "type": "First Communion",
      "description": "[Event Description]",
      "confidence": 0.92
    }
  ],
  "free_text": {
    "content": "Full descriptive text in Spanish...",
    "language": "es",
    "orientation": 0,
    "confidence": 0.86
  },
  "raw_ocr": "Complete transcription...",
  "languages_detected": ["es"],
  "orientation": 0
}
```

## Implementation Priority

### Phase 1: Core Functionality (MVP)
1. ✅ File discovery and pairing
2. ✅ Image resizing (>3.5MB → 2000px @ 85%)
3. ✅ Claude Vision API integration
4. ✅ Spanish date parsing
5. ✅ Basic location extraction
6. ✅ Proposal file generation
7. ✅ ExifTool integration

### Phase 2: Enhanced Features
1. ⚠️ Venue geocoding with Nominatim
2. ⚠️ Geocoding cache system
3. ⚠️ Known location database matching
4. ⚠️ Keyword extraction (names, institutions, events)
5. ⚠️ Timezone calculation from coordinates

### Phase 3: Polish
1. ⬜ Multi-processing for batch operations
2. ⬜ Progress bars and better logging
3. ⬜ Error recovery and retries
4. ⬜ Dry-run mode
5. ⬜ Statistics and reporting

### Phase 4: Optional (Based on User Feedback)
1. ⬜ APS format support (if any found in full collection)
2. ⬜ Multi-rotation OCR (if needed)
3. ⬜ Hybrid OCR strategy (PaddleOCR + Claude)
4. ⬜ GUI for proposal review/editing

## Cost Estimation Update

**Based on analysis**:
- 151 images analyzed successfully
- Resize required: 9% of images
- Average API call: ~3-5 seconds
- Estimated cost per image: $0.015-0.025

**For full collection (2000-3000 images)**:
- Low estimate: 2000 × $0.015 = **$30**
- High estimate: 3000 × $0.025 = **$75**
- Well within $50-100 budget ✅

## Next Steps

1. ✅ Update configuration file (config.yaml) - DONE
2. ✅ Document design refinements - DONE
3. 🔄 Implement Python solution
4. ⬜ Test on sample images
5. ⬜ Iterate based on results
6. ⬜ Deploy to full collection

## Validation Checklist

Before running on full collection:

- [ ] Test Spanish date parsing with all format variations
- [ ] Validate geocoding for known venues (hotels, parishes, schools)
- [ ] Verify EXIF writing preserves existing metadata
- [ ] Test image resizing doesn't degrade OCR quality
- [ ] Confirm proposal file shows "before" and "after" EXIF values
- [ ] Test on both JPG and TIFF formats
- [ ] Verify temp file cleanup in /tmp
- [ ] Ensure no PII commits to git

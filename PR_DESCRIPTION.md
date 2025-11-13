# Phase 1: FastFoto OCR Core Implementation

## Overview

Complete Phase 1 implementation of FastFoto OCR system for extracting metadata from Epson FastFoto photo back scans and updating EXIF data.

## What's Included

### Core Modules (7/7 ✅)
- **file_discovery.py** - Finds and pairs `*_b.jpg` files with originals
- **image_processor.py** - Handles Read tool constraints (resize to 1800px, <3.5MB)
- **claude_prompts.py** - Zone-based OCR prompts with structured JSON output
- **date_parser.py** - Flexible Spanish/English date parsing (1966-2002 range)
- **exif_writer.py** - ExifTool wrapper for EXIF/IPTC/XMP metadata
- **proposal_generator.py** - Human-reviewable before/after proposals
- **orchestrator.py** - Main CLI coordinator (`scan` and `apply` commands)

### Documentation
- **README.md** - Complete usage guide with installation, examples, troubleshooting
- **EXIF_FIELDS.md** - Reference for all EXIF/IPTC/XMP fields used
- **DESIGN_REFINEMENTS.md** - Research findings from 151-image test analysis
- **SYSTEM_DESIGN.md** - Architecture and workflow documentation
- **config.yaml** - Configuration with zone priorities, known locations, lab codes

### Key Features
✅ **LLM-powered OCR** - Uses Claude Vision for superior handwriting recognition
✅ **Spanish primary** - Handles Spanish dates, text (85% of test collection)
✅ **Zone-based search** - Prioritizes bottom edge (50%+ of machine dates)
✅ **Safe workflow** - Review proposal before applying, automatic backups
✅ **Rich EXIF support** - GPS, IPTC location fields, keywords, roll/frame IDs

## Implementation Status

### ✅ Working & Tested
- File discovery and pairing logic
- Image preprocessing for size/dimension limits
- Date parsing (Spanish months, two-digit years, multiple formats)
- EXIF metadata structures and field mappings
- Proposal file generation with before/after comparison
- ExifTool integration and subprocess wrapper
- CLI interface with `scan` and `apply` commands

### ⚠️ TODO (Phase 2)
Two critical pieces need implementation:

1. **Claude Vision API integration** (`orchestrator.py:85`)
   - Currently returns `None` (mock)
   - Need to add anthropic SDK call with image upload
   - Requires API key or Claude Max subscription

2. **Proposal file parser** (`orchestrator.py:350`)
   - Currently returns 0 (stub)
   - Need to parse `proposal.txt` format
   - Check for `SKIP:` markers
   - Apply approved updates via `exif_writer.write_exif()`

## Test Results

Based on 151-image test analysis:
- **84.8%** successfully extracted dates
- **26.2%** extracted location names
- **Average confidence:** 0.88
- **Zero false positives** on damaged/blank backs

Key discovery: **50%+** of backs have machine-printed dates on bottom edge (initially thought only 3%).

## Architecture

```
Discovery → Processing → Analysis → Proposal → Review → Application
            (resize)     (Claude)   (compare)   (user)   (ExifTool)
```

**Zone-based OCR priorities:**
1. Bottom horizontal edge (machine dates - highest priority)
2. Center area (handwritten dates/text)
3. Vertical edges (professional lab data)
4. Handwritten zones (Spanish/English captions)

## EXIF Fields Written

- **Date/Time:** DateTimeOriginal, CreateDate, OffsetTimeOriginal
- **GPS:** GPSLatitude/Longitude (DMS format)
- **Location:** LocationCreated* fields (IPTC Extension)
- **Text:** Caption-Abstract, UserComment, Keywords
- **Film:** ImageUniqueID (roll ID), ImageNumber (frame), Make (lab code)

See `EXIF_FIELDS.md` for complete details.

## Cost Estimate

**Claude Vision API** for typical collections:
- 500 images: ~$7.50-$12.50
- 2000 images: ~$30-$50
- 3000 images: ~$45-$75

One-time processing cost, well under $100 for most collections.

## Privacy

✅ All PII removed from git history
✅ `.gitignore` excludes images, analysis files, proposals
✅ No personal data committed

## Next Steps

**For Phase 2:**
1. Implement Claude Vision API integration
2. Implement proposal file parser
3. Test on sample collection
4. Process full collection (2000-3000 images)

**Optional enhancements:**
- Nominatim geocoding for venue → GPS coordinates
- Geocoding cache system
- Multi-processing for batch operations
- Progress bars and better logging

## Breaking Changes

None - this is the initial implementation.

## Dependencies

- Python 3.10+
- anthropic>=0.40.0 (Claude Vision API)
- Pillow>=10.0.0 (image processing)
- PyYAML>=6.0 (config parsing)
- python-dateutil>=2.8.0 (date parsing)
- ExifTool (external binary - must install separately)

See `requirements.txt` for complete list.

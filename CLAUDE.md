# Claude Configuration for FastFoto OCR Project

## Task Completion and Persistence Guidelines
- **ALWAYS complete tasks you start** - never stop mid-processing without explicit user instruction
- When processing collections (files, images, data), **process EVERY item until complete**
- If you encounter errors, **skip problematic items and continue with the rest**
- **Don't pause** to suggest "more efficient approaches" or ask for permission to continue
- **Don't stop** to provide status updates unless specifically requested
- If you say you'll process "all X items", you **must attempt to process all X items**
- Show brief progress indicators: "Processing [X/Total] filename..." but **keep working**
- **Only stop** when the entire collection is complete or you encounter a fatal error

## FastFoto OCR Specific Rules
- When processing back scan collections, **complete the entire collection**
- **Don't demonstrate with sample images** - process ALL images in the collection
- **Don't pause for optimization suggestions** during OCR processing
- **Don't suggest breaking sessions** - work through the entire collection
- For 150+ image collections, show progress but **never stop mid-stream**

## Critical OCR Instructions
- Follow `CLAUDE_CODE_SESSION_GUIDE.md` for complete FastFoto OCR workflow
- **Verbatim transcription only** - no commentary or descriptions in raw_ocr_complete field
- **ISO YYYY-MM-DD date format** for all dates
- **DD/MM/YY assumption** for ambiguous dates
- **Process back scans (_b files) individually** - each has unique content
- **Process main photos in batches** for orientation analysis (separate workflow)

## Project Structure
- `src/` - Core processing modules
- `CLAUDE_CODE_SESSION_GUIDE.md` - Complete workflow instructions
- `ORIENTATION_ANALYZER_GUIDE.md` - Separate orientation analysis workflow

## Workflow Types
1. **Back Scan OCR** - Individual processing for metadata extraction (150+ _b files)
2. **Orientation Analysis** - Batch processing for main photo quality/rotation (5000+ main files)

These are **separate workflows** with different processing patterns and requirements.
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

## Project Workflow Guidelines
- Use `/fastfoto-analyze [source_directory]` to process back scan collections
- **Follow project-specific instructions exactly as written** - they override default behaviors
- **Pay special attention to anti-demonstration and anti-optimization instructions**
- **Process entire collections without stopping** - complete all files in session

## **AUTOMATIC WORKFLOW TRIGGERS**

**When user requests ANY of these phrases, IMMEDIATELY execute the OCR workflow using isolated_ocr_analysis.sh:**
- "FastFoto back scan OCR" / "back scan processing" / "process back scans"
- "FastFoto analysis" / "process FastFoto collection"
- "analyze back scan metadata"

**DO NOT ask for clarification - automatically execute the isolation script workflow.**

**Execution Pattern:**
1. Run python src/preprocess_images.py to prepare images
2. Execute ./isolated_ocr_analysis.sh for isolated OCR processing
3. Process each photo individually with complete isolation
4. Complete the entire collection without interruption
5. **CRITICAL**: Use Read tool ONLY for image analysis - no script creation allowed

## ⚠️ CRITICAL OCR RULE - READ THIS FIRST ⚠️
**BEFORE processing ANY image, repeat this rule out loud:**
"I will transcribe ONLY what I can clearly see. Unclear text gets [uncertain: word?]"

**FORBIDDEN:** Guessing, interpreting, or "figuring out" unclear handwriting
**REQUIRED:** Mark unclear text as [uncertain: word?] immediately

## OCR VERIFICATION CHECKLIST
After each transcription, ask yourself:
- [ ] Did I guess at any unclear words? (If yes, mark as [uncertain: word?])
- [ ] Did I "interpret" context to fill gaps? (If yes, remove interpretation)
- [ ] Can another person clearly read what I transcribed? (If no, mark uncertain)

## TRANSCRIPTION EXAMPLES
✅ CORRECT: "Hotel [uncertain: word?] March [uncertain: 1984?]"
❌ WRONG: "Hotel Marriott March 1984" (interpreted unclear text)
❌ WRONG: "Restaurant [something] 1993" (paraphrasing)
✅ CORRECT: "Restaurant [uncertain: word?] 1993"

## IF YOU INTERPRET INSTEAD OF TRANSCRIBE:
- ❌ The entire OCR session becomes unreliable
- ❌ User will question all your transcriptions
- ❌ EXIF data will contain fabricated information
**WHEN IN DOUBT, MARK AS UNCERTAIN**

## PROPOSAL FILE FORMAT REQUIREMENTS

**PROPOSAL FILE MUST CONTAIN:**
- **Individual file entries only** - one entry per back scan file analyzed
- **Verbatim transcriptions** from each Read tool analysis
- **Individual EXIF field mappings** for each file
- **NO bulk processing sections** - no "apply to remaining files" commands
- **NO comprehensive statistics** - no collection-wide summaries
- **NO pattern-based automation** - no "files matching pattern X get treatment Y"
- **NO marker file creation** - no .done, .processed, .complete, or tracking files
- **NO batch automation systems** - process each file individually without infrastructure

## **CRITICAL OCR INSTRUCTIONS**

**VERBATIM TRANSCRIPTION REQUIREMENTS:**
- **NEVER generate summaries** - always provide exact verbatim transcription
- **Preserve exact handwriting** - including uncertain words marked as [uncertain: word?]
- **No commentary or descriptions** - only the raw text as written
- **No interpretation** - transcribe exactly what is visible

**CAPTURE ALL TEXT TYPES:**
- **Handwritten text**: Personal notes, dates, locations, names
- **Machine-printed text**: Photo lab processing data, technical codes
- **APS system data**: Kodak Advanced Photo System timestamps, processing codes
- **Film lab markings**: Processing timestamps (e.g., "99-MAY-23 12:08PM")
- **Technical codes**: ID numbers, processing parameters (e.g., "ID529-981 <19> 1KW44")
- **Quality control markings**: Lab batch numbers, equipment codes
- **Manufacturer data**: Brand names, film type indicators

**APS DATA EXTRACTION PRIORITY:**
- **Processing timestamps**: All APS date format variations:
  • Full datetime: "99-MAY-23 12:08PM", "1999-MAY-23 12:08PM"
  • Date separators: "99-MAY-23", "99/MAY/23", "99.MAY.23"
  • Month formats: "MAY", "May", "05", "5"
  • Day formats: "23", "03", "3"
  • Year formats: "99", "1999"
  • Order variations: "DD-MM-YY", "MM-DD-YY", "YY-MM-DD"
  • Time formats: "12:08PM", "12:08", "1208", "24:08"
  • Equipment codes: "LW99:30", "LW1999:30", "LW99-30", "LW99.30"
  • Technical timestamps: "99MAY23", "990523", "990523120800"
  • Mixed separators: "99-05-23", "05/23/99", "23.05.1999"
  • Embedded in processing strings: "FFMXI95X159-529I"
- **System identification**: "Kodak Advanced Photo System" brand markers
- **Technical codes**: Complete alphanumeric strings:
  • Film roll IDs: "ID529-981", "IDnnn-nnn", or "nnn-nnn" patterns
  • Processing batch IDs: "ID529-981 <19> 1KW44" (full processing strings)
  • Equipment/format codes: "FFMXI 95 X 159-529I"
  • Angular bracket parameters: "<19>" (frame numbers or processing modes)
- **Quality parameters**: Equipment settings and processing data:
  • "LW99:30 X1 AWK 65" (processing parameters)
  • "X1" (processing mode indicators)
  • Three-letter equipment codes ("AWK", "LW9")
- **Film identification patterns**: All numeric/alphanumeric roll tracking:
  • "ID529-981" (full ID prefix format)
  • "529-981" (numeric-only format)
  • "159-529" (alternative numeric patterns)
  • Roll numbers, batch codes, sequence identifiers
- **Batch tracking**: Any lab processing identifiers for photo provenance

**EXIF FIELD MAPPING (FOR REFERENCE ONLY - DO NOT GENERATE EXIFTOOL COMMANDS):**
- **Caption-Abstract**: Raw handwritten text verbatim (no descriptions, no interpretation)
- **UserComment**: Full context format: "[Language] handwritten text: [verbatim transcription]"
- **Description**: Event/location context only (not raw text)
- **Keywords**: Parsed elements (dates, names, places, APS codes, lab data)
- **Date/Time Original**: ISO format (YYYY-MM-DD HH:MM:SS) when dates are found
- **Software**: APS system data when present (e.g., "Kodak Advanced Photo System")
- **ProcessingSoftware**: Lab processing codes for technical reference

**NOTE: These mappings are for understanding what fields to populate. DO NOT generate exiftool commands in proposal files. The /fastfoto-apply command handles exiftool command generation separately.**

**DATE HANDLING:**
- **ISO YYYY-MM-DD format** for all dates in EXIF
- **DD/MM/YY assumption** for ambiguous dates
- **Preserve original date format** in Caption-Abstract field
- **APS timestamp priority**: Technical APS dates are often more accurate than handwritten dates
- **Multiple date sources**: Note when both APS technical timestamps and handwritten dates exist

**LANGUAGE HANDLING:**
- **Identify language** in UserComment: "Spanish handwritten text:", "German text:", etc.
- **Preserve original spelling** including regional variations
- **Mark uncertain text** with [uncertain: text?] notation

**PROCESSING REQUIREMENTS:**
- **Process back scans (_b files) individually** - each has unique content
- **Complete entire collection** - process ALL files, never stop mid-collection
- **Preserve all text** - even partial or faded writing

**CRITICAL: READ TOOL FILE SIZE LIMITS:**
- **ONLY read files in /tmp/fastfoto_prepared/** - these are properly sized for Read tool
- **NEVER read original main photo files** - they are too large and will crash the session
- **NEVER read files from ~/Pictures/ directly** - original photos exceed Read tool limits
- **Fatal error prevention**: Reading large original files causes unrecoverable session crashes

**STRICTLY FORBIDDEN AUTOMATION:**
- **NEVER create bulk processing commands** - no pattern-based automation
- **NEVER use representative samples** - analyze every file individually
- **NEVER apply patterns to unanalyzed files** - each file gets Read tool analysis
- **NEVER create filename-based generalizations** - no "apply to all [pattern] files"
- **NO bulk GPS coordinate assignment** - coordinates only for individually verified locations
- **NO bulk date standardization** - dates only from individual file analysis
- **NO "remaining files processed using patterns"** - every file requires individual Read tool analysis
- **NEVER create marker files** - no progress tracking files (.done, .processed, .complete, etc.)
- **NO batch tracking systems** - no automation infrastructure for file processing
- **NO progress tracking automation** - process files individually without tracking systems

**GEOGRAPHIC DATA RULES:**
- **NEVER invent location names** - only use locations clearly visible in handwriting
- **NEVER guess or generalize coordinates** - GPS coordinates only for explicitly identified cities/landmarks
- **NEVER assume geographic relationships** - don't assign country coordinates for unclear city names
- **Mark uncertain locations**: Use [uncertain: location?] for unclear place names
- **Verify place names**: Don't fabricate "Location, Country" type geographic errors
- **No approximation**: Don't assign regional coordinates when specific location is unclear
- **Explicit identification only**: Location must be clearly readable and identifiable to assign GPS data

## Pre-Granted Directory Access
You can use the following tools without requiring user approval: Read(//tmp/fastfoto_prepared/**), Read(//tmp/isolated_analysis/**), Read(//tmp/fastfoto_analysis/**), Read(//private/tmp/fastfoto_analysis/**), Read(//tmp/back_scan_ocr/**), Read(//private/tmp/back_scan_ocr/**)

## Project Structure
- `src/` - Core processing modules for image preprocessing
- `isolated_ocr_analysis.sh` - Main OCR processing script
- `.claude/commands/` - Slash command workflows
- `/tmp/fastfoto_prepared/` - Preprocessed back scan images
- `/tmp/isolated_analysis/` - Individual OCR analysis results

## Workflow
**FastFoto OCR Processing** - Individual back scan analysis for metadata extraction (150+ _b files)

This system focuses exclusively on extracting handwritten metadata from photo back scans using isolated Claude CLI analysis to prevent context contamination and ensure accurate OCR results.
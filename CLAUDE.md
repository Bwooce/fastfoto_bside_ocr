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
- Follow `CLAUDE_CODE_SESSION_GUIDE.md` for complete FastFoto OCR workflow instructions
- **Follow project-specific instructions exactly as written** - they override default behaviors
- **Pay special attention to anti-demonstration and anti-optimization instructions**
- **Project guides specify complete processing requirements vs. sample demonstrations**

## **AUTOMATIC WORKFLOW TRIGGERS**

**When user requests ANY of these phrases, IMMEDIATELY read and execute `ORIENTATION_ANALYZER_GUIDE.md`:**
- "FastFoto orientation analysis" / "analyze orientation"
- "FastFoto back scan OCR" / "back scan processing" / "process back scans"
- "FastFoto analysis" / "process FastFoto collection"
- "analyze main photos" + "back scan metadata"

**DO NOT ask for clarification - automatically execute the documented Task tool commands from the guide.**

**Execution Pattern:**
1. Read ORIENTATION_ANALYZER_GUIDE.md
2. Use Task tool with model="haiku" and the exact phrases from the guide
3. Execute automatically without asking permission
4. Complete the entire workflow as documented
5. **CRITICAL**: Task agents must use Read tool ONLY - no script creation allowed

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
- **Processing timestamps**: All format variations found in collection:
  • "99-MAY-23 12:08PM" (full datetime stamps)
  • "LW99:30" (equipment/time codes)
  • Date codes embedded in technical strings
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

**EXIF FIELD MAPPING:**
- **Caption-Abstract**: Raw handwritten text verbatim (no descriptions, no interpretation)
- **UserComment**: Full context format: "[Language] handwritten text: [verbatim transcription]"
- **Description**: Event/location context only (not raw text)
- **Keywords**: Parsed elements (dates, names, places, APS codes, lab data)
- **Date/Time Original**: ISO format (YYYY-MM-DD HH:MM:SS) when dates are found
- **Software**: APS system data when present (e.g., "Kodak Advanced Photo System")
- **ProcessingSoftware**: Lab processing codes for technical reference

**DATE HANDLING:**
- **ISO YYYY-MM-DD format** for all dates in EXIF
- **DD/MM/YY assumption** for ambiguous dates
- **Preserve original date format** in Caption-Abstract field

**LANGUAGE HANDLING:**
- **Identify language** in UserComment: "Spanish handwritten text:", "German text:", etc.
- **Preserve original spelling** including regional variations
- **Mark uncertain text** with [uncertain: text?] notation

**PROCESSING REQUIREMENTS:**
- **Process back scans (_b files) individually** - each has unique content
- **Complete entire collection** - process ALL files, never stop mid-collection
- **Preserve all text** - even partial or faded writing
- **Process main photos in batches** for orientation analysis (separate workflow)

**GEOGRAPHIC DATA RULES:**
- **NEVER invent location names** - only use locations clearly visible in handwriting
- **NEVER assume geographic relationships** - don't assign coordinates unless location is explicit
- **Mark uncertain locations**: Use [uncertain: location?] for unclear place names
- **Verify place names**: Don't fabricate "Lock Haren, Netherlands" type errors

## Pre-Granted Directory Access
You can use the following tools without requiring user approval: Read(//tmp/orientation_analysis/**), Read(//private/tmp/orientation_analysis/**), Read(//tmp/fastfoto_analysis/**), Read(//private/tmp/fastfoto_analysis/**), Read(//tmp/back_scan_ocr/**), Read(//private/tmp/back_scan_ocr/**)

## Project Structure
- `src/` - Core processing modules
- `CLAUDE_CODE_SESSION_GUIDE.md` - Complete workflow instructions
- `ORIENTATION_ANALYZER_GUIDE.md` - Separate orientation analysis workflow

## Workflow Types
1. **Back Scan OCR** - Individual processing for metadata extraction (150+ _b files)
2. **Orientation Analysis** - Batch processing for main photo quality/rotation (5000+ main files)

These are **separate workflows** with different processing patterns and requirements.

## ⚠️ **CRITICAL: Orientation Analysis Instructions**

When user requests: **"Analyze orientation of main FastFoto photos with verification checkpoints"**

**DO THIS IMMEDIATELY - USE TASK TOOL FOR BATCH PROCESSING:**
Use Task tool with:
- subagent_type="general-purpose"
- model="haiku"
- Include downsampling to 300px for Read tool compatibility
- Verify: "Do people look upright? Does the scene make visual sense when displayed?"
- Process in batches of 50 max with verification checkpoints

**DO NOT:**
- ❌ Create project overview documents
- ❌ Use Explore tool to understand codebase
- ❌ Write new scripts or code
- ❌ Set up todo lists for exploration

**The tool already exists and works! See ORIENTATION_ANALYZER_GUIDE.md for details.**
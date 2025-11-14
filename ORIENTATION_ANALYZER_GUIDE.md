# FastFoto Analysis - Task Tool Instructions

## 🚨 **TASK TOOL AGENTS: READ THIS FIRST**

**MANDATORY: Use model="haiku" and Read tool ONLY. NO script creation allowed.**

**ABSOLUTELY FORBIDDEN:**
- Creating ANY bash scripts, Python files, or automation tools
- Creating comprehensive reports, summaries, or implementation guides
- Using sampling or pattern-based extrapolation
- Creating multiple output files

**REQUIRED: USE SLASH COMMANDS ONLY - NO CUSTOM AUTOMATION**

## ⚠️ **USE TASK TOOL ONLY - NO CODE WRITING**

This guide provides exact phrases for FastFoto analysis using Claude Code's Task tool with Read tool integration.

---

## 🔄 **Orientation Analysis**

When a user requests orientation analysis, use this **exact phrase**:

```
"CRITICAL: Use existing batch script ONLY - NO custom automation, NO Read tool scripts allowed. Run: python batch_orientation_analysis.py to analyze ALL main photos for orientation issues. The batch script handles Read tool integration internally and processes files systematically. MANDATORY: Use the tested workflow only, no custom approaches or sampling. OUTPUT: Batch script generates orientation analysis results as designed. NEVER create ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, custom JSON files, or any documentation files. Use batch_orientation_analysis.py exclusively."
```

**What this does:**
- Uses tested batch script with built-in Read tool integration
- Processes all main photos systematically for orientation analysis
- Identifies actual orientation problems (upside down, sideways photos)
- Generates orientation analysis results per script design

**Expected findings:**
- Photos with people upside down (180° rotation needed)
- Landscape photos in portrait orientation (90° rotation needed)
- Portrait photos in landscape orientation (90° rotation needed)
- Sideways group photos (90° counter-clockwise rotation needed)

---

## 📝 **Back Scan OCR Processing**

When a user requests back scan metadata extraction, use this **exact phrase**:

```
"CRITICAL: Use /fastfoto slash command ONLY - NO custom automation, NO scripts allowed. The slash command uses Read tool directly for individual back scan analysis. MANDATORY: Process files individually using Read tool for verbatim OCR transcription. OUTPUT: Individual EXIF metadata updates based on real handwritten text extraction. NEVER create comprehensive reports, ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, or automation files. Use /fastfoto slash command exclusively."
```

**What this does:**
- Auto-discovers all back scan (_b.jpg) files in the prepared directory
- Uses Read tool for verbatim OCR text transcription in small batches
- Provides exact handwritten text with no interpretation or summaries
- Identifies language and preserves original spelling/formatting
- Maps raw text to proper EXIF fields (Caption-Abstract, UserComment, Description)
- Supports multilingual text (Spanish, German, English) with language tagging
- Generates precise JSON proposals for EXIF metadata updates

**Expected findings:**
- Multiple photos with verbatim text transcriptions
- Raw handwritten text in multiple languages (Spanish, German, English)
- Exact date notations: "May 80", "March 1981", "July 28 1988"
- Location names as written: "City names", "Hotel names", "Place names"
- People names: Common first names found in handwriting
- Event descriptions: "Birthday", "Quinceañera", "Graduation"
- Language-tagged EXIF fields with preserved original spelling

---

## 🔧 **Combined Analysis**

For complete FastFoto processing, use this **exact phrase**:

```
"CRITICAL: Use slash commands ONLY - NO custom automation allowed. Step 1: Run /fastfoto-orientation for visual orientation analysis of main photos. Step 2: Run /fastfoto for back scan OCR processing using Read tool directly. MANDATORY: Use slash commands only, no custom scripts or batch processing. Commands use Read tool internally for individual file analysis. OUTPUT: Real visual orientation assessment AND individual EXIF metadata updates based on verbatim text extraction. NEVER create ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, FASTFOTO_ANALYSIS_SUMMARY.txt, or comprehensive reports. Use slash commands exclusively."
```

---

## ❌ **NEVER DO THIS - TASK TOOL VIOLATIONS:**

- ❌ **NEVER** create bash scripts (`/tmp/process_*.sh`, `/tmp/*.py`)
- ❌ **NEVER** use subprocess.run() or shell commands for automation
- ❌ **NEVER** create custom automation pipelines or processing tools
- ❌ **NEVER** generate any script files whatsoever
- ❌ **NEVER** use bash for image analysis or batch processing
- ❌ **NEVER** create loop-based file processing scripts
- ❌ **NEVER** write custom Read tool automation scripts
- ❌ **NEVER** use direct Read tool calls in Task tool sessions
- ❌ **NEVER** create comprehensive reports (`ANALYSIS_SUMMARY.txt`, `QUICK_REFERENCE_IMPLEMENTATION.txt`, `FASTFOTO_ANALYSIS_SUMMARY.txt`)
- ❌ **NEVER** generate action plans, implementation guides, or summary documents
- ❌ **NEVER** create multiple documentation files
- ❌ **NEVER** use sampling, pattern extrapolation, or representative analysis
- ❌ **NEVER** stop processing before using documented scripts completely
- ❌ **NEVER** create custom .txt files (EXCEPTION: orchestrator.py generates approved proposal.txt files)

**TASK TOOL AGENTS: Use orchestrator.py and batch scripts ONLY. Let scripts create their designed outputs. Creating custom automation or Read tool scripts violates constraints!**

## ✅ **ALWAYS DO THIS - USE SLASH COMMANDS:**

- ✅ **Use /fastfoto exclusively** for back scan OCR processing
- ✅ **Use /fastfoto-orientation** for orientation analysis with Read tool
- ✅ **Process files individually** with Read tool - no batch automation
- ✅ **Extract verbatim text only** - no comprehensive reports or summaries
- ✅ **Use Read tool directly** - no scripts or simulation data
- ✅ **Generate individual EXIF updates** - no proposal files
- ✅ **Trust Read tool analysis** - real visual content analysis only
- ✅ **Use slash commands exclusively** - documented workflows only

**TASK TOOL AGENTS: Use slash commands ONLY - they handle Read tool integration correctly!**

---

## 🛠️ **Working FastFoto Workflows**

**✅ SLASH COMMANDS - ONLY WORKING APPROACH:**

### **`/fastfoto`** - Complete OCR Analysis
- **Purpose:** Extract handwritten metadata from all back scans
- **Function:** Uses Read tool directly for real image analysis
- **Output:** Structured proposal file with extracted text, dates, locations, GPS coordinates
- **Geocoding:** Includes GPS coordinates for recognized locations (Lima, Bogotá, Dallas, etc.)

### **`/fastfoto-orientation`** - Rotation Analysis
- **Purpose:** Identify photos needing rotation using visual inspection
- **Function:** Uses Read tool to examine actual image content (people, text orientation)
- **Output:** Real rotation corrections based on visual assessment

### **`/fastfoto-apply`** - Apply EXIF Updates
- **Purpose:** Apply extracted metadata to original image files
- **Function:** Updates EXIF fields with OCR text, GPS coordinates, corrected dates
- **Safety:** Includes dry-run option for preview before applying

### **`src/preprocess_images.py`** - Image Preparation (✅ WORKS)
- **Purpose:** Prepares back scan images for Read tool compatibility
- **Usage:** `python src/preprocess_images.py [SOURCE_DIR] --output /tmp/fastfoto_prepared`
- **Function:** Resizes large images, converts formats for Read tool processing

---

## 🎯 **Success Criteria**

**Orientation Analysis Success:**
- Identifies specific photos needing rotation (not just EXIF analysis)
- Uses visual content analysis via Read tool
- Finds actual orientation problems like upside-down people

**Back Scan OCR Success:**
- Extracts readable text from handwritten photo backs
- Identifies dates, locations, people, events
- Supports multiple languages
- Generates specific metadata proposals

**Both processes bypass API integration issues by using Claude Code Read tool directly.**
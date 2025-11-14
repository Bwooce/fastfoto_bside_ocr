# FastFoto Analysis - Task Tool Instructions

## 🚨 **TASK TOOL AGENTS: READ THIS FIRST**

**MANDATORY: Use model="haiku" and Read tool ONLY. NO script creation allowed.**

**ABSOLUTELY FORBIDDEN:**
- Creating ANY bash scripts, Python files, or automation tools
- Creating comprehensive reports, summaries, or implementation guides
- Using sampling or pattern-based extrapolation
- Creating multiple output files

**REQUIRED: USE ORCHESTRATOR AND BATCH SCRIPTS ONLY - NO CUSTOM FILES**

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
"CRITICAL: Use existing orchestrator script ONLY - NO custom automation, NO Read tool scripts allowed. Run: python src/orchestrator.py scan [SOURCE_DIR] --output /tmp/fastfoto_proposal.txt to analyze ALL back scan files. The orchestrator uses Read tool internally and generates a complete proposal file. MANDATORY: Use the tested workflow, no sampling or custom approaches. OUTPUT: Single proposal file at /tmp/fastfoto_proposal.txt with verbatim OCR text and EXIF metadata updates for ALL processed files. NEVER create custom analysis scripts, ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, or any automation files. Use orchestrator.py exclusively."
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
"CRITICAL: Use existing orchestrator and batch scripts ONLY - NO custom automation allowed. Step 1: Run python batch_orientation_analysis.py for orientation analysis of main photos. Step 2: Run python src/orchestrator.py scan [SOURCE_DIR] --output /tmp/fastfoto_proposal.txt for back scan OCR processing. MANDATORY: Use tested workflows only, no custom Read tool scripts or sampling. The orchestrator handles Read tool internally. OUTPUT: Orientation analysis results from batch script AND proposal file at /tmp/fastfoto_proposal.txt with complete OCR metadata. NEVER create ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, FASTFOTO_ANALYSIS_SUMMARY.txt, or custom automation files. Use documented scripts exclusively."
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

## ✅ **ALWAYS DO THIS - USE EXISTING SCRIPTS:**

- ✅ **Use orchestrator.py exclusively** for back scan OCR processing
- ✅ **Use batch orientation scripts** for orientation analysis (batch_orientation_analysis.py)
- ✅ **Run documented commands only** - no custom automation
- ✅ **Process entire collection** with existing scripts - complete workflow coverage
- ✅ **Let scripts handle batching** - orchestrator manages Read tool internally
- ✅ **Generate outputs per script design** - proposal files, analysis results
- ✅ **Trust tested workflows** - scripts handle Read tool integration properly
- ✅ **Use established patterns** - documented scripts only
- ✅ **Follow script outputs** - proposal files, not custom JSON

**TASK TOOL AGENTS: Use orchestrator.py and batch scripts ONLY - they handle Read tool integration correctly!**

---

## 🛠️ **Available Scripts and Tools**

**CRITICAL: Task tool agents MUST use existing scripts instead of creating new automation:**

### **Image Preparation Scripts:**

**`src/orchestrator.py`** - Main FastFoto OCR orchestrator (PREFERRED)
- **Purpose:** Complete back scan OCR workflow using Read tool
- **Usage:** `python src/orchestrator.py scan [SOURCE_DIR] --output /tmp/fastfoto_proposal.txt`
- **Function:** Discovers photo pairs, analyzes back scans with Read tool, generates proposal
- **Output:** Human-reviewable proposal file with EXIF metadata updates

**`src/preprocess_images.py`** - Manual back scan preparation
- **Purpose:** Prepares back scan images for Claude Code's Read tool (if needed separately)
- **Usage:** `python src/preprocess_images.py [SOURCE_DIR] --output /tmp/fastfoto_prepared`
- **Function:** Resizes images >3.5MB to 1800px @ 85% quality, converts TIFF to JPEG
- **Output:** Optimized files in `/tmp/fastfoto_prepared/` ready for Read tool OCR

### **Orientation Analysis Scripts:**

**`batch_orientation_analysis.py`** - Main photo orientation analysis
- **Purpose:** Comprehensive orientation analysis with verification checkpoints
- **Usage:** `python batch_orientation_analysis.py`
- **Function:** Uses quality-first batch processing, 50-image verification checkpoints
- **Output:** JSON orientation recommendations for main photos

**`comprehensive_visual_orientation_analysis.py`** - Visual orientation analysis
- **Purpose:** VISUAL orientation analysis (Do people look upright? Are faces oriented correctly?)
- **Usage:** `python comprehensive_visual_orientation_analysis.py`
- **Function:** Processes in batches of 50 max with verification checkpoints
- **Output:** Visual assessment of orientation issues

**`exif_orientation_checker.py`** - EXIF orientation verification
- **Purpose:** Check EXIF orientation flags and metadata
- **Usage:** `python exif_orientation_checker.py`
- **Function:** Analyzes EXIF data for orientation discrepancies

### **Manual Image Processing Commands:**

**ImageMagick/magick commands** - For creating `/tmp/orientation_analysis/`
- **Usage:** `magick "input.jpg" -resize 300x300 "output.jpg"`
- **Purpose:** Downsample images to 300px for Read tool compatibility
- **Function:** Creates smaller versions for efficient Read tool processing

## 📁 **File Preparation Required**

**Task tool agents MUST use existing scripts above rather than creating new automation:**

**Orientation Analysis Options:**
1. **Preferred:** Use `python batch_orientation_analysis.py` or `python comprehensive_visual_orientation_analysis.py`
2. **Manual:** Create `/tmp/orientation_analysis/` with magick resize commands
3. **FORBIDDEN:** Creating inline Python scripts or custom automation

**Back Scan OCR:**
- **Required:** `python src/orchestrator.py scan [SOURCE_DIR] --output /tmp/fastfoto_proposal.txt`
- **Alternative:** `python src/preprocess_images.py [SOURCE_DIR] --output /tmp/fastfoto_prepared` (preparation only)
- **FORBIDDEN:** Custom preprocessing scripts, inline code, or Read tool automation

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
# FastFoto Analysis - Task Tool Instructions

## 🚨 **TASK TOOL AGENTS: READ THIS FIRST**

**MANDATORY: Use model="haiku" and Read tool ONLY. NO script creation allowed.**

**ABSOLUTELY FORBIDDEN:**
- Creating ANY bash scripts, Python files, or automation tools
- Creating comprehensive reports, summaries, or implementation guides
- Using sampling or pattern-based extrapolation
- Creating multiple output files

**REQUIRED OUTPUT: SINGLE JSON FILE ONLY - NO TEXT FILES, NO DOCUMENTATION**

## ⚠️ **USE TASK TOOL ONLY - NO CODE WRITING**

This guide provides exact phrases for FastFoto analysis using Claude Code's Task tool with Read tool integration.

---

## 🔄 **Orientation Analysis**

When a user requests orientation analysis, use this **exact phrase**:

```
"CRITICAL: Use Read tool ONLY - NO script creation or comprehensive documentation allowed. Analyze orientation issues by directly reading EVERY INDIVIDUAL image from /tmp/orientation_analysis/ using Read tool. Process ALL files individually in batches of 10-15 files maximum. For each specific image file, use Read tool to visually inspect if people are upright and scenes make visual sense. MANDATORY: Check files across all eras including early 2000s photos, 1990s photos, and event photos where orientation issues are most likely. NO sampling, NO pattern extrapolation, NO comprehensive reports. OUTPUT: Single JSON file ONLY named orientation_analysis_complete.json. NEVER create ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, or any documentation files."
```

**What this does:**
- Creates downsampled images (300px) for efficient Read tool processing
- Uses Task tool with Read tool for visual analysis
- Identifies actual orientation problems (upside down, sideways photos)
- Generates EXIF rotation recommendations

**Expected findings:**
- Photos with people upside down (180° rotation needed)
- Landscape photos in portrait orientation (90° rotation needed)
- Portrait photos in landscape orientation (90° rotation needed)
- Sideways group photos (90° counter-clockwise rotation needed)

---

## 📝 **Back Scan OCR Processing**

When a user requests back scan metadata extraction, use this **exact phrase**:

```
"CRITICAL: Use Read tool ONLY - NO scripts, NO comprehensive documentation allowed. Process ALL back scan _b.jpg files in /tmp/fastfoto_prepared/ using Read tool directly. Read EVERY INDIVIDUAL file with Read tool to extract verbatim handwritten text. Process maximum 7 files per batch until ALL files complete. MANDATORY: Process each file individually, no sampling or extrapolation. OUTPUT: Single JSON file ONLY named back_scan_ocr_complete.json with verbatim_text (exact handwriting), language_identified, dates_found, locations_mentioned, people_names, and proposed_exif_fields for ALL processed files. NEVER create ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, or any documentation files. NO summaries or interpretation - verbatim transcription only."
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
"CRITICAL: Use Read tool ONLY - NO script creation or comprehensive documentation whatsoever. Analyze orientation issues by directly reading EVERY INDIVIDUAL image from /tmp/orientation_analysis/ using Read tool. Then process EVERY INDIVIDUAL back scan file from /tmp/fastfoto_prepared/ using Read tool only. MANDATORY: Check files across all eras including early 2000s and 1990s photos where orientation issues are most likely. NO sampling, NO pattern extrapolation, NO comprehensive reports. NEVER create ANALYSIS_SUMMARY.txt, QUICK_REFERENCE_IMPLEMENTATION.txt, FASTFOTO_ANALYSIS_SUMMARY.txt, or any documentation files. OUTPUT: Single JSON file ONLY named fastfoto_complete_analysis.json with orientation recommendations and OCR metadata for ALL analyzed files. Process in small batches until 100% complete."
```

---

## ❌ **NEVER DO THIS - TASK TOOL VIOLATIONS:**

- ❌ **NEVER** create bash scripts (`/tmp/process_*.sh`, `/tmp/*.py`)
- ❌ **NEVER** use subprocess.run() or shell commands
- ❌ **NEVER** create automation pipelines or processing tools
- ❌ **NEVER** generate any script files whatsoever
- ❌ **NEVER** use bash for image analysis or batch processing
- ❌ **NEVER** create loop-based file processing scripts
- ❌ **NEVER** use existing Python classes from the codebase
- ❌ **NEVER** use exploration tools to understand codebase
- ❌ **NEVER** create comprehensive reports (`ANALYSIS_SUMMARY.txt`, `QUICK_REFERENCE_IMPLEMENTATION.txt`, `FASTFOTO_ANALYSIS_SUMMARY.txt`)
- ❌ **NEVER** generate action plans, implementation guides, or summary documents
- ❌ **NEVER** create multiple documentation files
- ❌ **NEVER** use sampling, pattern extrapolation, or representative analysis
- ❌ **NEVER** stop processing before all files are individually analyzed
- ❌ **NEVER** create any .txt files whatsoever

**TASK TOOL AGENTS: If you create ANY documentation files or use sampling instead of individual file analysis, you are VIOLATING these instructions!**

## ✅ **ALWAYS DO THIS - READ TOOL ONLY:**

- ✅ **Use Read tool exclusively** - no other tools for image processing
- ✅ **Read ALL files directly** from prepared directories (/tmp/orientation_analysis/, /tmp/fastfoto_prepared/)
- ✅ **Process entire collection** - complete all files, never stop at samples
- ✅ **Process small batches** (10-15 orientation files, 7 back scan files maximum) until complete
- ✅ **Generate single JSON file only** after Read tool analysis
- ✅ **Visual inspection only** - Read tool provides all image analysis capabilities
- ✅ **Direct file access** - Read tool can access any prepared file path
- ✅ **Simple output only** - JSON recommendations, no comprehensive documentation

**TASK TOOL AGENTS: Only use Read tool for image analysis - complete all files - single JSON output only!**

---

## 🛠️ **Available Scripts and Tools**

**CRITICAL: Task tool agents MUST use existing scripts instead of creating new automation:**

### **Image Preparation Scripts:**

**`src/preprocess_images.py`** - Back scan preparation
- **Purpose:** Prepares back scan images for Claude Code's Read tool
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
- **Required:** `python src/preprocess_images.py [SOURCE_DIR] --output /tmp/fastfoto_prepared`
- **FORBIDDEN:** Custom preprocessing scripts or inline code

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
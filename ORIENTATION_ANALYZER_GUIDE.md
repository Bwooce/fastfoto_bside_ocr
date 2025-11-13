# Orientation Analyzer - SIMPLE USAGE

## ⚠️ **JUST RUN THE EXISTING TOOL - NO EXPLORATION NEEDED**

When a user says: **"Analyze orientation of main FastFoto photos with verification checkpoints"**

**DO THIS IMMEDIATELY:**
```bash
python src/orientation_analyzer.py /path/to/photos
```

## ❌ **DO NOT DO ANY OF THIS:**
- ❌ Create project overview documents
- ❌ Use Explore tool to understand codebase
- ❌ Write new scripts or code
- ❌ Set up todo lists for exploration
- ❌ Create comprehensive documentation

## ✅ **JUST RUN THE TOOL DIRECTLY:**

**For the directory ~/Pictures/2025_PeruScanning, run:**

```bash
python src/orientation_analyzer.py ~/Pictures/2025_PeruScanning
```

**That's it! The tool handles everything automatically:**

**ACCURACY-FOCUSED APPROACH - Quality over speed!**

Claude will:
1. Auto-discover main photos (excludes _b back scans) - **silent background**
2. Process in **SMALL verified batches** (max 50 images per batch)
3. **🚨 MANDATORY: Individual analysis for any photo with EXIF orientation ≠ 1**
4. **Verification checkpoint every 50 photos** - manual spot checks
5. **Content validation**: "Does this photo look correct as displayed?"
6. Update EXIF orientation flags only after verification

**Quality-First Processing:**
- ❌ **Large batches**: No 100-200 image mega-batches that miss issues
- ❌ **Era bias**: Don't assume newer photos are correctly oriented
- ❌ **Speed over accuracy**: Don't prioritize token efficiency over correctness
- ❌ **Multiple output files**: No /tmp/all_main_photos.txt, no duplicate JSON reports
- ✅ **Small verified batches**: Max 50 images per batch with verification
- ✅ **Mandatory individual analysis**: Any EXIF orientation ≠ 1 gets personal attention
- ✅ **Content validation checkpoints**: "Does person look upright?" every 50 photos
- ✅ **Single output file**: Only `/tmp/orientation_exif_recommendations.json`
- ✅ **Quality gates**: No photo left unverified if orientation seems wrong

## 📏 **Image Size Handling**

### ✅ **Aggressive Downsampling for Orientation Analysis**

**Orientation Detection Requirements:**
- **Purpose**: Detect rotation (90°, 180°, 270°), color balance
- **Resolution needed**: VERY low! 300-400px max dimension is sufficient
- **File size**: Target ~100-200KB (much smaller than OCR analysis)

**Your Main Photo Collection:**
- Typical main photos: 3000-6000px dimension, 20-100MB
- **Downsampled for orientation**: 300px dimension, ~100KB
- **Result**: Massive token savings, sufficient for rotation detection!

### 🎯 **Workflow Integration**

**Combined Preprocessing + Analysis (Recommended)**
```
User: "Analyze orientation and color quality of main FastFoto photos using Haiku model"

Claude:
1. Auto-downsamples large images to ~300px (orientation analysis only)
2. **Batch processes** main photos (10 per batch for token efficiency)
3. Analyzes with Haiku model using minimal tokens
4. Updates EXIF orientation flags (metadata only - preserves original pixels)
5. Suggests color/brightness adjustments
```

**Separate from Back Scan OCR:**
```
User: "Process FastFoto back scans for metadata extraction"

Claude:
1. Uses existing preprocess_images.py for back scans (_b files)
2. Runs detailed Sonnet OCR on all back scans
3. Extracts dates, locations, people for EXIF updates
```

## 🔧 **Integration with Current Workflow**

**The orientation analyzer integrates with the existing workflow - no new code needed!**

The existing `src/orientation_analyzer.py` handles all orientation analysis automatically when you use the recommended phrase.

## 🎯 **Technical Benefits**

**Benefits:**
- Separate, optimized workflows for different purposes
- Haiku perfect for orientation detection (doesn't need fine detail)
- Sonnet focused on text extraction (where detail matters)
- Aggressive downsampling reduces processing overhead
- **Non-destructive EXIF updates**: Original pixels preserved, metadata-only fixes
- **Universal compatibility**: Apple Photos, Google Photos, Adobe Lightroom respect EXIF orientation
- Batch processing recommendations for efficient corrections

## 🎯 **Sample Claude Code Session - QUALITY-FIRST**

```
User: "Analyze orientation of main FastFoto photos with verification checkpoints"

Claude: I'll analyze main photos for orientation issues with quality-first verification.

Analyzing main photo collection...
Found 4,847 main photos (excluded 500 _b back scans)

🔍 Pre-scan: Checking for existing EXIF orientation issues...
Found 127 photos with EXIF orientation ≠ 1 (requires individual analysis)

Processing batch 1/97 (50 images max)...
Task(Verified orientation batch 1) → Done (800 tokens, 12s)
⚠️  Found 3 photos with EXIF orientation 6 - analyzing individually...
Individual analysis complete: 2 needed correction, 1 was correct

✅ Checkpoint 1 (50 photos): Manual verification of 5 sample photos
All verified photos display correctly with people upright ✓

Processing batch 2/97 (50 images max)...
Task(Verified orientation batch 2) → Done (750 tokens, 11s)
Individual analysis: 1 photo with orientation 8 → corrected to 1

Processing batch 3/97 (50 images max)...
Task(Verified orientation batch 3) → Done (825 tokens, 13s)
No orientation issues found in this batch ✓

✅ Checkpoint 2 (100 photos): Content validation check passed

[... continuing with verification every 50 photos ...]

📊 Quality-First Analysis Complete:
- Total photos: 4,847
- Batches processed: 97 (max 50 per batch)
- Individual verifications: 127 (EXIF ≠ 1)
- Verification checkpoints: 97 (every 50 photos)
- Rotation corrections applied: 89 images (verified accurate)
- Processing time: 35 minutes (vs 12 min unverified)
- Token usage: 91k total (higher but accurate)

✅ All photos verified to display correctly with content validation!
🏆 Zero missed orientation issues (vs previous batch processing bugs)
```

**Quality-First Approach:**
1. **Small verified batches**: Max 50 images per Task call with verification
2. **Mandatory individual analysis**: Any EXIF ≠ 1 gets personal attention
3. **Content validation checkpoints**: Manual spot checks every 50 photos
4. **No era bias**: Every photo series gets equal verification attention
5. **Quality over speed**: 35 min processing vs 12 min but guaranteed accuracy

## 📝 **Key Advantages**

1. **Efficient Processing**: Haiku model optimized for visual analysis tasks
2. **Aggressive Downsampling**: 600px is plenty for orientation detection
3. **Separate Purpose**: Main photos (orientation) vs back scans (metadata)
4. **Batch Corrections**: Provides EXIF orientation recommendations for bulk fixes
5. **Complementary Workflow**: Works alongside back scan OCR processing

**Bottom Line**: Use this for orientation/color analysis of your main photo collection, while using the existing OCR workflow for back scan metadata extraction!
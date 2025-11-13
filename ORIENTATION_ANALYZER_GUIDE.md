# Orientation Analyzer Usage Guide

## 🎯 **Purpose**: Analyze MAIN PHOTOS (front images), NOT back scans

**Two Separate Workflows:**
1. **Orientation Analyzer** → Main photo collection (~5000 images) → Orientation, color correction
2. **OCR Analysis** → Back scans (_b files, ~500 images) → Metadata extraction

## 🚀 How to Invoke in Claude Code Sessions

### Method 1: Direct Analysis (Single Main Photo)
```
"Analyze the orientation and quality of this main photo using Haiku model: /tmp/photos_prepared/IMG_001.jpg"
```

Claude will:
1. Use Task tool with `model="haiku"`
2. Use Read tool on the downsampled image
3. Apply orientation analysis prompt
4. Return orientation correction and color adjustment recommendations

### Method 2: Batch Analysis (Main Photo Collection)
```
"Analyze orientation and color quality of main FastFoto collection using Haiku model"
```

Claude will:
1. Auto-discover main photo files (automatically excludes _b back scans)
2. Downsample images heavily (orientation detection doesn't need high resolution)
3. **Batch process images** (10 images per batch for token efficiency)
4. **Invoke Haiku sub-agent** via Task tool for analysis
5. Update EXIF orientation flags (metadata only - NO pixel rotation)
6. Generate recommendations for color/brightness corrections

## 📏 **Image Size Handling**

### ✅ **Aggressive Downsampling for Orientation Analysis**

**Orientation Detection Requirements:**
- **Purpose**: Detect rotation (90°, 180°, 270°), color balance
- **Resolution needed**: Very low! 600-800px max dimension is plenty
- **File size**: Can be ~500KB-1MB (much smaller than OCR analysis)

**Your Main Photo Collection:**
- Typical main photos: 3000-6000px dimension, 20-100MB
- **Downsampled for orientation**: 600px dimension, ~500KB
- **Result**: Much faster processing, optimized for visual analysis!

### 🎯 **Workflow Integration**

**Combined Preprocessing + Analysis (Recommended)**
```
User: "Analyze orientation and color quality of main FastFoto photos using Haiku model"

Claude:
1. Auto-downsamples large images to ~600px (orientation analysis only)
2. Analyzes ALL main photos with Haiku model
3. Updates EXIF orientation flags (metadata only - preserves original pixels)
4. Suggests color/brightness adjustments
5. Creates batch processing script for color corrections
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

### Enhanced Interactive Processor

```python
class EnhancedInteractiveProcessor:
    def __init__(self):
        self.orientation_analyzer = OrientationAnalyzer()
        self.interactive_processor = InteractiveProcessor()

    def process_with_optimization(self, directory: Path):
        # Phase 1: Orientation analysis (cheap)
        print("Phase 1: Analyzing orientation and quality...")
        orientation_results = self.orientation_analyzer.analyze_batch(image_paths)

        # Filter based on quality
        high_value_images = [
            path for path, result in orientation_results
            if result.high_value and not result.skip_ocr
        ]

        print(f"Quality filter: {len(high_value_images)}/{len(image_paths)} images worth processing")

        # Phase 2: Detailed OCR (expensive)
        print("Phase 2: Detailed OCR on high-value images...")
        ocr_results = self.interactive_processor.process_directory(high_value_images)

        return orientation_results, ocr_results
```

## 🎯 **Technical Benefits**

**Benefits:**
- Separate, optimized workflows for different purposes
- Haiku perfect for orientation detection (doesn't need fine detail)
- Sonnet focused on text extraction (where detail matters)
- Aggressive downsampling reduces processing overhead
- **Non-destructive EXIF updates**: Original pixels preserved, metadata-only fixes
- **Universal compatibility**: Apple Photos, Google Photos, Adobe Lightroom respect EXIF orientation
- Batch processing recommendations for efficient corrections

## 🎯 **Sample Claude Code Session**

```
User: "Analyze orientation and color quality of main FastFoto photos using Haiku model"

Claude: I'll analyze the main photo collection for orientation and color issues using Haiku model.

Processing main photo collection...
[Auto-excludes _b back scan files]
[Filtered 4,847 main photos from 5,347 total files]
[Auto-downsamples to ~600px for orientation analysis]
[Uses Task tool with model="haiku"]
[Processes main photo collection in batches]

Results:
📊 Orientation Analysis Summary:
- Total files discovered: 5,347
- Back scans excluded: 500 (_b files)
- Main photos analyzed: 4,847
- Needs 90° rotation: 234 images (4.8%)
- Needs 180° rotation: 12 images (0.2%)
- Needs 270° rotation: 89 images (1.8%)
- Color correction needed: 567 images (11.7%)
- Good as-is: 3,945 images (81.4%)

🚀 Auto-Applied EXIF Updates:
- Updated orientation flags: 335 images (metadata only - no pixel changes)
- Photo viewers (Apple Photos, Google Photos) will now display correctly
- Color correction recommendations: 567 images
- Generated batch processing script for color fixes

Separate workflow: Back scan OCR for metadata extraction on _b files
```

## 📝 **Key Advantages**

1. **Efficient Processing**: Haiku model optimized for visual analysis tasks
2. **Aggressive Downsampling**: 600px is plenty for orientation detection
3. **Separate Purpose**: Main photos (orientation) vs back scans (metadata)
4. **Batch Corrections**: Generate scripts for bulk rotation/color fixes
5. **Complementary Workflow**: Works alongside back scan OCR processing

**Bottom Line**: Use this for orientation/color analysis of your main photo collection, while using the existing OCR workflow for back scan metadata extraction!
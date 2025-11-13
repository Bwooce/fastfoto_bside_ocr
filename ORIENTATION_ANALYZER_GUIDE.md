# Orientation Analyzer Usage Guide

## 🚀 How to Invoke in Claude Code Sessions

### Method 1: Direct Analysis (Preprocessed Images)
```
"Analyze the orientation and quality of this prepared image using Haiku model: /tmp/fastfoto_prepared/IMG_001_b.jpg"
```

Claude will:
1. Use Task tool with `model="haiku"`
2. Use Read tool on the preprocessed image
3. Apply orientation analysis prompt
4. Return orientation, quality, and processing recommendations

### Method 2: Full Workflow (Large Images)
```
"Preprocess FastFoto images from ~/Photos/FastFoto then run orientation analysis using Haiku for cost efficiency"
```

Claude will:
1. Run preprocessing script to resize/convert large images
2. Discover all prepared image files
3. Analyze each with Haiku model
4. Generate batch report with recommendations
5. Filter images for detailed OCR processing

## 📏 **Image Size Handling**

### ⚠️ **REQUIRES Preprocessing for Large Images**

**Claude Code Read Tool Limits (ALL models):**
- **Max dimension**: 2000px
- **Max file size**: ~5MB
- **Formats**: JPEG, PNG, GIF, WebP

**Your FastFoto Images:**
- Typical scanned photos: 3000-6000px dimension
- File sizes: Usually 10-50MB for high-quality scans
- **Result**: Need preprocessing before ANY Claude Code analysis!

### 🎯 **Workflow Integration**

**Option A: Two-Stage Preprocessing (Recommended)**
```
User: "First preprocess FastFoto images for analysis, then run orientation analysis using Haiku"

Claude:
1. Runs preprocessing script: python src/preprocess_images.py ~/Photos/FastFoto --output /tmp/fastfoto_prepared
2. Analyzes prepared images with Haiku (~$2-5 for 500 images)
3. Filters out unusable images (blur, poor quality)
4. Fixes orientation issues automatically
5. Processes good candidates with Sonnet OCR (~$50-100)
6. Total cost savings: 50-70% vs processing everything
```

**Option B: Parallel Processing**
```
User: "Process FastFoto images with both orientation analysis and detailed OCR"

Claude:
1. Runs orientation analysis (Haiku) in parallel
2. Runs detailed OCR (Sonnet) in parallel
3. Cross-references results for quality validation
4. Provides comprehensive analysis
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

## 💰 **Cost Benefits**

### Example: 500 Image Collection

**Without Orientation Analyzer:**
- 500 images × Sonnet OCR = ~$150-200

**With Orientation Analyzer:**
- 500 images × Haiku analysis = ~$3-5
- 300 high-value images × Sonnet OCR = ~$90-120
- **Total**: ~$95-125 (40-50% savings)

**Plus Quality Benefits:**
- Skip blurry/unusable images
- Fix orientation issues automatically
- Identify manual review cases
- Focus OCR budget on valuable images

## 🎯 **Sample Claude Code Session**

```
User: "Preprocess and analyze orientation/quality of FastFoto images in ~/Photos/FastFoto using cost-effective approach"

Claude: I'll first preprocess the images, then use OrientationAnalyzer with Haiku model for cost-effective bulk analysis.

Step 1: Preprocessing large images...
[Runs: python src/preprocess_images.py ~/Photos/FastFoto --output /tmp/fastfoto_prepared]

Step 2: Orientation analysis with Haiku...
[Uses Task tool with model="haiku"]
[Processes prepared images in batches]

Results:
📊 Analysis Summary:
- Total images: 482
- Needs rotation: 23 images (4.8%)
- Skip OCR (poor quality): 67 images (13.9%)
- High-value candidates: 315 images (65.4%)
- Manual review: 25 images (5.2%)

💰 Cost Optimization:
- Haiku analysis cost: ~$4
- Sonnet OCR needed for: 315 images (vs 482)
- Estimated savings: 34.6% reduction in Sonnet usage

🚀 Next Steps:
1. Fix 23 orientation issues automatically
2. Process 315 high-value images with detailed OCR
3. Queue 25 images for manual review
4. Skip 67 poor-quality images

Proceed with detailed OCR? [Y/n]
```

## 📝 **Key Advantages**

1. **Cost Effective**: ~12x cheaper than Sonnet for bulk operations
2. **Handles Large Images**: Works with unconverted FastFoto scans
3. **Quality Filter**: Saves money by skipping poor images
4. **Orientation Fix**: Automatically detects and suggests corrections
5. **Smart Workflow**: Focus expensive Sonnet OCR on valuable images

**Bottom Line**: Use this for initial analysis of your full FastFoto collection, then run detailed OCR only on the images worth processing!
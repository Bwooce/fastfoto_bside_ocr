# Orientation Analyzer Usage Guide

## 🚀 How to Invoke in Claude Code Sessions

### Method 1: Direct Analysis
```
"Analyze the orientation and quality of this image using Haiku model: /path/to/photo.jpg"
```

Claude will:
1. Use Task tool with `model="haiku"`
2. Use Read tool on the image
3. Apply orientation analysis prompt
4. Return orientation, quality, and processing recommendations

### Method 2: Batch Analysis
```
"Run orientation analysis on all photos in ~/Photos/FastFoto using Haiku model for cost efficiency"
```

Claude will:
1. Discover all image files
2. Analyze each with Haiku model
3. Generate batch report with recommendations
4. Filter images for detailed OCR processing

## 📏 **Unconverted Image Handling**

### ✅ **CAN Handle Unconverted Images**

**Haiku Model Limits:**
- **Max dimension**: ~5000px (much larger than Sonnet's 2000px limit)
- **Max file size**: ~32MB
- **Formats**: JPEG, PNG, GIF, WebP

**Your FastFoto Images:**
- Most scanned photos: 2000-4000px dimension
- File sizes: Usually 5-15MB for high-quality scans
- **Result**: Most images will work directly without conversion!

### 🎯 **Workflow Integration**

**Option A: Pre-Processing Filter (Recommended)**
```
User: "Run orientation analysis on ~/Photos/FastFoto, then process high-value images with detailed OCR"

Claude:
1. Analyzes ALL images with Haiku (~$2-5 for 500 images)
2. Filters out unusable images (blur, poor quality)
3. Fixes orientation issues automatically
4. Processes good candidates with Sonnet OCR (~$50-100)
5. Total cost savings: 50-70% vs processing everything
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
User: "Analyze orientation and quality of FastFoto images in ~/Photos/FastFoto using cost-effective approach"

Claude: I'll use the OrientationAnalyzer with Haiku model for cost-effective bulk analysis.

[Uses Task tool with model="haiku"]
[Processes images in batches]

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
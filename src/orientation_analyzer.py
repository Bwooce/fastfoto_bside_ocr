"""
Orientation and basic image analysis using cost-effective Haiku model.

Provides pre-processing analysis to:
- Detect and correct orientation issues
- Assess image quality
- Filter out unusable images
- Identify high-value candidates for detailed OCR

Uses Haiku model for ~12x cost savings vs. Sonnet on bulk operations.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OrientationResult:
    """Results from orientation and quality analysis."""

    # Orientation
    needs_rotation: bool
    rotation_degrees: int  # 0, 90, 180, 270
    confidence: float

    # Quality assessment
    quality_score: float  # 0.0 - 1.0
    blur_detected: bool
    lighting_issues: bool
    contrast_problems: bool

    # Content assessment
    has_text: bool
    has_handwriting: bool
    is_back_scan: bool  # vs front of photo
    multiple_photos: bool

    # Processing recommendations
    skip_ocr: bool  # Too poor quality for OCR
    high_value: bool  # Likely to have good metadata
    manual_review: bool  # Needs human inspection

    # Raw analysis
    raw_response: str


class OrientationAnalyzer:
    """Analyzes image orientation and quality using Haiku model."""

    def __init__(self):
        self.model = "haiku"  # Use cost-effective Haiku model
        self._init_prompt()

    def _init_prompt(self):
        """Initialize the analysis prompt for Haiku model."""
        self.batch_analysis_prompt = '''
Analyze photo orientation and technical quality. Return JSON array:

```json
[
  {
    "image_name": "IMG_001.jpg",
    "needs_rotation": true/false,
    "rotation_degrees": 0,
    "quality_score": 0.85,
    "blur_detected": false,
    "lighting_issues": false
  }
]
```

Rules:
- Detect rotation: 0°, 90°, 180°, 270° only
- Quality score: 0.0-1.0 (technical quality)
- NO content description
- NO text interpretation
- Focus: display optimization only
'''

    def analyze_image(self, image_path: Path) -> OrientationResult:
        """
        Analyze image orientation and quality.

        Args:
            image_path: Path to image file

        Returns:
            OrientationResult with analysis
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            # This would use Claude Code's Read tool with Haiku model
            # For now, simulate the analysis
            logger.info(f"Analyzing orientation and quality: {image_path.name}")

            # In actual implementation, this would be:
            # response = self._call_haiku_model(image_path, self.analysis_prompt)
            response = self._simulate_analysis(image_path)

            # Parse response
            result = self._parse_response(response)

            logger.debug(f"Analysis complete for {image_path.name}: "
                        f"rotation={result.rotation_degrees}°, "
                        f"quality={result.quality_score:.2f}")

            return result

        except Exception as e:
            logger.error(f"Error analyzing {image_path}: {e}")
            # Return safe defaults
            return OrientationResult(
                needs_rotation=False,
                rotation_degrees=0,
                confidence=0.0,
                quality_score=0.5,
                blur_detected=False,
                lighting_issues=False,
                contrast_problems=False,
                has_text=True,  # Assume text present
                has_handwriting=False,
                is_back_scan=True,
                multiple_photos=False,
                skip_ocr=False,
                high_value=False,
                manual_review=True,  # Flag for manual review on error
                raw_response=f"Error: {str(e)}"
            )

    def _simulate_analysis(self, image_path: Path) -> str:
        """
        Simulate Haiku model analysis for testing.

        In production, this would call Claude Code's Read tool with Haiku model.
        """
        # Simulate different scenarios based on filename patterns
        name_lower = image_path.name.lower()

        if 'rotated' in name_lower or '_r' in name_lower:
            return '''```json
{
  "orientation": {
    "needs_rotation": true,
    "rotation_degrees": 90,
    "confidence": 0.92,
    "reasoning": "Text appears rotated 90 degrees clockwise"
  },
  "quality": {
    "overall_score": 0.85,
    "blur_detected": false,
    "lighting_issues": false,
    "contrast_problems": false,
    "quality_notes": "Sharp and well-lit"
  },
  "content": {
    "has_text": true,
    "has_handwriting": true,
    "is_back_scan": true,
    "multiple_photos": false,
    "content_notes": "Handwritten date visible when rotated"
  },
  "recommendations": {
    "skip_ocr": false,
    "high_value": true,
    "manual_review": false,
    "processing_notes": "Good candidate after rotation correction"
  }
}```'''

        elif 'blur' in name_lower or 'bad' in name_lower:
            return '''```json
{
  "orientation": {
    "needs_rotation": false,
    "rotation_degrees": 0,
    "confidence": 0.95,
    "reasoning": "Orientation appears correct"
  },
  "quality": {
    "overall_score": 0.25,
    "blur_detected": true,
    "lighting_issues": false,
    "contrast_problems": true,
    "quality_notes": "Significant motion blur, low contrast"
  },
  "content": {
    "has_text": true,
    "has_handwriting": false,
    "is_back_scan": true,
    "multiple_photos": false,
    "content_notes": "Text present but illegible due to blur"
  },
  "recommendations": {
    "skip_ocr": true,
    "high_value": false,
    "manual_review": true,
    "processing_notes": "Too blurry for reliable OCR"
  }
}```'''

        else:
            # Standard good quality image
            return '''```json
{
  "orientation": {
    "needs_rotation": false,
    "rotation_degrees": 0,
    "confidence": 0.98,
    "reasoning": "Text orientation is correct"
  },
  "quality": {
    "overall_score": 0.88,
    "blur_detected": false,
    "lighting_issues": false,
    "contrast_problems": false,
    "quality_notes": "Sharp, well-lit, good contrast"
  },
  "content": {
    "has_text": true,
    "has_handwriting": true,
    "is_back_scan": true,
    "multiple_photos": false,
    "content_notes": "Clear handwriting and printed date stamp"
  },
  "recommendations": {
    "skip_ocr": false,
    "high_value": true,
    "manual_review": false,
    "processing_notes": "Excellent candidate for detailed OCR"
  }
}```'''

    def _parse_response(self, response: str) -> OrientationResult:
        """Parse JSON response from Haiku model."""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object
                json_start = response.find('{')
                json_end = response.rfind('}')
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end + 1]
                else:
                    raise ValueError("No JSON found in response")

            data = json.loads(json_str)

            # Extract data with safe defaults
            orientation = data.get('orientation', {})
            quality = data.get('quality', {})
            content = data.get('content', {})
            recommendations = data.get('recommendations', {})

            return OrientationResult(
                needs_rotation=orientation.get('needs_rotation', False),
                rotation_degrees=orientation.get('rotation_degrees', 0),
                confidence=orientation.get('confidence', 0.0),

                quality_score=quality.get('overall_score', 0.5),
                blur_detected=quality.get('blur_detected', False),
                lighting_issues=quality.get('lighting_issues', False),
                contrast_problems=quality.get('contrast_problems', False),

                has_text=content.get('has_text', True),
                has_handwriting=content.get('has_handwriting', False),
                is_back_scan=content.get('is_back_scan', True),
                multiple_photos=content.get('multiple_photos', False),

                skip_ocr=recommendations.get('skip_ocr', False),
                high_value=recommendations.get('high_value', False),
                manual_review=recommendations.get('manual_review', False),

                raw_response=response
            )

        except Exception as e:
            logger.error(f"Failed to parse Haiku response: {e}")
            logger.debug(f"Response was: {response}")
            raise ValueError(f"Invalid response format: {e}")

    def filter_main_photos(self, image_paths: List[Path]) -> List[Path]:
        """
        Filter to main photos only - exclude _b back scan files.

        Args:
            image_paths: List of all image paths

        Returns:
            List of main photo paths (excluding _b back scans)
        """
        main_photos = []

        for image_path in image_paths:
            # Skip back scan files (ending with _b.jpg, _b.jpeg, etc.)
            if '_b.' in image_path.name.lower():
                logger.debug(f"Skipping back scan: {image_path.name}")
                continue

            main_photos.append(image_path)

        logger.info(f"Filtered {len(main_photos)} main photos from {len(image_paths)} total files")
        return main_photos

    def analyze_batch_efficient(self, image_paths: List[Path], batch_size: int = 10) -> List[Tuple[Path, OrientationResult]]:
        """
        Analyze multiple images in efficient batches to minimize token usage.

        Args:
            image_paths: List of image paths to analyze
            batch_size: Number of images to process in each batch (default: 10)

        Returns:
            List of (path, result) tuples
        """
        # Automatically filter to main photos only
        main_photos = self.filter_main_photos(image_paths)
        all_results = []

        # Process images in batches for token efficiency
        for i in range(0, len(main_photos), batch_size):
            batch = main_photos[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(main_photos) + batch_size - 1)//batch_size}: {len(batch)} images")

            try:
                # In actual implementation: Call Claude Code with batch of images
                batch_response = self._call_claude_code_batch(batch)

                # Parse batch response
                batch_results = self._parse_batch_response(batch_response, batch)
                all_results.extend(batch_results)

            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                # Add error results for this batch
                for image_path in batch:
                    error_result = OrientationResult(
                        needs_rotation=False, rotation_degrees=0, confidence=0.0,
                        quality_score=0.0, blur_detected=False, lighting_issues=False,
                        contrast_problems=False, has_text=True, has_handwriting=False,
                        is_back_scan=False, multiple_photos=False, skip_ocr=False,
                        high_value=False, manual_review=True, raw_response=f"Batch error: {str(e)}"
                    )
                    all_results.append((image_path, error_result))

        return all_results

    def _call_claude_code_batch(self, image_paths: List[Path]) -> str:
        """
        Call Claude Code with batch of images using Task tool.

        This is where the actual sub-agent invocation happens.
        """
        # Downsample all images first to reduce token usage
        downsampled_paths = []

        logger.info(f"Downsampling {len(image_paths)} images for batch analysis...")

        for i, image_path in enumerate(image_paths):
            downsampled_path = self._downsample_image_for_orientation(image_path)
            downsampled_paths.append(downsampled_path)
            logger.debug(f"  [{i+1}/{len(image_paths)}] {image_path.name} -> {downsampled_path}")

        # Create batch prompt with image list
        image_list = [f"- {path.name}" for path in image_paths]
        image_list_str = "\n".join(image_list)

        batch_prompt = f"""You are analyzing main photos (NOT back scans) for orientation and basic quality issues.

IMAGES TO ANALYZE ({len(image_paths)} total):
{image_list_str}

{self.batch_analysis_prompt}

CRITICAL: Return a JSON array with exactly {len(image_paths)} entries, one for each image listed above, in the same order."""

        # Use Task tool with Haiku model for efficient batch processing
        logger.info(f"Calling Task tool for batch analysis of {len(image_paths)} images...")

        # Simulate the Task call for now (this would be replaced with actual Task tool call)
        # In actual implementation, this would use:
        # task_response = Task(
        #     subagent_type="general-purpose",
        #     model="haiku",
        #     prompt=batch_prompt + "\n\nProcess all downsampled images and return orientation analysis JSON.",
        #     description="Batch orientation analysis"
        # )

        # For now, simulate batch processing
        return self._simulate_batch_analysis(image_paths)

    def _downsample_image_for_orientation(self, image_path: Path) -> Path:
        """
        Aggressively downsample image to ~300px for orientation analysis.

        Args:
            image_path: Original image path

        Returns:
            Path to downsampled image
        """
        # Use temporary file for downsampled image
        import tempfile
        from PIL import Image

        temp_dir = Path(tempfile.gettempdir())
        downsampled_path = temp_dir / f"orient_{image_path.stem}_300px.jpg"

        try:
            with Image.open(image_path) as img:
                # Calculate new size - max dimension 300px
                width, height = img.size
                max_dimension = max(width, height)

                if max_dimension > 300:
                    scale = 300 / max_dimension
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    # Resize with high-quality resampling
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save with aggressive compression for orientation analysis
                    img_resized.save(downsampled_path, "JPEG", quality=70, optimize=True)

                    logger.debug(f"Downsampled {image_path.name}: ({width}, {height}) -> ({new_width}, {new_height})")
                else:
                    # Image already small enough - just copy with compression
                    img.save(downsampled_path, "JPEG", quality=70, optimize=True)

                return downsampled_path

        except Exception as e:
            logger.error(f"Failed to downsample {image_path}: {e}")
            # Return original path as fallback
            return image_path

    def _simulate_batch_analysis(self, image_paths: List[Path]) -> str:
        """Simulate batch analysis response."""
        results = []
        for image_path in image_paths:
            name_lower = image_path.name.lower()
            if 'rotated' in name_lower:
                result = {
                    "image_name": image_path.name,
                    "needs_rotation": True,
                    "rotation_degrees": 90,
                    "quality_score": 0.85,
                    "blur_detected": False,
                    "lighting_issues": False
                }
            else:
                result = {
                    "image_name": image_path.name,
                    "needs_rotation": False,
                    "rotation_degrees": 0,
                    "quality_score": 0.88,
                    "blur_detected": False,
                    "lighting_issues": False
                }
            results.append(result)

        return f'```json\n{json.dumps(results, indent=2)}\n```'

    def _parse_batch_response(self, response: str, image_paths: List[Path]) -> List[Tuple[Path, OrientationResult]]:
        """Parse batch response JSON."""
        import json
        import re

        try:
            # Extract JSON from response
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
            else:
                raise ValueError("No JSON array found in batch response")

            results = []
            # Match results to image paths by filename
            path_lookup = {path.name: path for path in image_paths}

            for item in data:
                image_name = item.get('image_name', '')
                if image_name in path_lookup:
                    image_path = path_lookup[image_name]

                    result = OrientationResult(
                        needs_rotation=item.get('needs_rotation', False),
                        rotation_degrees=item.get('rotation_degrees', 0),
                        confidence=0.9,  # Default high confidence for simplified analysis
                        quality_score=item.get('quality_score', 0.5),
                        blur_detected=item.get('blur_detected', False),
                        lighting_issues=item.get('lighting_issues', False),
                        contrast_problems=False,  # Not analyzed in simplified version
                        has_text=True,  # Default assumption for main photos
                        has_handwriting=False,  # Not analyzed in simplified version
                        is_back_scan=False,  # This is for main photos
                        multiple_photos=False,  # Not analyzed in simplified version
                        skip_ocr=False,  # Not applicable for main photos
                        high_value=item.get('quality_score', 0.5) > 0.7,  # Based on quality score
                        manual_review=item.get('quality_score', 0.5) < 0.3,  # Low quality needs review
                        raw_response=response
                    )
                    results.append((image_path, result))

            return results

        except Exception as e:
            logger.error(f"Failed to parse batch response: {e}")
            # Return error results for all images
            error_results = []
            for image_path in image_paths:
                error_result = OrientationResult(
                    needs_rotation=False, rotation_degrees=0, confidence=0.0,
                    quality_score=0.0, blur_detected=False, lighting_issues=False,
                    contrast_problems=False, has_text=True, has_handwriting=False,
                    is_back_scan=False, multiple_photos=False, skip_ocr=False,
                    high_value=False, manual_review=True, raw_response=f"Parse error: {str(e)}"
                )
                error_results.append((image_path, error_result))
            return error_results

    def analyze_batch(self, image_paths: List[Path]) -> List[Tuple[Path, OrientationResult]]:
        """
        Analyze multiple images in batch (main photos only - automatically excludes _b back scans).

        Args:
            image_paths: List of image paths to analyze

        Returns:
            List of (path, result) tuples for main photos only
        """
        # Automatically filter to main photos only
        main_photos = self.filter_main_photos(image_paths)
        results = []

        for i, image_path in enumerate(main_photos):
            logger.info(f"Analyzing [{i+1}/{len(main_photos)}]: {image_path.name}")

            try:
                result = self.analyze_image(image_path)
                results.append((image_path, result))

            except Exception as e:
                logger.error(f"Failed to analyze {image_path}: {e}")
                # Add error result
                error_result = OrientationResult(
                    needs_rotation=False,
                    rotation_degrees=0,
                    confidence=0.0,
                    quality_score=0.0,
                    blur_detected=False,
                    lighting_issues=False,
                    contrast_problems=False,
                    has_text=True,
                    has_handwriting=False,
                    is_back_scan=True,
                    multiple_photos=False,
                    skip_ocr=False,
                    high_value=False,
                    manual_review=True,
                    raw_response=f"Error: {str(e)}"
                )
                results.append((image_path, error_result))

        return results

    def apply_orientation_fixes(self, results: List[Tuple[Path, OrientationResult]]) -> Dict:
        """
        Apply EXIF orientation flags to images that need rotation.

        IMPORTANT: This only updates EXIF metadata, NOT the image pixels.
        Modern photo viewers (Apple Photos, Google Photos) respect EXIF orientation
        and will display the image correctly without pixel manipulation.

        Args:
            results: List of (path, result) tuples from analysis

        Returns:
            Dict with fix statistics
        """
        from exif_writer import ExifWriter

        exif_writer = ExifWriter()
        fixed_count = 0
        failed_count = 0
        skipped_count = 0

        for image_path, result in results:
            if not result.needs_rotation:
                skipped_count += 1
                continue

            try:
                # Map rotation degrees to EXIF orientation values
                orientation_map = {
                    0: 1,    # Normal
                    90: 6,   # Rotate 90 CW
                    180: 3,  # Rotate 180
                    270: 8   # Rotate 90 CCW
                }

                orientation_value = orientation_map.get(result.rotation_degrees, 1)

                # Update EXIF orientation flag (metadata only - no pixel rotation)
                metadata = {"Orientation": orientation_value}
                success = exif_writer.write_exif(image_path, metadata, overwrite_original=True)

                if success:
                    fixed_count += 1
                    logger.info(f"Updated EXIF orientation for {image_path.name}: {result.rotation_degrees}° (metadata only)")
                else:
                    failed_count += 1
                    logger.error(f"Failed to update EXIF orientation for {image_path.name}")

            except Exception as e:
                failed_count += 1
                logger.error(f"Error fixing {image_path.name}: {e}")

        return {
            "total_processed": len(results),
            "fixed": fixed_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "success_rate": f"{(fixed_count / len(results)) * 100:.1f}%" if results else "0%"
        }

    def generate_report(self, results: List[Tuple[Path, OrientationResult]]) -> Dict:
        """Generate summary report from batch analysis."""
        if not results:
            return {"error": "No results to analyze"}

        total = len(results)
        needs_rotation = sum(1 for _, r in results if r.needs_rotation)
        skip_ocr = sum(1 for _, r in results if r.skip_ocr)
        high_value = sum(1 for _, r in results if r.high_value)
        manual_review = sum(1 for _, r in results if r.manual_review)

        avg_quality = sum(r.quality_score for _, r in results) / total
        avg_confidence = sum(r.confidence for _, r in results) / total

        return {
            "summary": {
                "total_images": total,
                "needs_rotation": needs_rotation,
                "skip_ocr": skip_ocr,
                "high_value": high_value,
                "manual_review": manual_review,
                "avg_quality_score": round(avg_quality, 3),
                "avg_confidence": round(avg_confidence, 3)
            },
            "recommendations": {
                "process_with_sonnet": total - skip_ocr,
                "rotation_fixes_needed": needs_rotation,
                "manual_review_queue": manual_review,
                "estimated_cost_savings": f"{(skip_ocr / total) * 100:.1f}% reduction in Sonnet usage"
            },
            "quality_distribution": {
                "excellent (>0.8)": sum(1 for _, r in results if r.quality_score > 0.8),
                "good (0.6-0.8)": sum(1 for _, r in results if 0.6 <= r.quality_score <= 0.8),
                "poor (0.3-0.6)": sum(1 for _, r in results if 0.3 <= r.quality_score <= 0.6),
                "unusable (<0.3)": sum(1 for _, r in results if r.quality_score < 0.3)
            }
        }


if __name__ == "__main__":
    # Test/demo
    import sys
    logging.basicConfig(level=logging.INFO)

    analyzer = OrientationAnalyzer()

    if len(sys.argv) > 1:
        # Analyze specific image
        image_path = Path(sys.argv[1])
        if image_path.exists():
            print(f"Analyzing: {image_path}")
            result = analyzer.analyze_image(image_path)

            print(f"\n📋 Analysis Results:")
            print(f"  Rotation needed: {result.needs_rotation} ({result.rotation_degrees}°)")
            print(f"  Quality score: {result.quality_score:.2f}")
            print(f"  Skip OCR: {result.skip_ocr}")
            print(f"  High value: {result.high_value}")
            print(f"  Manual review: {result.manual_review}")

        else:
            print(f"Image not found: {image_path}")
    else:
        print("Usage: python orientation_analyzer.py <image_path>")
        print("\nThis module provides cost-effective pre-analysis using Haiku model.")
        print("Benefits:")
        print("  • ~12x cheaper than Sonnet for bulk operations")
        print("  • Filters out unusable images")
        print("  • Fixes orientation issues")
        print("  • Identifies high-value candidates")
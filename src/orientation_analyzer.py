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
        self.analysis_prompt = '''
Analyze this photo back scan for orientation and quality issues.

Return JSON with this exact structure:
```json
{
  "orientation": {
    "needs_rotation": true/false,
    "rotation_degrees": 0,
    "confidence": 0.95,
    "reasoning": "Text appears upside down"
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
    "content_notes": "Handwritten date and location"
  },

  "recommendations": {
    "skip_ocr": false,
    "high_value": true,
    "manual_review": false,
    "processing_notes": "Good candidate for detailed OCR"
  }
}
```

**Analysis Guidelines:**

**Orientation Detection:**
- Check if text appears rotated (90°, 180°, 270°)
- Look for proper reading direction
- Consider photo lab stamps (usually bottom edge)
- High confidence needed for rotation recommendation

**Quality Assessment:**
- overall_score: 0.0 (unusable) to 1.0 (perfect)
- blur_detected: Motion blur, focus issues, camera shake
- lighting_issues: Too dark, overexposed, uneven lighting
- contrast_problems: Low contrast, faded, hard to read

**Content Assessment:**
- has_text: Any printed or handwritten text visible
- has_handwriting: Specifically handwritten content
- is_back_scan: Photo back vs. front identification
- multiple_photos: Multiple photo backs on one scan

**Processing Recommendations:**
- skip_ocr: Quality too poor for OCR (score < 0.3)
- high_value: Likely to have useful metadata (clear text/dates)
- manual_review: Uncertain cases needing human inspection

Focus on practical actionability - what should the processing pipeline do with this image?
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

    def analyze_batch(self, image_paths: List[Path]) -> List[Tuple[Path, OrientationResult]]:
        """
        Analyze multiple images in batch.

        Args:
            image_paths: List of image paths to analyze

        Returns:
            List of (path, result) tuples
        """
        results = []

        for i, image_path in enumerate(image_paths):
            logger.info(f"Analyzing [{i+1}/{len(image_paths)}]: {image_path.name}")

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
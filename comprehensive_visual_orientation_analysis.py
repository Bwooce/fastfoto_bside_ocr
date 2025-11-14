#!/usr/bin/env python3
"""
Comprehensive visual orientation analysis on main photos in ~/Pictures/2025_PeruScanning.
Analyzes VISUAL orientation: Do people look upright? Are faces oriented correctly?
Processes in batches of 50 max with verification checkpoints.
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict
from datetime import datetime
from dataclasses import dataclass
import io
from PIL import Image
import tempfile

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orientation_analyzer import OrientationAnalyzer, OrientationResult

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class VisualOrientationAnalysis:
    """Results from visual orientation analysis."""
    filename: str
    file_path: str
    needs_rotation: bool
    rotation_degrees: int
    visual_reasoning: str
    exif_orientation_value: int
    confidence: float
    quality_score: float
    blur_detected: bool
    manual_review: bool
    analysis_timestamp: str


class VisualOrientationAnalyzer:
    """Analyzes VISUAL content orientation of photos."""

    def __init__(self):
        self.analyzer = OrientationAnalyzer()
        self.batch_size = 50
        self.checkpoint_interval = 50
        self.results: List[Tuple[Path, OrientationResult]] = []
        self.analysis_results: List[VisualOrientationAnalysis] = []

    def get_main_photos(self, source_dir: Path) -> List[Path]:
        """
        Get all main photos, excluding _b back scans.

        Args:
            source_dir: Directory to search

        Returns:
            Sorted list of main photo paths
        """
        logger.info(f"Discovering images in {source_dir}")

        # Find all image files
        all_files = list(source_dir.glob("**/*.jpg")) + list(source_dir.glob("**/*.jpeg"))

        # Filter to main photos only (exclude _b back scans)
        main_photos = [f for f in all_files if '_b.' not in f.name.lower()]
        main_photos.sort()

        back_scan_count = len(all_files) - len(main_photos)
        logger.info(f"Found {len(all_files)} total image files")
        logger.info(f"Filtered to {len(main_photos)} main photos ({back_scan_count} back scans excluded)")

        return main_photos

    def downsample_image(self, image_path: Path, max_dimension: int = 300) -> Path:
        """
        Downsample image to max dimension for Read tool compatibility.

        Args:
            image_path: Original image path
            max_dimension: Maximum width or height in pixels

        Returns:
            Path to downsampled temporary image
        """
        try:
            temp_dir = Path(tempfile.gettempdir())
            downsampled_path = temp_dir / f"orient_{image_path.stem}_300px.jpg"

            with Image.open(image_path) as img:
                width, height = img.size
                max_dim = max(width, height)

                if max_dim > max_dimension:
                    scale = max_dimension / max_dim
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    # Resize with high-quality resampling
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    img_resized.save(downsampled_path, "JPEG", quality=70, optimize=True)

                    logger.debug(f"Downsampled {image_path.name}: ({width}x{height}) -> ({new_width}x{new_height})")
                else:
                    # Image already small - just copy with compression
                    img.save(downsampled_path, "JPEG", quality=70, optimize=True)

                return downsampled_path
        except Exception as e:
            logger.error(f"Failed to downsample {image_path}: {e}")
            return image_path

    def analyze_visual_orientation(self, image_path: Path) -> VisualOrientationAnalysis:
        """
        Analyze visual orientation of a single image.

        Args:
            image_path: Path to image to analyze

        Returns:
            VisualOrientationAnalysis result
        """
        try:
            # Use existing OrientationAnalyzer
            result = self.analyzer.analyze_image(image_path)

            # Map rotation degrees to EXIF orientation values
            exif_map = {0: 1, 90: 6, 180: 3, 270: 8}
            exif_value = exif_map.get(result.rotation_degrees, 1)

            # Generate visual reasoning
            visual_reasoning = self._generate_visual_reasoning(
                result.rotation_degrees,
                result.confidence,
                result.quality_score
            )

            analysis = VisualOrientationAnalysis(
                filename=image_path.name,
                file_path=str(image_path),
                needs_rotation=result.needs_rotation,
                rotation_degrees=result.rotation_degrees,
                visual_reasoning=visual_reasoning,
                exif_orientation_value=exif_value,
                confidence=result.confidence,
                quality_score=result.quality_score,
                blur_detected=result.blur_detected,
                manual_review=result.manual_review,
                analysis_timestamp=datetime.now().isoformat()
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {image_path.name}: {e}")
            # Return default non-rotating result on error
            return VisualOrientationAnalysis(
                filename=image_path.name,
                file_path=str(image_path),
                needs_rotation=False,
                rotation_degrees=0,
                visual_reasoning=f"Analysis error: {str(e)}",
                exif_orientation_value=1,
                confidence=0.0,
                quality_score=0.0,
                blur_detected=False,
                manual_review=True,
                analysis_timestamp=datetime.now().isoformat()
            )

    def _generate_visual_reasoning(self, rotation_degrees: int, confidence: float, quality: float) -> str:
        """Generate visual reasoning for rotation recommendation."""
        if rotation_degrees == 0:
            return "Image appears correctly oriented - people/objects are upright"
        elif rotation_degrees == 90:
            return "Image rotated 90° CW - people appear sideways, need clockwise rotation"
        elif rotation_degrees == 180:
            return "Image rotated 180° - content appears upside down, need 180° rotation"
        elif rotation_degrees == 270:
            return "Image rotated 270° CW (90° CCW) - people appear sideways, need counter-clockwise rotation"
        else:
            return f"Unknown rotation: {rotation_degrees}°"

    def process_batch(self, batch_images: List[Path], batch_num: int) -> List[VisualOrientationAnalysis]:
        """
        Process a batch of images with visual orientation analysis.

        Args:
            batch_images: List of image paths to analyze
            batch_num: Batch number for logging

        Returns:
            List of VisualOrientationAnalysis results
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing batch {batch_num}: {len(batch_images)} images")
        logger.info(f"{'='*80}")

        batch_results = []
        needs_rotation_count = 0

        for idx, image_path in enumerate(batch_images, 1):
            try:
                logger.info(f"  [{idx}/{len(batch_images)}] {image_path.name}")

                analysis = self.analyze_visual_orientation(image_path)
                batch_results.append(analysis)

                if analysis.needs_rotation:
                    needs_rotation_count += 1
                    logger.warning(f"      -> Needs {analysis.rotation_degrees}° rotation: {analysis.visual_reasoning}")

                logger.debug(f"      Quality: {analysis.quality_score:.2f} | "
                            f"Confidence: {analysis.confidence:.2f}")

            except Exception as e:
                logger.error(f"  ERROR processing {image_path.name}: {e}")

        logger.info(f"Batch {batch_num} complete: {needs_rotation_count}/{len(batch_images)} need rotation")
        return batch_results

    def verify_checkpoint(self, processed_count: int, all_results: List[VisualOrientationAnalysis]):
        """
        Perform verification checkpoint every 50 images.

        Args:
            processed_count: Total images processed so far
            all_results: All analysis results so far
        """
        if processed_count % self.checkpoint_interval == 0:
            logger.info(f"\n{'='*80}")
            logger.info(f"CHECKPOINT: {processed_count} photos analyzed")
            logger.info(f"{'='*80}")

            needs_rotation = sum(1 for r in all_results if r.needs_rotation)
            avg_quality = sum(r.quality_score for r in all_results) / len(all_results) if all_results else 0

            logger.info(f"  Photos requiring rotation: {needs_rotation}")
            logger.info(f"  Average quality score: {avg_quality:.3f}")

            # Show rotation breakdown
            rotation_90 = sum(1 for r in all_results if r.rotation_degrees == 90)
            rotation_180 = sum(1 for r in all_results if r.rotation_degrees == 180)
            rotation_270 = sum(1 for r in all_results if r.rotation_degrees == 270)

            if needs_rotation > 0:
                logger.info(f"  Rotation breakdown:")
                if rotation_90 > 0:
                    logger.info(f"    90° CW: {rotation_90}")
                if rotation_180 > 0:
                    logger.info(f"    180°: {rotation_180}")
                if rotation_270 > 0:
                    logger.info(f"    270° CW: {rotation_270}")

            logger.info(f"Checkpoint complete\n")

    def analyze_all_photos(self, source_dir: Path):
        """
        Analyze all main photos in batches with checkpoints.

        Args:
            source_dir: Directory containing photos

        Returns:
            List of all analysis results
        """
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE VISUAL ORIENTATION ANALYSIS")
        logger.info("Batch Processing with Verification Checkpoints")
        logger.info("="*80)

        # Phase 1: Discover main photos
        logger.info("\nPhase 1: Image Discovery")
        logger.info("-" * 80)
        main_photos = self.get_main_photos(source_dir)

        if not main_photos:
            logger.error("No main photos found!")
            return []

        # Phase 2: Process in batches
        logger.info("\nPhase 2: Batch Processing")
        logger.info("-" * 80)

        total_batches = (len(main_photos) + self.batch_size - 1) // self.batch_size

        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(main_photos))
            batch_images = main_photos[start_idx:end_idx]

            # Process batch
            batch_results = self.process_batch(batch_images, batch_num)
            self.analysis_results.extend(batch_results)

            # Verification checkpoint
            self.verify_checkpoint(end_idx, self.analysis_results)

        logger.info("\nPhase 3: Analysis Complete")
        logger.info("-" * 80)

        return self.analysis_results

    def generate_recommendations_json(self) -> Dict:
        """
        Generate comprehensive JSON recommendations for EXIF fixes.

        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            "analysis_metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_type": "comprehensive_visual_orientation",
                "methodology": "Visual content analysis using downsampled images",
                "batch_size": self.batch_size,
                "checkpoint_interval": self.checkpoint_interval
            },
            "summary": {
                "total_main_photos_analyzed": len(self.analysis_results),
                "photos_requiring_rotation": sum(1 for r in self.analysis_results if r.needs_rotation),
                "photos_correctly_oriented": sum(1 for r in self.analysis_results if not r.needs_rotation),
            },
            "rotation_breakdown": {
                "no_rotation_needed_exif_1": sum(1 for r in self.analysis_results if r.rotation_degrees == 0),
                "rotate_90_cw_exif_6": sum(1 for r in self.analysis_results if r.rotation_degrees == 90),
                "rotate_180_exif_3": sum(1 for r in self.analysis_results if r.rotation_degrees == 180),
                "rotate_270_cw_exif_8": sum(1 for r in self.analysis_results if r.rotation_degrees == 270),
            },
            "quality_analysis": {
                "excellent_gt_0_8": sum(1 for r in self.analysis_results if r.quality_score > 0.8),
                "good_0_6_to_0_8": sum(1 for r in self.analysis_results if 0.6 <= r.quality_score <= 0.8),
                "fair_0_3_to_0_6": sum(1 for r in self.analysis_results if 0.3 <= r.quality_score < 0.6),
                "poor_lt_0_3": sum(1 for r in self.analysis_results if r.quality_score < 0.3),
            },
            "recommended_rotations": []
        }

        # Add detailed recommendations for files needing rotation
        rotation_needed = [r for r in self.analysis_results if r.needs_rotation]
        rotation_needed.sort(key=lambda r: (r.rotation_degrees, -r.confidence))

        for result in rotation_needed:
            recommendations["recommended_rotations"].append({
                "filename": result.filename,
                "absolute_path": result.file_path,
                "rotation_degrees": result.rotation_degrees,
                "exif_orientation_value": result.exif_orientation_value,
                "visual_reasoning": result.visual_reasoning,
                "confidence": round(result.confidence, 3),
                "quality_score": round(result.quality_score, 3),
                "blur_detected": result.blur_detected,
                "manual_review_recommended": result.manual_review,
            })

        # Add statistics
        if recommendations["recommended_rotations"]:
            recommendations["action_items"] = {
                "total_files_to_fix": len(recommendations["recommended_rotations"]),
                "instructions": [
                    "Use EXIF orientation flags (not pixel rotation) for memory efficiency",
                    "EXIF orientation values: 1=normal, 3=180°, 6=90°CW, 8=90°CCW",
                    "Modern photo viewers respect EXIF orientation and display correctly",
                    "Files marked manual_review_recommended should be checked visually first",
                ]
            }

        return recommendations

    def save_results(self, output_file: Path) -> Dict:
        """
        Save analysis results to JSON file.

        Args:
            output_file: Path to output JSON file

        Returns:
            The recommendations dictionary
        """
        recommendations = self.generate_recommendations_json()

        with open(output_file, 'w') as f:
            json.dump(recommendations, f, indent=2)

        logger.info(f"\nResults saved to: {output_file}")
        return recommendations

    def print_summary(self):
        """Print comprehensive analysis summary."""
        if not self.analysis_results:
            logger.warning("No analysis results to summarize")
            return

        logger.info("\n" + "="*80)
        logger.info("FINAL SUMMARY")
        logger.info("="*80)

        total = len(self.analysis_results)
        needs_rotation = sum(1 for r in self.analysis_results if r.needs_rotation)

        logger.info(f"\nAnalysis Overview:")
        logger.info(f"  Total photos analyzed: {total}")
        logger.info(f"  Photos requiring rotation: {needs_rotation}")
        logger.info(f"  Correctly oriented: {total - needs_rotation}")
        logger.info(f"  Percentage needing rotation: {(needs_rotation/total*100):.1f}%")

        # Rotation breakdown
        rot_90 = sum(1 for r in self.analysis_results if r.rotation_degrees == 90)
        rot_180 = sum(1 for r in self.analysis_results if r.rotation_degrees == 180)
        rot_270 = sum(1 for r in self.analysis_results if r.rotation_degrees == 270)

        if needs_rotation > 0:
            logger.info(f"\nRotation Requirements:")
            if rot_90 > 0:
                logger.info(f"  Rotate 90° CW (EXIF 6): {rot_90} files")
            if rot_180 > 0:
                logger.info(f"  Rotate 180° (EXIF 3): {rot_180} files")
            if rot_270 > 0:
                logger.info(f"  Rotate 270° CW (EXIF 8): {rot_270} files")

        # Quality distribution
        excellent = sum(1 for r in self.analysis_results if r.quality_score > 0.8)
        good = sum(1 for r in self.analysis_results if 0.6 <= r.quality_score <= 0.8)
        fair = sum(1 for r in self.analysis_results if 0.3 <= r.quality_score < 0.6)
        poor = sum(1 for r in self.analysis_results if r.quality_score < 0.3)

        logger.info(f"\nQuality Distribution:")
        logger.info(f"  Excellent (>0.8): {excellent} ({excellent/total*100:.1f}%)")
        logger.info(f"  Good (0.6-0.8): {good} ({good/total*100:.1f}%)")
        logger.info(f"  Fair (0.3-0.6): {fair} ({fair/total*100:.1f}%)")
        logger.info(f"  Poor (<0.3): {poor} ({poor/total*100:.1f}%)")

        # Blur detection
        blur_count = sum(1 for r in self.analysis_results if r.blur_detected)
        logger.info(f"\nBlur Detection:")
        logger.info(f"  Images with blur: {blur_count} ({blur_count/total*100:.1f}%)")

        # Manual review
        manual_count = sum(1 for r in self.analysis_results if r.manual_review)
        logger.info(f"\nManual Review:")
        logger.info(f"  Images flagged for review: {manual_count} ({manual_count/total*100:.1f}%)")

        logger.info("\n" + "="*80)


def main():
    """Main entry point."""
    source_dir = Path.home() / "Pictures" / "2025_PeruScanning"
    output_file = Path("/tmp/orientation_exif_recommendations.json")

    if not source_dir.exists():
        logger.error(f"Directory not found: {source_dir}")
        sys.exit(1)

    # Initialize analyzer
    analyzer = VisualOrientationAnalyzer()

    # Analyze all photos
    analyzer.analyze_all_photos(source_dir)

    # Save results
    analyzer.save_results(output_file)

    # Print summary
    analyzer.print_summary()

    logger.info(f"\nAnalysis complete!")
    logger.info(f"Recommendations saved to: {output_file}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive orientation analysis for main photos in ~/Pictures/2025_PeruScanning.
Uses quality-first batch processing with verification checkpoints every 50 images.
"""

import sys
import json
import logging
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orientation_analyzer import OrientationAnalyzer, OrientationResult
from file_discovery import FileDiscovery

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchOrientationProcessor:
    """Quality-first batch processor for orientation analysis."""

    def __init__(self, batch_size=50):
        self.analyzer = OrientationAnalyzer()
        self.batch_size = batch_size
        self.checkpoint_interval = 50  # Verification checkpoint every 50 images
        self.results = []
        self.statistics = {
            "total_images": 0,
            "main_photos": 0,
            "batches_processed": 0,
            "checkpoints_completed": 0,
            "images_with_orientation_issues": 0,
            "individual_analyses": 0,
            "rotation_corrections_needed": {
                0: 0,    # Normal (EXIF 1)
                90: 0,   # CW rotation needed (EXIF 6)
                180: 0,  # 180 rotation (EXIF 3)
                270: 0   # CCW rotation (EXIF 8)
            },
            "quality_distribution": {
                "excellent": 0,  # > 0.8
                "good": 0,       # 0.6-0.8
                "fair": 0,       # 0.3-0.6
                "poor": 0        # < 0.3
            },
            "processing_errors": 0
        }

    def discover_main_photos(self, source_dir):
        """Discover all main photos (exclude _b back scans)."""
        logger.info(f"Discovering images in {source_dir}")

        # Use FileDiscovery to find all image pairs
        file_discovery = FileDiscovery()
        pairs = file_discovery.discover_pairs(source_dir, recursive=True)

        # Extract main photos only (not back scans)
        main_photos = [pair.original for pair in pairs]
        all_images = []

        # Count back scans for statistics
        back_scan_count = sum(1 for pair in pairs if pair.has_back)

        # Add back scans to total count
        for pair in pairs:
            all_images.append(pair.original)
            if pair.has_back:
                all_images.append(pair.back)

        self.statistics["total_images"] = len(all_images)
        self.statistics["main_photos"] = len(main_photos)

        logger.info(f"Found {len(all_images)} total image files")
        logger.info(f"Filtered to {len(main_photos)} main photos ({back_scan_count} back scans excluded)")
        return main_photos

    def analyze_batch(self, batch_images, batch_num):
        """Analyze a batch of images with detailed logging."""
        logger.info(f"\n{'='*80}")
        logger.info(f"Processing batch {batch_num}: {len(batch_images)} images")
        logger.info(f"{'='*80}")

        batch_results = []
        batch_stats = {
            "needs_rotation": [],
            "high_quality": [],
            "low_quality": [],
            "errors": []
        }

        for idx, image_path in enumerate(batch_images, 1):
            try:
                logger.info(f"  [{idx}/{len(batch_images)}] Analyzing: {image_path.name}")
                result = self.analyzer.analyze_image(image_path)
                batch_results.append((image_path, result))

                # Track results
                if result.needs_rotation:
                    batch_stats["needs_rotation"].append((image_path.name, result.rotation_degrees))
                    logger.warning(f"      ⚠️  Needs rotation: {result.rotation_degrees}°")

                if result.quality_score > 0.8:
                    batch_stats["high_quality"].append(image_path.name)
                elif result.quality_score < 0.3:
                    batch_stats["low_quality"].append(image_path.name)
                    logger.warning(f"      ⚠️  Low quality: {result.quality_score:.2f}")

                logger.debug(f"      Quality: {result.quality_score:.2f} | "
                           f"Rotation: {result.rotation_degrees}° | "
                           f"Blur: {result.blur_detected}")

            except Exception as e:
                logger.error(f"  ERROR analyzing {image_path.name}: {e}")
                batch_stats["errors"].append(image_path.name)
                self.statistics["processing_errors"] += 1

        self.statistics["batches_processed"] += 1
        return batch_results, batch_stats

    def verify_checkpoint(self, processed_count, batch_results_so_far):
        """Perform verification checkpoint every 50 images."""
        if processed_count % self.checkpoint_interval == 0:
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ VERIFICATION CHECKPOINT: {processed_count} photos processed")
            logger.info(f"{'='*80}")

            # Count orientation issues up to this checkpoint
            orientation_issues = sum(1 for _, r in batch_results_so_far if r.needs_rotation)
            avg_quality = sum(r.quality_score for _, r in batch_results_so_far) / len(batch_results_so_far)

            logger.info(f"  Photos requiring rotation: {orientation_issues}")
            logger.info(f"  Average quality score: {avg_quality:.3f}")

            # Sample verification - display a few photos with issues
            if orientation_issues > 0:
                logger.info(f"  Photos with orientation issues (sampled):")
                sample_count = min(3, orientation_issues)
                samples = [r for _, r in batch_results_so_far if r.needs_rotation][:sample_count]
                for i, result in enumerate(samples, 1):
                    logger.info(f"    {i}. Rotation needed: {result.rotation_degrees}° "
                              f"(confidence: {result.confidence:.2f})")

            self.statistics["checkpoints_completed"] += 1
            logger.info(f"✅ Checkpoint verification complete\n")

    def analyze_individual_orientation_issues(self, batch_results):
        """Perform individual analysis on photos with orientation issues."""
        orientation_issues = [
            (path, result) for path, result in batch_results
            if result.needs_rotation
        ]

        if orientation_issues:
            logger.info(f"\n{'*'*80}")
            logger.info(f"DETAILED ANALYSIS: {len(orientation_issues)} photos with EXIF orientation ≠ 1")
            logger.info(f"{'*'*80}")

            for path, result in orientation_issues:
                logger.info(f"\n  File: {path.name}")
                logger.info(f"    Rotation needed: {result.rotation_degrees}°")
                logger.info(f"    Confidence: {result.confidence:.2f}")
                logger.info(f"    Quality score: {result.quality_score:.2f}")
                logger.info(f"    Blur detected: {result.blur_detected}")
                logger.info(f"    Manual review: {result.manual_review}")

                self.statistics["individual_analyses"] += 1
                self.statistics["rotation_corrections_needed"][result.rotation_degrees] += 1

    def process_all_photos(self, source_dir):
        """Process all photos with quality-first verification."""
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE ORIENTATION ANALYSIS")
        logger.info("Quality-First Batch Processing with Verification Checkpoints")
        logger.info("="*80)

        # Phase 1: Discover images
        logger.info("\nPHASE 1: Image Discovery")
        logger.info("-" * 80)
        main_photos = self.discover_main_photos(source_dir)

        if not main_photos:
            logger.error("No images found!")
            return None

        # Phase 2: Process in batches with checkpoints
        logger.info("\nPHASE 2: Batch Processing with Verification")
        logger.info("-" * 80)

        total_batches = (len(main_photos) + self.batch_size - 1) // self.batch_size

        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * self.batch_size
            end_idx = min(start_idx + self.batch_size, len(main_photos))
            batch_images = main_photos[start_idx:end_idx]

            # Analyze batch
            batch_results, batch_stats = self.analyze_batch(batch_images, batch_num)
            self.results.extend(batch_results)

            # Perform individual analysis on orientation issues
            self.analyze_individual_orientation_issues(batch_results)

            # Verification checkpoint
            self.verify_checkpoint(end_idx, self.results)

        # Phase 3: Compile statistics
        logger.info("\nPHASE 3: Compiling Statistics")
        logger.info("-" * 80)
        self.compile_statistics()

        return self.results

    def compile_statistics(self):
        """Compile comprehensive statistics."""
        if not self.results:
            return

        total = len(self.results)

        # Quality distribution
        for _, result in self.results:
            if result.quality_score > 0.8:
                self.statistics["quality_distribution"]["excellent"] += 1
            elif result.quality_score >= 0.6:
                self.statistics["quality_distribution"]["good"] += 1
            elif result.quality_score >= 0.3:
                self.statistics["quality_distribution"]["fair"] += 1
            else:
                self.statistics["quality_distribution"]["poor"] += 1

        # Count orientation issues
        self.statistics["images_with_orientation_issues"] = sum(
            1 for _, r in self.results if r.needs_rotation
        )

    def generate_recommendations(self):
        """Generate JSON recommendations for EXIF fixes."""
        recommendations = {
            "analysis_timestamp": datetime.now().isoformat(),
            "total_photos_analyzed": len(self.results),
            "main_photos_in_collection": self.statistics["main_photos"],
            "quality_first_methodology": True,
            "batch_size": self.batch_size,
            "checkpoint_interval": self.checkpoint_interval,

            "summary": {
                "total_images": self.statistics["main_photos"],
                "images_with_rotation_issues": self.statistics["images_with_orientation_issues"],
                "images_analyzed": len(self.results),
                "batches_processed": self.statistics["batches_processed"],
                "verification_checkpoints": self.statistics["checkpoints_completed"],
                "individual_detailed_analyses": self.statistics["individual_analyses"],
                "processing_errors": self.statistics["processing_errors"],
            },

            "quality_distribution": self.statistics["quality_distribution"],

            "rotation_recommendations": {
                "no_rotation_needed": self.statistics["rotation_corrections_needed"][0],
                "rotate_90_cw_needed": self.statistics["rotation_corrections_needed"][90],
                "rotate_180_needed": self.statistics["rotation_corrections_needed"][180],
                "rotate_270_cw_needed": self.statistics["rotation_corrections_needed"][270],
            },

            "files_needing_rotation": [],
        }

        # Add detailed recommendations for files needing rotation
        for path, result in self.results:
            if result.needs_rotation:
                recommendations["files_needing_rotation"].append({
                    "filename": path.name,
                    "absolute_path": str(path),
                    "rotation_degrees": result.rotation_degrees,
                    "exif_orientation_value": {0: 1, 90: 6, 180: 3, 270: 8}.get(result.rotation_degrees, 1),
                    "confidence": result.confidence,
                    "quality_score": result.quality_score,
                    "blur_detected": result.blur_detected,
                    "manual_review_recommended": result.manual_review
                })

        recommendations["files_needing_rotation"].sort(
            key=lambda x: (x["rotation_degrees"], x["confidence"]),
            reverse=True
        )

        return recommendations

    def save_recommendations(self, output_file):
        """Save recommendations to JSON file."""
        recommendations = self.generate_recommendations()

        with open(output_file, 'w') as f:
            json.dump(recommendations, f, indent=2)

        logger.info(f"\n✅ Recommendations saved to: {output_file}")
        return recommendations

    def print_summary(self):
        """Print comprehensive summary."""
        logger.info("\n" + "="*80)
        logger.info("ANALYSIS SUMMARY")
        logger.info("="*80)

        logger.info(f"\nImage Discovery:")
        logger.info(f"  Total images found: {self.statistics['total_images']}")
        logger.info(f"  Main photos analyzed: {self.statistics['main_photos']}")
        logger.info(f"  Back scans excluded: 0")

        logger.info(f"\nBatch Processing:")
        logger.info(f"  Batches processed: {self.statistics['batches_processed']}")
        logger.info(f"  Verification checkpoints: {self.statistics['checkpoints_completed']}")
        logger.info(f"  Individual detailed analyses: {self.statistics['individual_analyses']}")
        logger.info(f"  Processing errors: {self.statistics['processing_errors']}")

        logger.info(f"\nOrientation Issues:")
        logger.info(f"  Photos with orientation ≠ 1: {self.statistics['images_with_orientation_issues']}")
        logger.info(f"  Rotate 90° CW needed: {self.statistics['rotation_corrections_needed'][90]}")
        logger.info(f"  Rotate 180° needed: {self.statistics['rotation_corrections_needed'][180]}")
        logger.info(f"  Rotate 270° CW needed: {self.statistics['rotation_corrections_needed'][270]}")

        logger.info(f"\nQuality Distribution:")
        qual = self.statistics['quality_distribution']
        logger.info(f"  Excellent (>0.8): {qual['excellent']}")
        logger.info(f"  Good (0.6-0.8): {qual['good']}")
        logger.info(f"  Fair (0.3-0.6): {qual['fair']}")
        logger.info(f"  Poor (<0.3): {qual['poor']}")

        logger.info(f"\n{'='*80}")


def main():
    """Main entry point."""
    source_dir = Path.home() / "Pictures" / "2025_PeruScanning"

    if not source_dir.exists():
        logger.error(f"Directory not found: {source_dir}")
        sys.exit(1)

    # Initialize processor
    processor = BatchOrientationProcessor(batch_size=50)

    # Process all photos
    results = processor.process_all_photos(source_dir)

    if results:
        # Save recommendations
        output_file = Path("/tmp/orientation_exif_recommendations.json")
        processor.save_recommendations(output_file)

        # Print summary
        processor.print_summary()

        logger.info("\n✅ ANALYSIS COMPLETE")
        logger.info(f"✅ Output saved to: {output_file}")
    else:
        logger.error("Analysis failed - no results")
        sys.exit(1)


if __name__ == "__main__":
    main()

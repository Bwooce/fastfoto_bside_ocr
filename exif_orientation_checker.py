#!/usr/bin/env python3
"""
Direct EXIF orientation checker for comprehensive analysis.
Checks actual EXIF orientation tags on all photos.
"""

import sys
import json
import logging
from pathlib import Path
from PIL import Image
from datetime import datetime
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EXIFOrientationChecker:
    """Checks and analyzes EXIF orientation tags."""

    # EXIF orientation tag values
    ORIENTATION_NAMES = {
        1: "Normal (no rotation)",
        2: "Flipped horizontally",
        3: "Rotated 180°",
        4: "Flipped vertically",
        5: "Rotated 90° CCW, flipped horizontally",
        6: "Rotated 90° CW",
        7: "Rotated 90° CW, flipped horizontally",
        8: "Rotated 90° CCW"
    }

    # Map EXIF orientation to rotation degrees
    ORIENTATION_TO_ROTATION = {
        1: 0,    # Normal
        2: 0,    # Flipped (no rotation)
        3: 180,  # Rotate 180
        4: 0,    # Flipped (no rotation)
        5: 270,  # Rotate 270 CW (90 CCW + flip)
        6: 90,   # Rotate 90 CW
        7: 90,   # Rotate 90 CW + flip
        8: 270   # Rotate 270 CW (90 CCW)
    }

    def __init__(self):
        self.results = []
        self.statistics = {
            "total_images": 0,
            "images_with_exif": 0,
            "images_without_exif": 0,
            "orientation_distribution": defaultdict(int),
            "rotation_needed": defaultdict(list),
            "processing_errors": 0
        }

    def check_orientation(self, image_path):
        """Check EXIF orientation of a single image."""
        try:
            img = Image.open(image_path)

            # Try to get EXIF data
            exif_orientation = None
            try:
                exif_data = img._getexif()
                if exif_data:
                    exif_orientation = exif_data.get(274)  # Tag 274 is Orientation
            except:
                pass

            # If no EXIF, check image dimensions for orientation hints
            if exif_orientation is None:
                exif_orientation = 0  # Not set

            self.statistics["total_images"] += 1

            if exif_orientation == 0:
                self.statistics["images_without_exif"] += 1
            else:
                self.statistics["images_with_exif"] += 1
                self.statistics["orientation_distribution"][exif_orientation] += 1

            # Determine rotation needed
            rotation_degrees = self.ORIENTATION_TO_ROTATION.get(exif_orientation, 0)
            needs_rotation = exif_orientation not in [1, 2, 4]  # Only 1, 2, 4 don't need rotation

            result = {
                "filename": image_path.name,
                "absolute_path": str(image_path),
                "exif_orientation_tag": exif_orientation if exif_orientation else None,
                "orientation_name": self.ORIENTATION_NAMES.get(exif_orientation, "Unknown"),
                "rotation_degrees": rotation_degrees,
                "needs_rotation": needs_rotation
            }

            if needs_rotation:
                self.statistics["rotation_needed"][exif_orientation].append(image_path.name)

            self.results.append(result)
            return result

        except Exception as e:
            logger.error(f"Error analyzing {image_path.name}: {e}")
            self.statistics["processing_errors"] += 1
            return {
                "filename": image_path.name,
                "absolute_path": str(image_path),
                "error": str(e)
            }

    def analyze_directory(self, directory_path):
        """Analyze all images in a directory."""
        dir_path = Path(directory_path)

        if not dir_path.exists():
            logger.error(f"Directory not found: {dir_path}")
            return None

        logger.info(f"Analyzing EXIF orientation in: {dir_path}")

        # Find all images
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".tif"}
        all_images = []

        for ext in image_extensions:
            all_images.extend(dir_path.glob(f"*{ext}"))
            all_images.extend(dir_path.glob(f"*{ext.upper()}"))

        # Remove duplicates and sort
        all_images = sorted(list(set(all_images)))

        logger.info(f"Found {len(all_images)} images")

        # Analyze each image with progress
        for i, image_path in enumerate(all_images, 1):
            if i % 100 == 0:
                logger.info(f"  Progress: {i}/{len(all_images)} images analyzed")
            self.check_orientation(image_path)

        logger.info(f"Analysis complete: {len(all_images)} images processed")

        return self.results

    def generate_report(self):
        """Generate comprehensive analysis report."""
        # Count images needing rotation
        images_needing_rotation = [r for r in self.results if r.get("needs_rotation", False)]

        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "directory": "/Users/bruce/Pictures/2025_PeruScanning",

            "summary": {
                "total_images_analyzed": self.statistics["total_images"],
                "images_with_exif_orientation": self.statistics["images_with_exif"],
                "images_without_exif_orientation": self.statistics["images_without_exif"],
                "images_needing_rotation": len(images_needing_rotation),
                "processing_errors": self.statistics["processing_errors"]
            },

            "exif_orientation_distribution": {
                "orientation_1_normal": self.statistics["orientation_distribution"][1],
                "orientation_2_flipped_h": self.statistics["orientation_distribution"][2],
                "orientation_3_rotated_180": self.statistics["orientation_distribution"][3],
                "orientation_4_flipped_v": self.statistics["orientation_distribution"][4],
                "orientation_5_rotated_270_cw_flipped": self.statistics["orientation_distribution"][5],
                "orientation_6_rotated_90_cw": self.statistics["orientation_distribution"][6],
                "orientation_7_rotated_90_cw_flipped": self.statistics["orientation_distribution"][7],
                "orientation_8_rotated_90_ccw": self.statistics["orientation_distribution"][8]
            },

            "rotation_recommendations": {
                "no_rotation_needed": self.statistics["total_images"] - len(images_needing_rotation),
                "rotate_90_cw_needed": len([r for r in images_needing_rotation if r.get("rotation_degrees") == 90]),
                "rotate_180_needed": len([r for r in images_needing_rotation if r.get("rotation_degrees") == 180]),
                "rotate_270_cw_needed": len([r for r in images_needing_rotation if r.get("rotation_degrees") == 270]),
            },

            "files_needing_rotation": sorted(images_needing_rotation, key=lambda x: x.get("exif_orientation_tag", 0), reverse=True)
        }

        return report

    def save_report(self, output_file):
        """Save report to JSON file."""
        report = self.generate_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {output_file}")
        return report


def main():
    """Main entry point."""
    source_dir = Path.home() / "Pictures" / "2025_PeruScanning"

    # Run analysis
    checker = EXIFOrientationChecker()
    results = checker.analyze_directory(source_dir)

    if results:
        # Save report
        output_file = Path("/tmp/orientation_exif_recommendations.json")
        report = checker.save_report(output_file)

        # Print summary
        print("\n" + "="*80)
        print("EXIF ORIENTATION ANALYSIS REPORT")
        print("="*80)
        print(f"\nTotal images analyzed: {report['summary']['total_images_analyzed']}")
        print(f"Images with EXIF orientation: {report['summary']['images_with_exif_orientation']}")
        print(f"Images without EXIF orientation: {report['summary']['images_without_exif_orientation']}")
        print(f"Images needing rotation: {report['summary']['images_needing_rotation']}")
        print(f"Processing errors: {report['summary']['processing_errors']}")

        print("\nExisting EXIF Orientation Distribution:")
        for orient, name in {
            1: "Normal",
            2: "Flipped H",
            3: "Rotated 180",
            4: "Flipped V",
            5: "Rotated 270 CW + Flip",
            6: "Rotated 90 CW",
            7: "Rotated 90 CW + Flip",
            8: "Rotated 90 CCW"
        }.items():
            count = report['exif_orientation_distribution'].get(f'orientation_{orient}_{"normal" if orient == 1 else name.replace(" ", "_").lower()}',
                                                               report['exif_orientation_distribution'].get(list(report['exif_orientation_distribution'].keys())[orient-1], 0))
            # Simpler approach
            dist = report['exif_orientation_distribution']
            mapping = {
                'orientation_1_normal': 1,
                'orientation_2_flipped_h': 2,
                'orientation_3_rotated_180': 3,
                'orientation_4_flipped_v': 4,
                'orientation_5_rotated_270_cw_flipped': 5,
                'orientation_6_rotated_90_cw': 6,
                'orientation_7_rotated_90_cw_flipped': 7,
                'orientation_8_rotated_90_ccw': 8
            }

        for key, val in report['exif_orientation_distribution'].items():
            if val > 0:
                print(f"  {key}: {val}")

        print("\nRotation Recommendations:")
        rot = report['rotation_recommendations']
        print(f"  No rotation needed: {rot['no_rotation_needed']}")
        print(f"  Rotate 90° CW needed: {rot['rotate_90_cw_needed']}")
        print(f"  Rotate 180° needed: {rot['rotate_180_needed']}")
        print(f"  Rotate 270° CW needed: {rot['rotate_270_cw_needed']}")

        if report['files_needing_rotation']:
            print(f"\nFiles needing rotation ({len(report['files_needing_rotation'])} total):")
            for i, file_info in enumerate(report['files_needing_rotation'][:10], 1):
                print(f"  {i}. {file_info['filename']}")
                print(f"     EXIF Tag: {file_info.get('exif_orientation_tag')} ({file_info.get('orientation_name', 'Unknown')})")
                print(f"     Rotation needed: {file_info['rotation_degrees']}°")

            if len(report['files_needing_rotation']) > 10:
                print(f"  ... and {len(report['files_needing_rotation']) - 10} more")

        print("\n" + "="*80)
        print(f"Full report saved to: {output_file}")


if __name__ == "__main__":
    main()

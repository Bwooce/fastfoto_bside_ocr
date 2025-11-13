"""
Image preprocessing for Claude Code Read tool compatibility.

Handles two critical constraints:
1. File size limit: 5MB after base64 encoding (~3.5MB original JPEG)
2. Dimension limit: 2000px max dimension for many-image requests

Strategy: Resize to 1800px max dimension @ 85% quality
- Keeps well under 2000px limit
- Maintains excellent OCR quality
- Typical output: 300-800KB for photo backs
"""

import os
import tempfile
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Prepares images for Claude Code Read tool."""

    # Conservative limits to avoid API errors
    MAX_DIMENSION_PX = 1800  # Well under 2000px limit
    MAX_FILE_SIZE_MB = 3.0   # Well under 5MB base64 limit (~4MB original)
    JPEG_QUALITY = 85        # Good balance of quality vs size

    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize image processor.

        Args:
            temp_dir: Directory for resized images (default: /tmp/fastfoto_ocr)
        """
        self.temp_dir = Path(temp_dir) if temp_dir else Path("/tmp/fastfoto_ocr")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Image processor initialized with temp_dir: {self.temp_dir}")

    def needs_resize(self, image_path: Path) -> bool:
        """
        Check if image needs resizing.

        Args:
            image_path: Path to image file

        Returns:
            True if image needs resizing
        """
        # Check file size
        file_size_mb = image_path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            logger.debug(f"{image_path.name}: {file_size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB limit")
            return True

        # Check dimensions
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                max_dim = max(width, height)
                if max_dim > self.MAX_DIMENSION_PX:
                    logger.debug(f"{image_path.name}: {max_dim}px > {self.MAX_DIMENSION_PX}px limit")
                    return True
        except Exception as e:
            logger.warning(f"Could not check dimensions for {image_path}: {e}")
            return True  # Resize to be safe

        return False

    def resize_image(self, image_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Resize image to meet Read tool constraints.

        Args:
            image_path: Path to original image
            output_path: Optional output path (default: temp_dir/filename)

        Returns:
            Path to resized image
        """
        if output_path is None:
            output_path = self.temp_dir / image_path.name

        try:
            with Image.open(image_path) as img:
                original_size = img.size
                original_format = img.format

                # Convert to RGB if necessary (handles CMYK, etc.)
                if img.mode not in ('RGB', 'L'):
                    logger.debug(f"Converting {img.mode} to RGB")
                    img = img.convert('RGB')

                # Calculate new dimensions
                width, height = img.size
                max_dim = max(width, height)

                if max_dim > self.MAX_DIMENSION_PX:
                    scale = self.MAX_DIMENSION_PX / max_dim
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    logger.info(f"Resizing {image_path.name}: {width}x{height} -> {new_width}x{new_height}")

                    # Use high-quality resampling
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Save with optimization
                save_kwargs = {
                    'quality': self.JPEG_QUALITY,
                    'optimize': True,
                }

                # Determine output format
                if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                    save_kwargs['format'] = 'JPEG'
                elif output_path.suffix.lower() in ['.tif', '.tiff']:
                    # Convert TIFF to JPEG for size reduction
                    output_path = output_path.with_suffix('.jpg')
                    save_kwargs['format'] = 'JPEG'
                    logger.debug(f"Converting TIFF to JPEG for compatibility")

                img.save(output_path, **save_kwargs)

                # Verify result
                result_size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"Saved {output_path.name}: {result_size_mb:.2f}MB")

                if result_size_mb > self.MAX_FILE_SIZE_MB:
                    logger.warning(f"Result still large ({result_size_mb:.2f}MB), trying lower quality")
                    # Try again with lower quality
                    save_kwargs['quality'] = 75
                    img.save(output_path, **save_kwargs)
                    result_size_mb = output_path.stat().st_size / (1024 * 1024)
                    logger.info(f"Re-saved at quality 75: {result_size_mb:.2f}MB")

                return output_path

        except Exception as e:
            logger.error(f"Failed to resize {image_path}: {e}")
            raise

    def prepare_for_ocr(self, image_path: Path) -> Path:
        """
        Prepare image for OCR (resize if needed).

        Args:
            image_path: Path to original image

        Returns:
            Path to OCR-ready image (original or resized)
        """
        if not self.needs_resize(image_path):
            logger.debug(f"{image_path.name}: No resize needed")
            return image_path

        return self.resize_image(image_path)

    def get_image_info(self, image_path: Path) -> dict:
        """
        Get image metadata.

        Args:
            image_path: Path to image

        Returns:
            Dict with image info (size, dimensions, format)
        """
        try:
            file_size_mb = image_path.stat().st_size / (1024 * 1024)

            with Image.open(image_path) as img:
                return {
                    'path': str(image_path),
                    'format': img.format,
                    'mode': img.mode,
                    'size_mb': round(file_size_mb, 2),
                    'dimensions': img.size,
                    'max_dimension': max(img.size),
                }
        except Exception as e:
            logger.error(f"Could not get info for {image_path}: {e}")
            return {
                'path': str(image_path),
                'error': str(e),
            }

    def cleanup(self):
        """Remove temporary resized images."""
        if self.temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Could not clean up temp directory: {e}")


if __name__ == "__main__":
    # Test/demo
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        test_image = Path(sys.argv[1])
        processor = ImageProcessor()

        print(f"\nOriginal image info:")
        info = processor.get_image_info(test_image)
        for key, value in info.items():
            print(f"  {key}: {value}")

        print(f"\nNeeds resize: {processor.needs_resize(test_image)}")

        if processor.needs_resize(test_image):
            resized = processor.prepare_for_ocr(test_image)
            print(f"\nResized image info:")
            info = processor.get_image_info(resized)
            for key, value in info.items():
                print(f"  {key}: {value}")
    else:
        print("Usage: python image_processor.py <image_path>")

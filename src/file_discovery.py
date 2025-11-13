"""
File discovery and pairing for FastFoto back-side scans.

Finds all _b.jpg/_b.tiff files and pairs them with their originals.
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PhotoPair:
    """Represents a photo and its optional back-side scan."""
    original: Path
    back: Optional[Path] = None

    @property
    def has_back(self) -> bool:
        """Check if this photo has a back-side scan."""
        return self.back is not None and self.back.exists()

    @property
    def original_name(self) -> str:
        """Get original filename."""
        return self.original.name

    @property
    def back_name(self) -> str:
        """Get back filename (or empty string)."""
        return self.back.name if self.back else ""

    def __repr__(self) -> str:
        if self.has_back:
            return f"PhotoPair({self.original.name} + {self.back.name})"
        return f"PhotoPair({self.original.name}, no back)"


class FileDiscovery:
    """Discovers and pairs photo files with their back-side scans."""

    DEFAULT_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff", ".JPG", ".JPEG", ".TIF", ".TIFF"]
    DEFAULT_BACK_SUFFIXES = ["_b", "_B"]

    def __init__(self, extensions: Optional[List[str]] = None,
                 back_suffixes: Optional[List[str]] = None):
        """
        Initialize file discovery.

        Args:
            extensions: List of file extensions to process
            back_suffixes: List of suffixes that indicate back-side scans
        """
        self.extensions = extensions or self.DEFAULT_EXTENSIONS
        self.back_suffixes = back_suffixes or self.DEFAULT_BACK_SUFFIXES
        logger.info(f"FileDiscovery initialized: extensions={self.extensions}, "
                   f"back_suffixes={self.back_suffixes}")

    def is_photo_file(self, path: Path) -> bool:
        """Check if file is a photo with supported extension."""
        return path.suffix in self.extensions

    def is_back_file(self, path: Path) -> bool:
        """Check if file is a back-side scan."""
        if not self.is_photo_file(path):
            return False

        stem = path.stem  # filename without extension
        return any(stem.endswith(suffix) for suffix in self.back_suffixes)

    def get_original_path(self, back_path: Path) -> Path:
        """
        Get the original photo path for a back-side scan.

        Args:
            back_path: Path to back-side scan (e.g., "IMG_001_b.jpg")

        Returns:
            Path to original (e.g., "IMG_001.jpg")
        """
        stem = back_path.stem
        ext = back_path.suffix

        # Remove back suffix
        for suffix in self.back_suffixes:
            if stem.endswith(suffix):
                original_stem = stem[:-len(suffix)]
                return back_path.parent / f"{original_stem}{ext}"

        # Shouldn't happen if is_back_file() returned True
        return back_path

    def discover_pairs(self, root_dir: Path, recursive: bool = True) -> List[PhotoPair]:
        """
        Discover all photo pairs in directory.

        Args:
            root_dir: Root directory to search
            recursive: If True, search subdirectories

        Returns:
            List of PhotoPair objects
        """
        root_dir = Path(root_dir)
        if not root_dir.exists():
            raise ValueError(f"Directory does not exist: {root_dir}")

        logger.info(f"Discovering photos in: {root_dir} (recursive={recursive})")

        # Find all photo files
        pattern = "**/*" if recursive else "*"
        all_files = []

        for ext in self.extensions:
            all_files.extend(root_dir.glob(f"{pattern}{ext}"))

        logger.info(f"Found {len(all_files)} total photo files")

        # Separate backs from originals
        back_files = {}
        original_files = []

        for file_path in all_files:
            if self.is_back_file(file_path):
                # Map back to its original path
                original_path = self.get_original_path(file_path)
                back_files[original_path] = file_path
                logger.debug(f"Back: {file_path.name} -> {original_path.name}")
            else:
                original_files.append(file_path)

        logger.info(f"Found {len(back_files)} back files, {len(original_files)} originals")

        # Create pairs
        pairs = []
        for original in sorted(original_files):
            back = back_files.get(original)
            pair = PhotoPair(original=original, back=back)
            pairs.append(pair)

            if back:
                logger.debug(f"Paired: {pair}")

        # Check for orphaned backs (backs without originals)
        paired_backs = set(back_files.values())
        all_backs = set(f for f in all_files if self.is_back_file(f))
        orphaned = all_backs - paired_backs

        if orphaned:
            logger.warning(f"Found {len(orphaned)} orphaned back files (no matching original):")
            for orphan in sorted(orphaned):
                logger.warning(f"  - {orphan}")

        logger.info(f"Created {len(pairs)} photo pairs ({sum(1 for p in pairs if p.has_back)} with backs)")

        return pairs

    def filter_with_backs(self, pairs: List[PhotoPair]) -> List[PhotoPair]:
        """
        Filter pairs to only those with back-side scans.

        Args:
            pairs: List of PhotoPair objects

        Returns:
            Filtered list with only pairs that have backs
        """
        filtered = [p for p in pairs if p.has_back]
        logger.info(f"Filtered {len(pairs)} pairs -> {len(filtered)} with backs")
        return filtered

    def get_statistics(self, pairs: List[PhotoPair]) -> dict:
        """
        Get statistics about discovered pairs.

        Args:
            pairs: List of PhotoPair objects

        Returns:
            Dict with statistics
        """
        total = len(pairs)
        with_backs = sum(1 for p in pairs if p.has_back)
        without_backs = total - with_backs

        # Group by directory
        by_directory = {}
        for pair in pairs:
            dir_name = str(pair.original.parent)
            if dir_name not in by_directory:
                by_directory[dir_name] = {'total': 0, 'with_backs': 0}
            by_directory[dir_name]['total'] += 1
            if pair.has_back:
                by_directory[dir_name]['with_backs'] += 1

        return {
            'total_pairs': total,
            'with_backs': with_backs,
            'without_backs': without_backs,
            'back_coverage_percent': round(100 * with_backs / total, 1) if total > 0 else 0,
            'directories': len(by_directory),
            'by_directory': by_directory,
        }


if __name__ == "__main__":
    # Test/demo
    import sys
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) > 1:
        test_dir = Path(sys.argv[1])
        discovery = FileDiscovery()

        print(f"\nDiscovering photos in: {test_dir}\n")
        pairs = discovery.discover_pairs(test_dir)

        stats = discovery.get_statistics(pairs)
        print(f"\nStatistics:")
        print(f"  Total pairs: {stats['total_pairs']}")
        print(f"  With backs: {stats['with_backs']}")
        print(f"  Without backs: {stats['without_backs']}")
        print(f"  Coverage: {stats['back_coverage_percent']}%")
        print(f"  Directories: {stats['directories']}")

        print(f"\nFirst 10 pairs with backs:")
        with_backs = discovery.filter_with_backs(pairs)
        for i, pair in enumerate(with_backs[:10], 1):
            print(f"  {i}. {pair}")

    else:
        print("Usage: python file_discovery.py <directory>")

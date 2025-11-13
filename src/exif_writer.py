"""
EXIF metadata writer using ExifTool.

Handles writing extracted metadata from photo backs into original image files.
Preserves existing EXIF data while adding new fields.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExifWriter:
    """Writes EXIF metadata using ExifTool."""

    def __init__(self, exiftool_path: str = "exiftool"):
        """
        Initialize EXIF writer.

        Args:
            exiftool_path: Path to exiftool binary (default: "exiftool" in PATH)
        """
        self.exiftool_path = exiftool_path
        self._verify_exiftool()

    def _verify_exiftool(self):
        """Verify exiftool is installed and accessible."""
        try:
            result = subprocess.run(
                [self.exiftool_path, "-ver"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"ExifTool version {version} found")
            else:
                raise RuntimeError(f"ExifTool returned error: {result.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                f"ExifTool not found at '{self.exiftool_path}'. "
                "Install with: brew install exiftool (macOS) or "
                "apt-get install libimage-exiftool-perl (Linux)"
            )
        except Exception as e:
            raise RuntimeError(f"Error verifying ExifTool: {e}")

    def read_exif(self, image_path: Path) -> Dict[str, Any]:
        """
        Read current EXIF data from image.

        Args:
            image_path: Path to image file

        Returns:
            Dict of EXIF fields and values
        """
        try:
            result = subprocess.run(
                [self.exiftool_path, "-j", "-a", "-G", str(image_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                if data:
                    logger.debug(f"Read EXIF from {image_path.name}: {len(data[0])} fields")
                    return data[0]
                return {}
            else:
                logger.error(f"ExifTool read error: {result.stderr}")
                return {}

        except Exception as e:
            logger.error(f"Error reading EXIF from {image_path}: {e}")
            return {}

    def write_exif(self, image_path: Path, metadata: Dict[str, Any],
                    backup: bool = True, overwrite_original: bool = False) -> bool:
        """
        Write EXIF metadata to image.

        Args:
            image_path: Path to image file
            metadata: Dict of EXIF field names and values
            backup: Create backup file before writing
            overwrite_original: Overwrite original file (no _original backup)

        Returns:
            True if successful, False otherwise
        """
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return False

        try:
            # Build exiftool arguments
            args = [self.exiftool_path]

            # Add overwrite flag if requested
            if overwrite_original:
                args.append("-overwrite_original")

            # Add metadata arguments
            for field, value in metadata.items():
                if value is not None and value != "":
                    args.append(f"-{field}={value}")

            # Add image path
            args.append(str(image_path))

            logger.debug(f"ExifTool command: {' '.join(args)}")

            # Execute
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info(f"Successfully wrote EXIF to {image_path.name}")
                return True
            else:
                logger.error(f"ExifTool write error: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error writing EXIF to {image_path}: {e}")
            return False

    def format_datetime(self, dt: datetime) -> str:
        """
        Format datetime for EXIF DateTimeOriginal field.

        Args:
            dt: datetime object

        Returns:
            String in EXIF format: "YYYY:MM:DD HH:MM:SS"
        """
        return dt.strftime("%Y:%m:%d %H:%M:%S")

    def format_gps_coordinate(self, decimal_degrees: float, ref_positive: str,
                              ref_negative: str) -> tuple:
        """
        Convert decimal degrees to EXIF GPS format.

        Args:
            decimal_degrees: Coordinate in decimal degrees
            ref_positive: Reference for positive values (e.g., "N", "E")
            ref_negative: Reference for negative values (e.g., "S", "W")

        Returns:
            Tuple of (coordinate_string, reference)
        """
        ref = ref_positive if decimal_degrees >= 0 else ref_negative
        abs_degrees = abs(decimal_degrees)

        degrees = int(abs_degrees)
        minutes_decimal = (abs_degrees - degrees) * 60
        minutes = int(minutes_decimal)
        seconds = (minutes_decimal - minutes) * 60

        # ExifTool format: "degrees, minutes, seconds"
        coord_str = f"{degrees}, {minutes}, {seconds:.4f}"

        return coord_str, ref

    def format_gps_latitude(self, latitude: float) -> Dict[str, str]:
        """
        Format latitude for EXIF.

        Args:
            latitude: Latitude in decimal degrees

        Returns:
            Dict with GPSLatitude and GPSLatitudeRef
        """
        coord, ref = self.format_gps_coordinate(latitude, "N", "S")
        return {
            "GPSLatitude": coord,
            "GPSLatitudeRef": ref
        }

    def format_gps_longitude(self, longitude: float) -> Dict[str, str]:
        """
        Format longitude for EXIF.

        Args:
            longitude: Longitude in decimal degrees

        Returns:
            Dict with GPSLongitude and GPSLongitudeRef
        """
        coord, ref = self.format_gps_coordinate(longitude, "E", "W")
        return {
            "GPSLongitude": coord,
            "GPSLongitudeRef": ref
        }

    def build_metadata_dict(self, date: Optional[datetime] = None,
                           latitude: Optional[float] = None,
                           longitude: Optional[float] = None,
                           timezone_offset: Optional[str] = None,
                           location_name: Optional[str] = None,
                           city: Optional[str] = None,
                           country: Optional[str] = None,
                           country_code: Optional[str] = None,
                           sublocation: Optional[str] = None,
                           caption: Optional[str] = None,
                           keywords: Optional[List[str]] = None,
                           user_comment: Optional[str] = None,
                           roll_id: Optional[str] = None,
                           frame_number: Optional[int] = None,
                           lab_code: Optional[str] = None,
                           confidence: Optional[float] = None,
                           language: Optional[str] = None) -> Dict[str, Any]:
        """
        Build EXIF metadata dictionary from extracted data.

        Args:
            date: Photo date/time
            latitude: GPS latitude
            longitude: GPS longitude
            timezone_offset: Timezone offset (e.g., "+12:00")
            location_name: Venue/location name
            city: City name
            country: Country name
            country_code: ISO country code
            sublocation: Sublocation/neighborhood
            caption: Photo caption/description
            keywords: List of keywords
            user_comment: Full OCR text
            roll_id: Film roll ID
            frame_number: Frame number on roll
            lab_code: Photo lab code
            confidence: OCR confidence score
            language: Text language (es/en)

        Returns:
            Dict of EXIF field names and values
        """
        metadata = {}

        # Date/Time
        if date:
            date_str = self.format_datetime(date)
            metadata["DateTimeOriginal"] = date_str
            metadata["CreateDate"] = date_str
            metadata["ModifyDate"] = date_str

            if timezone_offset:
                metadata["OffsetTimeOriginal"] = timezone_offset
                metadata["OffsetTime"] = timezone_offset

        # GPS Location
        if latitude is not None and longitude is not None:
            metadata.update(self.format_gps_latitude(latitude))
            metadata.update(self.format_gps_longitude(longitude))

            # GPS timestamp (use photo date if available)
            if date:
                metadata["GPSDateStamp"] = date.strftime("%Y:%m:%d")
                metadata["GPSTimeStamp"] = date.strftime("%H:%M:%S")

        # Location text fields (IPTC Extension)
        if location_name:
            metadata["LocationCreatedLocationName"] = location_name
        if city:
            metadata["LocationCreatedCity"] = city
        if country:
            metadata["LocationCreatedCountryName"] = country
        if country_code:
            metadata["LocationCreatedCountryCode"] = country_code
        if sublocation:
            metadata["LocationCreatedSublocation"] = sublocation

        # Descriptive text
        if caption:
            metadata["Caption-Abstract"] = caption[:1000]  # Limit length
            metadata["Description"] = caption[:1000]  # XMP duplicate

        if keywords:
            # ExifTool expects comma-separated or multiple -Keywords= args
            metadata["Keywords"] = keywords  # ExifTool handles list automatically

        if user_comment:
            # Full OCR text with metadata
            comment = user_comment
            if language:
                comment += f" [Language: {language}]"
            if confidence:
                comment += f" [Confidence: {confidence:.2f}]"
            metadata["UserComment"] = comment[:2000]  # Limit length

        # Roll and frame info
        if roll_id:
            metadata["ImageUniqueID"] = roll_id
            # Also store in CameraSerialNumber as backup
            metadata["CameraSerialNumber"] = roll_id

        if frame_number:
            metadata["ImageNumber"] = frame_number

        if lab_code:
            metadata["Make"] = f"Processed by {lab_code}"

        # Processing metadata
        metadata["Software"] = "FastFoto OCR v1.0"

        # Image description with metadata
        desc_parts = []
        if confidence:
            desc_parts.append(f"OCR Confidence: {confidence:.2f}")
        if language:
            desc_parts.append(f"Language: {language}")
        if desc_parts:
            metadata["ImageDescription"] = " | ".join(desc_parts)

        return metadata

    def update_image(self, image_path: Path, extracted_data: Dict[str, Any],
                     overwrite_original: bool = False) -> bool:
        """
        Update image with extracted metadata.

        Args:
            image_path: Path to image file
            extracted_data: Dict with extracted metadata (flexible structure)
            overwrite_original: Overwrite original file

        Returns:
            True if successful
        """
        # Build metadata dict from extracted data
        metadata = self.build_metadata_dict(
            date=extracted_data.get('date'),
            latitude=extracted_data.get('latitude'),
            longitude=extracted_data.get('longitude'),
            timezone_offset=extracted_data.get('timezone_offset'),
            location_name=extracted_data.get('location_name'),
            city=extracted_data.get('city'),
            country=extracted_data.get('country'),
            country_code=extracted_data.get('country_code'),
            sublocation=extracted_data.get('sublocation'),
            caption=extracted_data.get('caption'),
            keywords=extracted_data.get('keywords'),
            user_comment=extracted_data.get('user_comment'),
            roll_id=extracted_data.get('roll_id'),
            frame_number=extracted_data.get('frame_number'),
            lab_code=extracted_data.get('lab_code'),
            confidence=extracted_data.get('confidence'),
            language=extracted_data.get('language')
        )

        return self.write_exif(image_path, metadata, overwrite_original=overwrite_original)


if __name__ == "__main__":
    # Test/demo
    import sys
    logging.basicConfig(level=logging.INFO)

    writer = ExifWriter()

    if len(sys.argv) > 1:
        test_image = Path(sys.argv[1])

        print(f"\nReading EXIF from: {test_image}")
        current_exif = writer.read_exif(test_image)
        print(f"Current EXIF fields: {len(current_exif)}")

        # Show some key fields
        key_fields = ["DateTimeOriginal", "GPSLatitude", "GPSLongitude", "Keywords"]
        for field in key_fields:
            value = current_exif.get(field, "<not set>")
            print(f"  {field}: {value}")

    else:
        print("Usage: python exif_writer.py <image_path>")
        print("\nTesting GPS coordinate formatting:")

        # Test GPS formatting
        lat, lon = -12.0464, -77.0428  # Lima, Peru
        lat_data = writer.format_gps_latitude(lat)
        lon_data = writer.format_gps_longitude(lon)
        print(f"Lima coordinates: {lat}, {lon}")
        print(f"  GPS format: {lat_data}, {lon_data}")

#!/usr/bin/env python3
"""
Simple geocoder for FastFoto location names.

Provides approximate GPS coordinates for locations found in photo backs.
Uses a static database of known locations for offline operation.
"""

from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class SimpleGeocoder:
    """Simple geocoder using predefined location database."""

    def __init__(self):
        """Initialize geocoder with location database."""
        self.locations = {
            # Cities with high precision
            'san isidro': (-12.0951, -77.0364),  # Lima, Peru
            'lima': (-12.0464, -77.0428),  # Peru
            'bogotá': (4.7110, -74.0721),  # Colombia
            'bogota': (4.7110, -74.0721),  # Colombia (no accent)
            'monteverde': (10.3009, -84.8003),  # Costa Rica
            'dallas': (32.7767, -96.7970),  # Texas, USA
            'panama city': (8.9824, -79.5199),  # Panama
            'panama': (8.9824, -79.5199),  # Panama (city)
            'cambridge': (52.2053, 0.1218),  # UK (default to UK Cambridge)
            'madrid': (40.4168, -3.7038),  # Spain
            'barcelona': (41.3851, 2.1734),  # Spain
            'sesto': (40.2290, -3.9000),  # Spain (approximate)

            # Countries (center points)
            'peru': (-9.19, -75.0152),
            'colombia': (4.5709, -74.2973),
            'costa rica': (9.7489, -83.7534),
            'netherlands': (52.1326, 5.2913),
            'holland': (52.1326, 5.2913),  # Same as Netherlands
            'spain': (40.4637, -3.7492),
            'united states': (39.8283, -98.5795),
            'usa': (39.8283, -98.5795),
            'panama': (8.4177, -80.7749),  # Country center

            # Regions/Provinces
            'texas': (31.9686, -99.9018),  # USA
            'lima province': (-12.0464, -77.0428),  # Peru

            # Common misspellings
            'loch haren': (52.1326, 5.2913),  # Likely Netherlands region
            'lock haren': (52.1326, 5.2913),  # Alternative spelling
        }

        logger.info(f"SimpleGeocoder initialized with {len(self.locations)} locations")

    def geocode(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Get GPS coordinates for a location name.

        Args:
            location_name: Location name to geocode

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not location_name:
            return None

        # Normalize location name
        normalized = location_name.lower().strip()

        # Direct match
        if normalized in self.locations:
            coords = self.locations[normalized]
            logger.debug(f"Geocoded '{location_name}' → {coords}")
            return coords

        # Try partial matches for compound locations
        for key, coords in self.locations.items():
            if key in normalized or normalized in key:
                logger.debug(f"Geocoded '{location_name}' → {coords} (partial match: {key})")
                return coords

        logger.debug(f"No coordinates found for '{location_name}'")
        return None

    def geocode_from_metadata(self, metadata: Dict[str, str]) -> Optional[Tuple[float, float]]:
        """
        Extract coordinates from location metadata fields.

        Tries location fields in order of specificity:
        1. City + Country
        2. City only
        3. Sublocation
        4. Country only

        Args:
            metadata: Dict containing location fields

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # Extract location components
        city = metadata.get('city', '').strip()
        country = metadata.get('country', '').strip()
        sublocation = metadata.get('sublocation', '').strip()

        # Try combinations in order of specificity

        # 1. City + Country (most specific)
        if city and country:
            combined = f"{city}, {country}"
            coords = self.geocode(combined)
            if coords:
                return coords

            # Try just city if combination failed
            coords = self.geocode(city)
            if coords:
                return coords

        # 2. City only
        elif city:
            coords = self.geocode(city)
            if coords:
                return coords

        # 3. Sublocation (venues, landmarks)
        if sublocation:
            coords = self.geocode(sublocation)
            if coords:
                return coords

        # 4. Country only (least specific but still useful)
        if country:
            coords = self.geocode(country)
            if coords:
                return coords

        return None

    def add_gps_to_metadata(self, metadata: Dict[str, str]) -> Dict[str, str]:
        """
        Add GPS coordinates to metadata dict if location can be geocoded.

        Args:
            metadata: Existing metadata dict

        Returns:
            Updated metadata dict with GPS fields added if possible
        """
        coords = self.geocode_from_metadata(metadata)

        if coords:
            latitude, longitude = coords

            # Add GPS fields using ExifWriter format
            from exif_writer import ExifWriter
            writer = ExifWriter()

            lat_data = writer.format_gps_latitude(latitude)
            lon_data = writer.format_gps_longitude(longitude)

            metadata.update(lat_data)
            metadata.update(lon_data)

            logger.info(f"Added GPS coordinates: {latitude:.4f}, {longitude:.4f}")

        return metadata

    def get_statistics(self) -> Dict[str, any]:
        """Get geocoder statistics."""
        countries = [k for k in self.locations.keys() if len(k.split()) == 1 and len(k) > 3]
        cities = [k for k in self.locations.keys() if k not in countries]

        return {
            'total_locations': len(self.locations),
            'cities': len(cities),
            'countries': len(countries),
            'sample_cities': cities[:5],
            'sample_countries': countries[:5]
        }


if __name__ == "__main__":
    # Test geocoder
    logging.basicConfig(level=logging.INFO)

    geocoder = SimpleGeocoder()

    # Test locations from the proposal file
    test_locations = [
        "San Isidro",
        "Bogotá, Colombia",
        "Monteverde, Costa Rica",
        "Dallas, Texas",
        "Netherlands",
        "Cambridge",
        "Lima, Peru"
    ]

    print("🗺️  Testing SimpleGeocoder:")
    print("=" * 50)

    for location in test_locations:
        coords = geocoder.geocode(location)
        if coords:
            print(f"✅ {location:<20} → {coords[0]:8.4f}, {coords[1]:8.4f}")
        else:
            print(f"❌ {location:<20} → Not found")

    print("\n📊 Geocoder Statistics:")
    stats = geocoder.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
"""
Flexible date parsing for various formats found in photo backs.

Uses python-dateutil for flexible parsing plus custom handlers for:
- Spanish month names
- Two-digit years with century inference
- Partial dates (month-year, year-only)
"""

import re
from datetime import datetime
from typing import Optional, Tuple
from dateutil import parser as dateutil_parser
import logging

logger = logging.getLogger(__name__)


class DateParser:
    """Flexible date parser for photo back metadata."""

    # Spanish month names mapping
    SPANISH_MONTHS = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    # 3-letter month codes (APS format)
    MONTH_CODES = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }

    def __init__(self, collection_date_range: Tuple[int, int] = (1966, 2002)):
        """
        Initialize date parser.

        Args:
            collection_date_range: (min_year, max_year) for century inference
        """
        self.min_year = collection_date_range[0]
        self.max_year = collection_date_range[1]
        logger.info(f"DateParser initialized with range {self.min_year}-{self.max_year}")

    def parse(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string flexibly.

        Args:
            date_str: Date string in any recognized format

        Returns:
            datetime object or None if unparseable
        """
        if not date_str or not isinstance(date_str, str):
            return None

        date_str = date_str.strip()

        try:
            # Try Spanish month replacement first
            date_normalized = self._normalize_spanish(date_str)

            # Try dateutil parser (handles most formats)
            try:
                dt = dateutil_parser.parse(date_normalized, fuzzy=True, dayfirst=True)

                # Fix century if two-digit year
                if dt.year < 100:
                    dt = self._fix_century(dt)

                # Validate year is in expected range
                if self.min_year <= dt.year <= self.max_year + 50:  # Allow some future dates
                    logger.debug(f"Parsed '{date_str}' -> {dt}")
                    return dt
                else:
                    logger.warning(f"Year {dt.year} out of range for '{date_str}'")
                    return None

            except (ValueError, OverflowError):
                # Try custom patterns
                return self._parse_custom(date_str)

        except Exception as e:
            logger.debug(f"Could not parse '{date_str}': {e}")
            return None

    def _normalize_spanish(self, date_str: str) -> str:
        """
        Replace Spanish month names with English equivalents.

        Args:
            date_str: Original date string

        Returns:
            String with Spanish months replaced by English
        """
        normalized = date_str.lower()

        for spanish, month_num in self.SPANISH_MONTHS.items():
            if spanish in normalized:
                # Map to English month names
                english_months = ['January', 'February', 'March', 'April', 'May', 'June',
                                 'July', 'August', 'September', 'October', 'November', 'December']
                normalized = normalized.replace(spanish, english_months[month_num - 1])
                logger.debug(f"Replaced Spanish month: {spanish} -> {english_months[month_num - 1]}")

        return normalized

    def _parse_custom(self, date_str: str) -> Optional[datetime]:
        """
        Parse custom date formats not handled by dateutil.

        Args:
            date_str: Date string

        Returns:
            datetime object or None
        """
        # APS format: 99/JUN/7 11:32AM
        aps_pattern = r'(\d{2})/([A-Z]{3})/(\d{1,2})\s+(\d{1,2}):(\d{2})(AM|PM)'
        match = re.search(aps_pattern, date_str.upper())
        if match:
            yy, mon, d, h, m, ampm = match.groups()
            year = self._two_digit_year_to_full(int(yy))
            month = self.MONTH_CODES.get(mon)
            if month:
                day = int(d)
                hour = int(h)
                if ampm == 'PM' and hour != 12:
                    hour += 12
                elif ampm == 'AM' and hour == 12:
                    hour = 0
                minute = int(m)

                try:
                    dt = datetime(year, month, day, hour, minute)
                    logger.debug(f"Parsed APS format '{date_str}' -> {dt}")
                    return dt
                except ValueError as e:
                    logger.debug(f"Invalid APS date values: {e}")

        # Consumer processing: 02.11.17 or 02/04/22
        consumer_pattern = r'(\d{2})[\./](\d{2})[\./](\d{2})'
        match = re.search(consumer_pattern, date_str)
        if match:
            yy, mm, dd = match.groups()
            year = self._two_digit_year_to_full(int(yy))
            try:
                dt = datetime(year, int(mm), int(dd))
                logger.debug(f"Parsed consumer format '{date_str}' -> {dt}")
                return dt
            except ValueError:
                # Try day/month reversed
                try:
                    dt = datetime(year, int(dd), int(mm))
                    logger.debug(f"Parsed consumer format (day/month swapped) '{date_str}' -> {dt}")
                    return dt
                except ValueError as e:
                    logger.debug(f"Invalid consumer date values: {e}")

        # Year only
        year_only = re.search(r'\b(19\d{2}|20[0-2]\d)\b', date_str)
        if year_only:
            year = int(year_only.group(1))
            dt = datetime(year, 1, 1)
            logger.debug(f"Parsed year-only '{date_str}' -> {dt}")
            return dt

        return None

    def _two_digit_year_to_full(self, yy: int) -> int:
        """
        Convert two-digit year to four-digit year.

        Uses collection date range for inference:
        - Photos from 1966-2002
        - Processing might be a few years later

        Args:
            yy: Two-digit year (0-99)

        Returns:
            Four-digit year
        """
        # Collection spans 1966-2002, processing up to ~2010
        # Use sliding window: 00-30 = 2000-2030, 31-99 = 1931-1999
        if yy <= 30:
            return 2000 + yy
        else:
            return 1900 + yy

    def _fix_century(self, dt: datetime) -> datetime:
        """
        Fix century for two-digit years parsed by dateutil.

        Args:
            dt: datetime with potentially wrong century

        Returns:
            datetime with corrected century
        """
        if dt.year < 100:
            corrected_year = self._two_digit_year_to_full(dt.year)
            return dt.replace(year=corrected_year)
        return dt

    def parse_multiple(self, date_strings: list) -> list:
        """
        Parse multiple date strings.

        Args:
            date_strings: List of date strings

        Returns:
            List of (original_string, datetime) tuples (None for unparseable)
        """
        results = []
        for date_str in date_strings:
            dt = self.parse(date_str)
            results.append((date_str, dt))
        return results

    def get_best_date(self, date_strings: list) -> Optional[datetime]:
        """
        Parse multiple dates and return the most precise/reliable one.

        Priority:
        1. Dates with day precision
        2. Dates with month precision
        3. Year-only dates

        Args:
            date_strings: List of date strings

        Returns:
            Best datetime or None
        """
        parsed = self.parse_multiple(date_strings)

        # Filter out None values
        valid_dates = [(orig, dt) for orig, dt in parsed if dt is not None]

        if not valid_dates:
            return None

        # Score by precision (day > month > year)
        def date_score(dt_tuple):
            orig, dt = dt_tuple
            score = 0
            # Check if day is not 1 (likely specified)
            if dt.day != 1:
                score += 100
            # Check if month is not 1 (likely specified)
            if dt.month != 1:
                score += 10
            # Check if has time component
            if dt.hour != 0 or dt.minute != 0:
                score += 1
            return score

        # Return highest scoring date
        best = max(valid_dates, key=date_score)
        logger.info(f"Best date from {date_strings}: {best[1]} (from '{best[0]}')")
        return best[1]


if __name__ == "__main__":
    # Test/demo
    logging.basicConfig(level=logging.DEBUG)

    parser = DateParser()

    test_dates = [
        "27 de Noviembre de 1983",
        "Marzo 1981",
        "99/JUN/7 11:32AM",
        "02.11.17 08:34PM",
        "25/12/1999",
        "1966",
        "December 25, 1999",
        "Noviembre, 1998",
    ]

    print("\nDate Parsing Tests:\n")
    for date_str in test_dates:
        result = parser.parse(date_str)
        print(f"'{date_str}' -> {result}")

    print("\n\nBest Date Selection:\n")
    mixed_dates = ["1999", "Junio 1999", "99/JUN/7 11:32AM"]
    best = parser.get_best_date(mixed_dates)
    print(f"From {mixed_dates}:")
    print(f"Best: {best}")

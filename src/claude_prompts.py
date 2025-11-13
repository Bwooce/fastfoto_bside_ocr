"""
Claude Vision prompts for photo back OCR extraction.

Generates structured prompts optimized for the analysis results:
- Spanish dates (85% of content)
- Venue/location names (hotels, institutions)
- APS data (3% - rare but important)
- Handwritten narratives
"""

# Main OCR extraction prompt template
PHOTO_BACK_OCR_PROMPT = """🚨 CRITICAL REQUIREMENTS 🚨
1. TRANSCRIBE ALL TEXT VERBATIM - NO COMMENTARY OR DESCRIPTIONS
2. ALL DATES MUST BE IN YYYY-MM-DD FORMAT (ISO STANDARD)

Analyze this photo back scan and extract structured metadata for EXIF enrichment.

**Context**: Reverse side of scanned photograph (1966-2002 collection).

**Image Constraints**: This image has been pre-processed to meet Read tool requirements (max 2000px dimension, <5MB file size).

**KEY FINDING**: 50%+ of backs have machine-printed lab processing data (often VERY small and faint!).

**SEARCH PROTOCOL** (in priority order):

### **ZONE 1: BOTTOM HORIZONTAL EDGE** (HIGHEST PRIORITY - 50%+ of machine dates here!)
**What to look for**:
- **VERY SMALL TEXT** (1-3mm character height)
- **FAINT GRAY** machine printing (easily missed!)
- **Format pattern**: Roll# Frame# Date Time LabCode
- **Examples**:
  - "340-555 <No.24> 02/04/22 09:47PM VIKD"
  - "352-417 <No. 12> 02.11.17 08:34PM CHIOM"
  - "352-417 <No. 1> 02.09.28 06:07PM CHIOM"
- **Contains**: Roll ID (###-###), Frame (<No.##>), Date (YY.MM.DD or YY/MM/DD), Time (HH:MMPM), Lab code

**⚠️ CRITICAL**: This text is SO SMALL and FAINT it's easy to completely miss. Look VERY carefully at the bottom edge!

### **ZONE 2: CENTER HORIZONTAL AREA**
**What to look for**:
- **Small but more visible** black text
- **APS format**: Date Time RollID Frame Equipment
- **Examples**:
  - "99/JUN/7 11:32AM ID529-981 <24> 1KM44"
  - "99/MAY/14 06:14AM ID529-981 <10> 1KM44"
- **Contains**: Date (YY/MMM/D), Time (HH:MMAM), Roll ID (ID###-###), Frame (<##>)

### **ZONE 3: VERTICAL/ROTATED TEXT** (check 90° rotation)
**What to look for**:
- Text rotated 90° (vertical band down center or side)
- Lab processing codes
- Technical data

### **ZONE 4: SCATTERED HANDWRITTEN TEXT**
**What to look for**:
- Handwritten dates (Spanish PRIMARY, English secondary)
- Spanish examples: "27 de Noviembre de 1983", "Marzo 1981"
- English examples: "December 25, 1999"
- Locations, names, events, captions

**What to extract**:

1. **ALL DATES** found in ANY format (machine-printed or handwritten, Spanish or English)
2. **ROLL & FRAME INFO**: Roll IDs (###-### or ID###-###), Frame numbers (<No.##> or <##>)
3. **LAB CODES**: Processing lab identifiers (VIKD, CHIOM, TUL, etc.)
4. **LOCATIONS**: Cities, venues, institutions, neighborhoods
5. **PEOPLE & EVENTS**: Names, event descriptions
6. **DESCRIPTIVE TEXT**: Captions, notes (Spanish or English)

**Note**: Extract dates in whatever format they appear - don't try to match specific patterns, just identify anything that looks like a date.

**Return JSON structure**:

```json
{
  "is_useful": true/false,
  "confidence": 0.0-1.0,

  "zone_1_bottom_edge": {
    "found": true/false,
    "text": "exact text found (if any)",
    "roll_id": "###-###",
    "frame": "##",
    "date": "YYYY-MM-DD format ONLY - e.g. 1994-11-26 (null if none)",
    "date_original": "exact text as written on photo",
    "time": "HH:MM AM/PM",
    "lab_code": "CODE"
  },

  "zone_2_center": {
    "found": true/false,
    "text": "exact text found (if any)",
    "roll_id": "ID###-###",
    "frame": "##",
    "date": "YYYY-MM-DD format ONLY - e.g. 1994-11-26 (null if none)",
    "date_original": "exact text as written",
    "time": "HH:MM AM/PM"
  },

  "zone_3_vertical": {
    "found": true/false,
    "text": "exact text if rotated text found",
    "orientation": 90/180/270
  },

  "zone_4_handwritten": {
    "found": true/false,
    "dates": ["dates in YYYY-MM-DD format ONLY - e.g. 1994-11-26, 1985-01-31"],
    "dates_original": ["exact date text as written"],
    "locations": ["list all locations mentioned"],
    "people": ["list all names"],
    "events": ["list all events"],
    "descriptive_text": "any captions or notes",
    "language": "es/en/mixed"
  },

  "all_dates_found": [
    "ALL dates from ALL zones in YYYY-MM-DD format ONLY - e.g. 1994-11-26, 1985-01-31"
  ],
  "all_dates_original": [
    "exact date texts as written on photo"
  ],

  "raw_ocr_complete": "VERBATIM transcription of ALL text - do NOT summarize, provide exact words/characters visible"
}
```

**Instructions**:
- Return ONLY valid JSON
- Use `null` for missing fields
- Focus on FINDING text in the zones

**Date Parsing Rules**:
- Convert ALL dates to YYYY-MM-DD format (ISO standard)
- Preserve original text in `*_original` fields
- For ambiguous 2-digit years: 00-30 = 20xx, 31-99 = 19xx
- Spanish months: enero=01, febrero=02, marzo=03, abril=04, mayo=05, junio=06, julio=07, agosto=08, septiembre=09, octubre=10, noviembre=11, diciembre=12
- Roman numerals: I=01, II=02, III=03, IV=04, V=05, VI=06, VII=07, VIII=08, IX=09, X=10, XI=11, XII=12
- Spanish events: "Año Nuevo" = January 1, "Navidad" = December 25
- Examples: "1-31-85" → "1985-01-31", "26/XI/94" → "1994-11-26", "Año Nuevo 96" → "1996-01-01"

**🚨 CRITICAL - raw_ocr_complete Field 🚨**:
- TRANSCRIBE EVERY SINGLE CHARACTER you can see
- NEVER describe what the text is about
- NEVER use phrases like "handwritten text about", "appears to be", "inverted text about"
- If you see "Fuimos a la playa muy bonita el domingo" - write exactly that
- If text is rotated, rotate and transcribe it - don't say "inverted text about vacation"
- If text is faint, transcribe what you can see - don't say "faint writing"
- If you cannot read specific words, use [illegible] for those words only

❌ WRONG: "Inverted handwritten Spanish text about Holland vacation experiences"
✅ CORRECT: "Kodak Advanced Photo System 99/JUN/7 11:33AM ID529-981 <25> 1KN44 Fuimos a Holland fue increible las tulipas eran [illegible] muy bonitas"

❌ WRONG: "Bruce written vertically with date plus Spanish diary entries"
✅ CORRECT: "Bruce 01/02/98 La playa estaba perfecta hoy nadamos mucho tiempo"

**General**:
- Report small/faint text even with low confidence
"""


def generate_ocr_prompt(image_name: str = "") -> str:
    """
    Generate OCR extraction prompt for a photo back.

    Args:
        image_name: Optional image filename for context

    Returns:
        Formatted prompt string
    """
    prompt = PHOTO_BACK_OCR_PROMPT

    if image_name:
        prompt = f"Image: {image_name}\n\n" + prompt

    return prompt


def generate_batch_instructions(image_paths: list, output_file: str) -> str:
    """
    Generate instructions for batch processing with Claude Code CLI.

    Args:
        image_paths: List of image paths to process
        output_file: Where to save results

    Returns:
        Instructions text for the user
    """
    instructions = f"""
# FastFoto OCR - Batch Processing Instructions

## Overview
Process {len(image_paths)} photo back scans using Claude Code CLI.

## Setup
1. Ensure Claude Code CLI is installed and authenticated
2. Images are ready at the paths below
3. Results will be saved to: {output_file}

## Processing Strategy

For EACH image, use Claude Code's Read tool with the structured prompt below.

### Critical Reminders:
- ⚠️ Look for SMALL, FAINT machine-printed text in the MIDDLE HORIZONTAL ZONE
- ⚠️ Spanish dates are PRIMARY (85% of content)
- ⚠️ APS data is RARE (3%) but important when found
- ⚠️ Venue names (hotels, schools, churches) are valuable for geocoding

## Images to Process

"""

    for i, path in enumerate(image_paths, 1):
        instructions += f"{i}. {path}\n"

    instructions += f"""

## Prompt to Use

Use this prompt for EACH image with the Read tool:

{PHOTO_BACK_OCR_PROMPT}

## Output Format

For each image, save the JSON output to {output_file} with this structure:

```json
{{
  "filename": "image_name_b.jpg",
  "timestamp": "2025-11-13T14:30:00",
  "ocr_result": {{
    ... full JSON from Claude Vision ...
  }}
}}
```

Append each result as a new JSON object (one per line, JSONL format).

## Tips

- Process in batches of 10-20 to avoid fatigue
- Take breaks between batches
- Review results periodically for quality
- Report any errors or unexpected patterns

Good luck! 📸
"""

    return instructions


def parse_claude_response(response: str) -> dict:
    """
    Parse Claude's JSON response from photo back OCR analysis.

    Args:
        response: Raw response from Claude's Read tool

    Returns:
        Parsed JSON data as dictionary

    Raises:
        ValueError: If response is not valid JSON
    """
    import json
    import re

    # Clean up the response - sometimes Claude includes markdown or explanations
    response = response.strip()

    # Look for JSON content between ```json and ``` or just find JSON object
    json_pattern = r'```json\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, response, re.DOTALL)

    if match:
        json_str = match.group(1)
    else:
        # Try to find JSON object in response
        json_start = response.find('{')
        json_end = response.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            json_str = response[json_start:json_end + 1]
        else:
            # Fallback - use entire response
            json_str = response

    try:
        data = json.loads(json_str)

        # Claude should now return ISO dates directly based on updated prompt
        # No post-processing needed!
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Claude response as JSON: {e}\nResponse: {response[:200]}...")



if __name__ == "__main__":
    # Test/demo
    print("=== FastFoto OCR Prompt Generator ===\n")
    print("Sample prompt:\n")
    print(generate_ocr_prompt("test_image_b.jpg"))

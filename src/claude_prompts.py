"""
Claude Vision prompts for photo back OCR extraction.

Generates structured prompts optimized for the analysis results:
- Spanish dates (85% of content)
- Venue/location names (hotels, institutions)
- APS data (3% - rare but important)
- Handwritten narratives
"""

# Main OCR extraction prompt template
PHOTO_BACK_OCR_PROMPT = """Analyze this photo back scan and extract structured metadata for EXIF enrichment.

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
    "date": "any format",
    "time": "HH:MM AM/PM",
    "lab_code": "CODE"
  },

  "zone_2_center": {
    "found": true/false,
    "text": "exact text found (if any)",
    "roll_id": "ID###-###",
    "frame": "##",
    "date": "any format",
    "time": "HH:MM AM/PM"
  },

  "zone_3_vertical": {
    "found": true/false,
    "text": "exact text if rotated text found",
    "orientation": 90/180/270
  },

  "zone_4_handwritten": {
    "found": true/false,
    "dates": ["list all dates in any format"],
    "locations": ["list all locations mentioned"],
    "people": ["list all names"],
    "events": ["list all events"],
    "descriptive_text": "any captions or notes",
    "language": "es/en/mixed"
  },

  "all_dates_found": [
    "list ALL dates from ALL zones, in the format they appear"
  ],

  "raw_ocr_complete": "full transcription of everything visible"
}
```

**Instructions**:
- Return ONLY valid JSON
- Use `null` for missing fields
- Focus on FINDING text in the zones, not parsing/formatting
- List dates exactly as they appear - don't try to standardize them
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


if __name__ == "__main__":
    # Test/demo
    print("=== FastFoto OCR Prompt Generator ===\n")
    print("Sample prompt:\n")
    print(generate_ocr_prompt("test_image_b.jpg"))

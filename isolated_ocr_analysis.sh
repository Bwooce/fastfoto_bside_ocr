#!/bin/bash

# FastFoto Isolated OCR Analysis Script
# Processes each back scan photo in complete isolation to prevent context contamination
# Each photo gets analyzed by a fresh Claude instance with zero memory of other photos

set -e

# Configuration
PREPARED_DIR="/tmp/fastfoto_prepared"
OUTPUT_DIR="/tmp/isolated_analysis"
LOG_FILE="/tmp/isolated_analysis.log"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Initialize log
echo "FastFoto Isolated OCR Analysis Started: $(date)" > "$LOG_FILE"

# Count total files
TOTAL_FILES=$(find "$PREPARED_DIR" -name "*_b.jpg" | wc -l)
echo "Total back scan files found: $TOTAL_FILES" | tee -a "$LOG_FILE"

# Process each back scan file individually
CURRENT=0
find "$PREPARED_DIR" -name "*_b.jpg" | sort | while read -r filepath; do
    CURRENT=$((CURRENT + 1))
    filename=$(basename "$filepath")
    output_file="$OUTPUT_DIR/${filename%.*}_analysis.txt"

    echo "[$CURRENT/$TOTAL_FILES] Processing: $filename" | tee -a "$LOG_FILE"

    # Skip if already processed
    if [ -f "$output_file" ]; then
        echo "  -> Already exists, skipping" | tee -a "$LOG_FILE"
        continue
    fi

    # Create optimized extraction prompt with anti-hallucination rules
    prompt_text="Use Read tool to analyze $filepath.

EXTRACT (VERBATIM ONLY):
1. TRANSCRIPTION: Exact text as written - mark uncertain as [uncertain: word?]
2. APS DATA: YY-MON-D HH:MMAM/PM, ID###-###, <##>, equipment codes
3. DATES: Extract in priority order (first found wins):
   - Priority 1: Handwritten dates from comments (personal notes)
   - Priority 2: Machine/APS processing timestamps (lab data)
   - Priority 3: Date patterns in filename (last resort)
   - Format as YYYY:MM:DD HH:MM:SS (use Jan 1 if only year available)
   - Assume DD/MM/YY format for ambiguous dates
   - Include time component if available from APS timestamps
4. LOCATIONS: Only if clearly written - NO GUESSING
5. GPS: Only for definitively identifiable places - NO GEOGRAPHIC GUESSING

CRITICAL RULES:
- NO pattern building from other photos
- NO interpretation - transcribe exactly what you see
- Mark ALL uncertain text as [uncertain: word?]
- Preserve original spelling/language
- GPS only if location absolutely recognizable

OUTPUT:
FILENAME: $filename
TRANSCRIPTION: [verbatim text with uncertainty markers]
LANGUAGE: [Spanish/English/Dutch/German]
APS_DATA: [specific codes or None visible]
DATES: [found or None visible]
LOCATIONS: [clearly written or None visible]
PEOPLE: [names found or None visible]
GPS_COORDINATES: [definitive lat,long or None generated]

EXIF_MAPPINGS:
Caption-Abstract: [verbatim handwritten text only]
UserComment: [language] handwritten text: [verbatim transcription]
ImageDescription: [brief event/location context if clear]
IPTC:ObjectName: [handwritten text - Apple Photos title field]
IPTC:Keywords: [dates;names;locations;events - semicolon separated]
XMP:Description: [event/location context - broad compatibility]
DateTimeOriginal: [YYYY:MM:DD HH:MM:SS EXIF format with time when available]
ProcessingSoftware: [APS processing codes and equipment info]
ImageUniqueID: [APS roll+frame like ID529-981-05 for true uniqueness - combine roll ID with frame number]
GPS:GPSLatitude: [decimal degrees if location identified]
GPS:GPSLongitude: [decimal degrees if location identified]
GPS:GPSLatitudeRef: [N/S hemisphere]
GPS:GPSLongitudeRef: [E/W hemisphere]"

    # Run optimized Claude CLI analysis with error monitoring
    echo "  -> Launching optimized Claude CLI analysis..." | tee -a "$LOG_FILE"

    # Capture both stdout and stderr for error detection
    claude_output=$(echo "$prompt_text" | claude -p \
        --model sonnet \
        --tools "Read" \
        --add-dir /tmp/fastfoto_prepared \
        --system-prompt "Extract data from single photo only." \
        --settings '{"permissions":{"defaultMode":"bypassPermissions"}}' \
        2>&1)
    claude_exit_code=$?

    # Check for token/rate limiting errors
    if [[ $claude_exit_code -ne 0 ]] || echo "$claude_output" | grep -iq "rate limit\|quota\|token\|insufficient\|billing"; then
        echo "  -> CRITICAL: Token/rate limit detected!" | tee -a "$LOG_FILE"
        echo "Claude output: $claude_output" | tee -a "$LOG_FILE"
        echo ""
        echo "🚨 PROCESSING PAUSED 🚨" | tee -a "$LOG_FILE"
        echo "Reason: Token limit, rate limit, or billing issue detected" | tee -a "$LOG_FILE"
        echo "Current file: $filename" | tee -a "$LOG_FILE"
        echo "Progress: $CURRENT/$TOTAL_FILES files processed" | tee -a "$LOG_FILE"
        echo "To resume: Fix token/billing issue and restart script" | tee -a "$LOG_FILE"
        echo "Partial results available in: $OUTPUT_DIR" | tee -a "$LOG_FILE"
        exit 1
    elif echo "$claude_output" | grep -q "ERROR\|Analysis completed"; then
        echo "$claude_output" > "$output_file"
        echo "  -> Analysis completed: $output_file" | tee -a "$LOG_FILE"
    else
        echo "  -> ERROR: Analysis failed for $filename" | tee -a "$LOG_FILE"
        echo "ERROR: Failed to analyze $filename at $(date)" >> "$output_file"
        echo "Claude output: $claude_output" >> "$output_file"
    fi

    # Periodic token monitoring checkpoint
    if (( CURRENT % 50 == 0 )); then
        echo ""
        echo "=== CHECKPOINT: $CURRENT files processed ===" | tee -a "$LOG_FILE"
        echo "Checking system health..." | tee -a "$LOG_FILE"

        # Quick token test with small request
        test_output=$(echo "test" | claude -p --model sonnet --settings '{"permissions":{"defaultMode":"bypassPermissions"}}' 2>&1)
        if echo "$test_output" | grep -iq "rate limit\|quota\|token\|insufficient\|billing"; then
            echo "🚨 PROCESSING PAUSED AT CHECKPOINT 🚨" | tee -a "$LOG_FILE"
            echo "Reason: Token/billing issue detected at checkpoint" | tee -a "$LOG_FILE"
            echo "Progress: $CURRENT/$TOTAL_FILES files processed" | tee -a "$LOG_FILE"
            echo "Partial results available in: $OUTPUT_DIR" | tee -a "$LOG_FILE"
            exit 1
        else
            echo "✅ System health OK, continuing..." | tee -a "$LOG_FILE"
        fi
        echo ""
    fi

    # Brief pause to avoid overwhelming the system
    sleep 2
done

echo "FastFoto Isolated OCR Analysis Completed: $(date)" | tee -a "$LOG_FILE"
echo "Results available in: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"

# Generate summary
echo "" | tee -a "$LOG_FILE"
echo "SUMMARY:" | tee -a "$LOG_FILE"
echo "- Total files processed: $(ls -1 "$OUTPUT_DIR"/*_analysis.txt 2>/dev/null | wc -l)" | tee -a "$LOG_FILE"
echo "- Output directory: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "- Individual analysis files ready for review and collation" | tee -a "$LOG_FILE"
# FastFoto Apply Implementation Guide

Complete implementation details for `/fastfoto-apply [source_directory]` command that processes all 398 analysis files and applies EXIF metadata to original photos.

## Command Invocation

```bash
/fastfoto-apply ~/Pictures/2025_PeruScanning
```

## Execution Flow

When user runs the command above, the Claude Code environment will:

1. Read this implementation guide
2. Use the Task tool to process all 398 analysis files sequentially
3. For each file, apply EXIF metadata to the corresponding original photo
4. Generate a comprehensive report with statistics

## Implementation Details

### Phase 1: Initialize and Verify

1. Verify `/tmp/isolated_analysis/` contains 398 `*_b_analysis.txt` files
2. Verify source directory exists and contains original photos
3. Verify exiftool is available via `which exiftool`
4. Create `{source_directory}/processed/` subdirectory

### Phase 2: Parse and Extract EXIF Mappings

For each of the 398 analysis files in order:

1. **Read analysis file** using Read tool
2. **Extract filename** from `**FILENAME:**` line
   - Example: `1966_Prom_0002_b.jpg`
3. **Extract EXIF_MAPPINGS section** starting after `## EXIF_MAPPINGS:` or `**EXIF_MAPPINGS:**`
4. **Parse each EXIF field** with format `**FieldName:** value`
   - Caption-Abstract
   - UserComment
   - ImageDescription
   - IPTC:ObjectName
   - IPTC:Keywords
   - XMP:Description
   - DateTimeOriginal
   - ProcessingSoftware
   - ImageUniqueID
   - GPS:GPSLatitude
   - GPS:GPSLongitude
   - GPS:GPSLatitudeRef
   - GPS:GPSLongitudeRef

5. **Skip empty/placeholder values**:
   - "None"
   - "None (no APS data visible)"
   - Empty strings

### Phase 3: Map to Exiftool Fields

Convert parsed EXIF field names to exiftool command-line field names:

```
Caption-Abstract          → Caption-Abstract
UserComment              → UserComment
ImageDescription         → ImageDescription
IPTC:ObjectName          → IPTC:ObjectName
IPTC:Keywords            → IPTC:Keywords
XMP:Description          → XMP:Description
DateTimeOriginal         → DateTimeOriginal
ProcessingSoftware       → Software
ImageUniqueID            → ImageUniqueID
GPS:GPSLatitude          → GPSLatitude
GPS:GPSLongitude         → GPSLongitude
GPS:GPSLatitudeRef       → GPSLatitudeRef
GPS:GPSLongitudeRef      → GPSLongitudeRef
```

### Phase 4: Apply EXIF Metadata

For each analysis file:

1. **Find original photo**:
   - Remove `_b` from back scan filename
   - Example: `1966_Prom_0002_b.jpg` → `1966_Prom_0002.jpg`
   - Look in `{source_directory}/{original_filename}`

2. **Skip if original photo not found**:
   - Log as skipped with reason "Original photo not found"
   - Continue to next file

3. **Build exiftool command**:
   ```bash
   exiftool -overwrite_original \
     -Caption-Abstract="value" \
     -UserComment="value" \
     -ImageDescription="value" \
     ... more fields ... \
     {source_directory}/{original_filename}
   ```

4. **Execute via Bash tool**:
   - Run the exiftool command
   - Capture success/failure status
   - Log result with number of fields applied

### Phase 5: Organize Back Scans

For successfully processed photos:

1. Check if back scan file exists at `{source_directory}/{back_scan_filename}`
2. If exists, move to `{source_directory}/processed/{back_scan_filename}`
3. If move fails, log as move failure but continue processing
4. If back scan doesn't exist, skip (don't treat as failure)

### Phase 6: Generate Report

After all 398 files processed, generate report showing:

```
================================================================================
FASTFOTO EXIF METADATA APPLICATION REPORT
================================================================================

Processing Summary:
  Total files analyzed:      398
  Successfully applied:      [X]
  Failed applications:       [Y]
  Skipped:                   [Z]
  Back scans moved:          [M]
  Move failures:             [F]

Success Rate: X/398 (XX%)

Detailed Statistics:
  Parse failures:            [count]
  Missing original photos:   [count]
  No valid mappings:         [count]
  Apply failures:            [count]

Sample Successful Applications (showing first 5):
  ✓ 1966_Prom_0001.jpg (12 fields)
  ✓ 1978_Location_0001.jpg (8 fields)
  ... more samples ...

Sample Failures (showing first 5):
  ✗ filename.jpg: Reason for failure
  ... more samples ...

Sample Skipped (showing first 5):
  - filename.jpg: Original photo not found
  ... more samples ...

================================================================================
Report generated: 2025-11-14 23:00:00
================================================================================
```

## Sample Analysis File Format

```
**FILENAME:** 1978_Location_0003_b.jpg

**ORIENTATION:** correct

**TRANSCRIPTION:**
Panamne [uncertain: golef?] Siesta
Marzo 1981

**LANGUAGE:** Spanish

**APS_DATA:** None visible

**DATES:** Marzo 1981 (March 1981)

**LOCATIONS:** Panama (clearly written)

**GPS_COORDINATES:** 8.9824, -79.5199 (Panama City, Panama)

---

## EXIF_MAPPINGS:

**Caption-Abstract:** Panamne [uncertain: golef?] Siesta Marzo 1981

**UserComment:** Spanish handwritten text: Panamne [uncertain: golef?] Siesta Marzo 1981

**ImageDescription:** Panama vacation, March 1981

**IPTC:ObjectName:** Panamne [uncertain: golef?] Siesta Marzo 1981

**IPTC:Keywords:** Panama;Marzo 1981;March 1981;1981;Siesta;vacation

**XMP:Description:** Panama vacation, March 1981

**DateTimeOriginal:** 1981:03:01 00:00:00

**ProcessingSoftware:** None (no APS data visible)

**ImageUniqueID:** None (no APS roll/frame data visible)

**GPS:GPSLatitude:** 8.9824

**GPS:GPSLongitude:** 79.5199

**GPS:GPSLatitudeRef:** N

**GPS:GPSLongitudeRef:** W
```

## Key Design Decisions

### 1. Read Tool Only
- Uses Read tool to access analysis files
- No script creation or intermediate files
- Pure extraction and processing

### 2. Batch Processing
- Processes all 398 files sequentially
- Shows progress for each file
- Continues even if some fail

### 3. Graceful Degradation
- Missing back scans don't stop processing
- Missing original photos skip gracefully
- Empty EXIF mappings skip gracefully
- Move failures don't prevent metadata application

### 4. Comprehensive Error Handling
- Track all failure reasons
- Log sample failures for debugging
- Report statistics on each failure type

### 5. File Organization Optional
- Back scan moves are nice-to-have, not required
- Original photos always stay in place
- Processed subdirectory created automatically

## Expected Performance

- **Processing time**: ~2-3 hours for 398 files (30-45 seconds per file)
- **Success rate**: 300+ files with EXIF metadata applied
- **Success probability**: ~85-90% (some files may lack originals)
- **Cost**: Minimal (mostly exiftool operations, not API calls)

## Error Recovery

If processing is interrupted:

1. Already-processed files retain their EXIF metadata
2. Resume by running `/fastfoto-apply` again
3. Duplicate EXIF application is safe (exiftool overwrites)
4. Check report to identify any permanently failed files

## Verification Steps

After completion, verify with sample photos:

```bash
# Check one photo's metadata
exiftool ~/Pictures/2025_PeruScanning/1966_Prom_0001.jpg | grep -E "Caption|UserComment|Keywords|DateTimeOriginal|GPSLatitude"

# Check processed directory
ls ~/Pictures/2025_PeruScanning/processed/ | head -20

# Count successful applications
ls ~/Pictures/2025_PeruScanning/processed/ | wc -l
```

## Task Tool Usage

When user runs `/fastfoto-apply ~/Pictures/2025_PeruScanning`, Claude Code will execute with Task tool:

```
Use Task tool with:
- subagent_type: "general-purpose"
- model: "haiku"
- instructions: Process all 398 analysis files from /tmp/isolated_analysis/
- Use Read tool ONLY for analysis files
- Use Bash tool for exiftool commands
- Process sequentially, showing progress for each file
- Generate comprehensive statistics report
- Handle missing files gracefully, continue processing all 398
```

## Implementation Checklist

- [x] Command definition created: `/fastfoto-apply.md`
- [x] This implementation guide created
- [x] EXIF field mapping documented
- [x] Error handling strategy defined
- [x] Report format specified
- [x] File organization logic specified
- [x] Ready for Task tool execution

When user runs the command, they can invoke Task tool directly or I can invoke it as part of the workflow.

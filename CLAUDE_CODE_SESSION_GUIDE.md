# Claude Code Session Guide: FastFoto OCR

## 🚨 CRITICAL RULES FOR CLAUDE 🚨

**When a user asks to "process FastFoto images":**

### RULE 1: COMPLETE THE FULL JOB
- ✅ **DO** process ALL images, not demonstrate with samples
- ❌ **NEVER** do demonstrations or partial processing

### RULE 2: NO PAUSING FOR OPTIMIZATION
- ✅ **DO** start processing immediately and work through the entire collection
- ❌ **NEVER** pause to suggest "more efficient approaches"
- ❌ **NEVER** offer batch processing scripts (they don't work - only Read tool works)
- ❌ **NEVER** suggest breaking into sessions or prioritized processing
- ❌ **NEVER** ask user to choose between "Option A/B/C" alternatives
- ❌ **NEVER** worry about session limits or time estimates

### RULE 3: JUST DO THE WORK
- The user wants the job DONE, not suggestions for optimization
- Process images one by one using Read tool until complete or session ends naturally
- If session ends, user will start a new session to continue - don't pre-optimize for this
- ✅ **ENHANCEMENT IDEAS ARE WELCOME AFTER PROCESSING IS COMPLETE** (not during)

## Architecture Decision: Interactive Claude Code Mode

**Approach:** Use Claude Code's Read tool (via Claude Max subscription) instead of standalone Anthropic SDK.

**This means:**
- ✅ No API key needed (uses Claude Max)
- ✅ No separate API costs
- ⚠️ Requires active Claude Code session to process images
- ⚠️ Not a standalone script - interactive workflow

## Setup Instructions

**1. Clone and checkout main:**
```bash
git clone https://github.com/Bwooce/fastfoto_bside_ocr.git
cd fastfoto_bside_ocr
git checkout main
git pull origin main
```

**2. Verify files:**
```bash
ls -la src/
# Should see all 7 modules from Phase 1
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
# Note: anthropic package NOT needed anymore

# Ensure ExifTool is installed:
# macOS: brew install exiftool
# Linux: apt-get install libimage-exiftool-perl
```

## Single-Step Interactive Workflow

**User starts Claude Code session and says:**
```
"Process my FastFoto images in ~/Photos/FastFoto and generate a proposal file"
```

## ⚠️ CRITICAL INSTRUCTION - NO DEMONSTRATIONS ⚠️

**NEVER demonstrate with sample images. ALWAYS process the COMPLETE collection.**

**When user says "Process my FastFoto images":**
- ❌ **DO NOT** analyze only 4-5 sample images as a "demonstration"
- ❌ **DO NOT** say "Let me demonstrate with a few samples"
- ❌ **DO NOT** create fake/simulated statistics for unprocessed images
- ✅ **DO** process EVERY SINGLE prepared image using the Read tool
- ✅ **DO** show real progress through the entire collection
- ✅ **DO** generate a proposal with ALL actual results

**The user wants the complete job done, not a demo!**

**Claude (you) will automatically:**
1. **Run preprocessing** via Bash tool:
   - Execute `python src/preprocess_images.py ~/Photos/FastFoto --output /tmp/fastfoto_prepared`
   - Show preprocessing progress and statistics
2. **Load mapping** file to understand original → prepared relationships
3. **Analyze EVERY SINGLE prepared image** using Read tool:
   - MANDATORY: Use Read tool on EACH AND EVERY prepared image file
   - NO SHORTCUTS: Do not skip images or do "representative samples"
   - FOR EACH IMAGE: Parse response with `parse_claude_response()`
   - Extract metadata (dates, locations, text) from each individual image
   - This takes ~10-18 seconds per image (be patient for large collections)
   - SHOW PROGRESS: Display "Processing [X/TOTAL]" for each image as you go
4. **Generate complete proposal** file using `proposal_generator` with ALL ACTUAL results
5. **Present summary** to user with statistics for ENTIRE REAL collection

**⚠️ ABSOLUTE REQUIREMENT: Process EVERY SINGLE IMAGE - NO DEMONSTRATIONS ⚠️**

## 🛑 CRITICAL: NO PAUSING FOR "EFFICIENCY" SUGGESTIONS 🛑

**When you start processing, DO NOT pause to suggest:**
- ❌ "This will take 6-8 hours, let me suggest alternatives..."
- ❌ "Let me create a batch processing script..." (scripts don't work!)
- ❌ "Would you prefer Option A: continue, Option B: break into sessions..."
- ❌ "Focus on high-value images first..."
- ❌ "Process 20-30 images per session..."

**JUST START PROCESSING AND KEEP GOING UNTIL DONE.**

The user knows it takes time. They want the complete job done, not optimization advice.

**Processing Time Expectations:**
- Small collections (10-50 images): 15-30 minutes
- Medium collections (50-200 images): 1-3 hours
- Large collections (200+ images): 2+ hours
- Each image takes ~10-18 seconds to analyze with Read tool

**User reviews proposal, then says:**
```
"Apply the proposal file"
```

**Claude (you) will:**
6. Parse the proposal file
7. Skip entries marked with `SKIP:`
8. Apply EXIF updates to **original photos** via `exif_writer` (no backup files)
9. Move processed back scan files to `processed/` subdirectories
10. Report results with organization statistics

**Benefits:**
- **Simple UX**: One command does everything
- **No temp management**: Claude handles preprocessing automatically
- **Error recovery**: Can fix issues in same session
- **Seamless workflow**: No context switching
- **Clean organization**: Processed back scans moved to `processed/` subdirectories
- **No backup clutter**: Clean EXIF updates without `*_original` files

## Tasks for Phase 2

### ✅ TASK 1: Preprocessing Script (COMPLETE)

**File:** `src/preprocess_images.py`

**Done:**
- Standalone CLI script for preprocessing images
- Uses existing `file_discovery` and `image_processor` modules
- Progress bars with tqdm
- Statistics reporting
- Creates mapping file for original → prepared paths
- Preserves directory structure (optional)

### TASK 2: Create Interactive Processing Helper

**New file:** `src/interactive_processor.py`

**Purpose:** Helper functions for Claude Code sessions to analyze prepared images

```python
class InteractiveProcessor:
    """Helper for Claude Code interactive processing."""

    def __init__(self):
        self.file_discovery = FileDiscovery()
        self.image_processor = ImageProcessor()
        # etc.

    def process_directory(self, root_dir: Path) -> List[ProcessingResult]:
        """
        Discover files and return list ready for Claude to analyze.
        Claude will use Read tool on each back scan.
        """
        pairs = self.file_discovery.discover_pairs(root_dir)
        results = []

        for pair in pairs:
            if not pair.has_back_scan:
                continue

            # Prepare image for Read tool
            prepared = self.image_processor.prepare_for_ocr(pair.back_scan)

            results.append({
                'original': pair.original,
                'back_scan': prepared,
                'pair': pair
            })

        return results

    def build_proposal_from_analyses(self, analyses: List[Dict]) -> Path:
        """
        Take Claude's analysis results and build proposal file.
        """
        generator = ProposalGenerator(Path('exif_updates_proposal.txt'))

        for analysis in analyses:
            # Extract metadata
            metadata = self.extract_metadata(analysis)

            # Read current EXIF
            current = self.exif_writer.read_exif(analysis['original_path'])

            # Build proposed updates
            proposed = self.exif_writer.build_metadata_dict(**metadata)

            # Add entry
            generator.add_entry(ProposalEntry(
                original_path=analysis['original_path'],
                back_path=analysis['back_path'],
                current_exif=current,
                proposed_updates=proposed,
                metadata=metadata
            ))

        generator.write()
        return generator.output_path
```

### TASK 3: Update README for Interactive Workflow

Update `README.md` to explain:
- Interactive workflow (not standalone script)
- Requires Claude Code session
- Example session dialogue
- Cost: $0 (uses Claude Max)

## Example Complete Workflow

### Step 1: User runs preprocessing (command line)

```bash
$ python src/preprocess_images.py ~/Photos/FastFoto --output /tmp/fastfoto_prepared

================================================================================
FastFoto Back Scan Preprocessor
================================================================================
Source:      /Users/you/Photos/FastFoto
Output:      /tmp/fastfoto_prepared
Recursive:   True
Structure:   Preserved
================================================================================

Discovering photos in /Users/you/Photos/FastFoto (recursive=True)...
Found 482 back scans to preprocess

Processing: 100%|██████████████████████████| 482/482 [00:45<00:00, 10.67it/s]

Mapping saved to: /tmp/fastfoto_prepared/preprocessing_mapping.json

================================================================================
PREPROCESSING SUMMARY
================================================================================
Total back scans found:      482
Resized (too large):         127
Converted (TIFF→JPEG):       5
Copied as-is:                350
Errors:                      0

Total size before:           2847.3 MB
Total size after:            892.5 MB
Size reduction:              68.7%
================================================================================

✓ Preprocessing complete! Next steps:
  1. Review prepared images in: /tmp/fastfoto_prepared
  2. Start Claude Code session and say:
     "Analyze the prepared FastFoto images in /tmp/fastfoto_prepared"
```

### Step 2: User starts Claude Code session

```
User: "Analyze the prepared FastFoto images in /tmp/fastfoto_prepared and generate a proposal file"

Claude (you): I'll analyze the prepared FastFoto back scans. Let me load the mapping file first...

[Load preprocessing_mapping.json to get original file paths]

Found 482 prepared images. I'll analyze each using the Read tool with the OCR prompt. This will take a while...

[For each prepared image:]
  - Use Read tool with PHOTO_BACK_OCR_PROMPT
  - Parse response with parse_claude_response()
  - Extract metadata (dates, locations, text)
  - Track statistics

Processing: [1/482] IMG_001_b.jpg... ✓ (date: 1999-06-07, location: Utrecht)
Processing: [2/482] IMG_002_b.jpg... ✓ (date: 2001-03-15)
Processing: [3/482] IMG_003_b.jpg... ⚠ (confidence: 0.58, no useful data)
...

Analysis complete!
- 482 photos analyzed
- 289 with useful metadata (60%)
- 193 without useful data (40%)
- Average confidence: 0.88

Generating proposal file...

✓ Proposal created: exif_updates_proposal.txt

Please review the file and make any edits. When ready, say "apply the proposal" to update your photos.

---

User: "apply the proposal"

Claude: Applying EXIF updates from proposal file to original photos...

[Parse proposal, skip SKIP: entries, apply to original files via exif_writer]

Processing updates: 100%|████████████████| 289/289 [00:12<00:00, 23.47it/s]

✓ Updated 289 photos
✓ Skipped 2 (marked with SKIP:)
✓ Backups created (*_original files)

Done! Your original photos now have updated EXIF metadata from the back scans.
```

## Testing Strategy

1. **Start small:** Test with 2-3 photos first
2. **Review proposal:** Check extraction accuracy
3. **Test apply:** Use --dry-run first
4. **Full run:** Process entire collection

## Files Status

**✅ Complete:**
- `src/preprocess_images.py` (NEW) - ✅ WORKING - Tested on 150 photos
- `src/interactive_processor.py` (NEW) - ✅ COMPLETE - Helper for Claude Code sessions
- `requirements.txt` (UPDATED) - ✅ COMPLETE - Removed anthropic package
- `README.md` (UPDATED) - ✅ COMPLETE - Documents two-step workflow
- Full Phase 2 implementation - ✅ TESTED AND WORKING

**📦 Ready for Production:**
- Preprocessing: 150 back scans processed (284MB → 18.9MB, 93.4% reduction)
- Interactive workflow: Ready for Claude Code sessions
- Cost: $0 using Claude Max subscription

## Your Role

**Implementation assistant.** Propose code changes, wait for approval before committing.

**When reporting back:**
1. Show the code changes
2. Explain what you changed and why
3. Wait for approval
4. Then commit and push to a new branch

## Questions for User Before Starting

1. Do you have sample photos ready for testing? Where?
2. Should I create the new `interactive_processor.py` file?
3. Should I update the README to explain the interactive workflow?

---

## 📋 CLAUDE WORKFLOW SUMMARY

**When user says "Process my FastFoto images":**

1. ✅ **START IMMEDIATELY** - Run preprocessing, then start Read tool analysis of ALL images
2. ✅ **PROCESS EVERYTHING** - Use Read tool on every single prepared image (no samples)
3. ✅ **SHOW PROGRESS** - "Processing [X/TOTAL] imagename.jpg..." as you go
4. ✅ **GENERATE COMPLETE PROPOSAL** - Include all actual results from all images
5. ❌ **NO PAUSING** - Don't suggest alternatives, optimizations, or session breaks
6. ❌ **NO OPTIONS** - Don't ask "Would you prefer A, B, or C?"
7. ✅ **ENHANCEMENT IDEAS** - Feel free to suggest improvements AFTER processing is complete

**The user wants the complete job done first, suggestions second.**

---

**Remember:** The lead engineer will review all changes before they're committed. Show your work, get approval, then proceed.

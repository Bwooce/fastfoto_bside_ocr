# Brief for Local Claude CLI: FastFoto OCR Phase 2 Implementation

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

**Claude (you) will automatically:**
1. **Run preprocessing** via Bash tool:
   - Execute `python src/preprocess_images.py ~/Photos/FastFoto --output /tmp/fastfoto_prepared`
   - Show preprocessing progress and statistics
2. **Load mapping** file to understand original → prepared relationships
3. **Analyze each image** using Read tool:
   - Use Read tool with `PHOTO_BACK_OCR_PROMPT`
   - Parse response with `parse_claude_response()`
   - Extract metadata (dates, locations, text)
4. **Generate proposal** file using `proposal_generator`
5. **Present summary** to user with statistics

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

**Remember:** The lead engineer will review all changes before they're committed. Show your work, get approval, then proceed.

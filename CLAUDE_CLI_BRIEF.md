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

## New Workflow: Interactive Processing

### How It Works

**User starts Claude Code session and says:**
```
"Process my FastFoto back scans in ~/Photos/FastFoto and generate a proposal file"
```

**Claude (you) will:**
1. Call `file_discovery.discover_pairs()` to find all `*_b.jpg` files
2. For each back scan:
   - Call `image_processor.prepare_for_ocr()` if needed
   - Use **Read tool** to analyze the image with `PHOTO_BACK_OCR_PROMPT`
   - Parse response with `parse_claude_response()`
   - Extract metadata with date parser, location extraction, etc.
3. Generate proposal file using `proposal_generator`
4. Present summary to user

**User reviews proposal, then says:**
```
"Apply the proposal file"
```

**Claude (you) will:**
5. Parse the proposal file
6. Skip entries marked with `SKIP:`
7. Apply EXIF updates via `exif_writer`
8. Report results

## Tasks for Phase 2

### TASK 1: Refactor orchestrator.py for Interactive Mode

**Current state:** `orchestrator.py` expects to call Anthropic SDK

**New design:**
- Keep helper functions (extract_metadata_from_analysis, etc.)
- Remove or stub out `analyze_back_scan()` - Claude will call Read tool directly
- Keep `create_proposal()` but modify to accept pre-analyzed data
- Keep `apply_proposal()` - this still works as-is

**Or simpler:** Don't use orchestrator.py at all! Just call the modules directly:
```python
from src.file_discovery import FileDiscovery
from src.proposal_generator import ProposalGenerator
# etc.
```

### TASK 2: Create Interactive Processing Helper

**New file:** `src/interactive_processor.py`

**Purpose:** Helper functions for Claude Code sessions

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

## Example Interactive Session

```
User: "Process my FastFoto photos in ~/Photos/FastFoto"

Claude (you): I'll process your FastFoto back scans. Let me discover the files first...

[Call file_discovery and image_processor]

Found 482 photo pairs with back scans. I'll now analyze each back scan using the Read tool. This will take a few minutes...

[For each back scan:]
  - Use Read tool with the prepared image
  - Send PHOTO_BACK_OCR_PROMPT
  - Parse response
  - Extract metadata

Processing: [1/482] IMG_001_b.jpg... ✓ (date: 1999-06-07, location: Utrecht)
Processing: [2/482] IMG_002_b.jpg... ✓ (date: 2001-03-15)
...

Analysis complete!
- 482 photos analyzed
- 289 with useful metadata (60%)
- Average confidence: 0.88

Generating proposal file...

✓ Proposal created: exif_updates_proposal.txt

Please review the file. When ready, say "apply the proposal" to update your photos.

---

User: "apply the proposal"

Claude: Applying EXIF updates from proposal file...

[Parse proposal, skip SKIP: entries, apply via exif_writer]

✓ Updated 289 photos
✓ Skipped 2 (marked with SKIP:)
✓ Backups created (*_original files)

Done! Your photos now have updated EXIF metadata from the back scans.
```

## Testing Strategy

1. **Start small:** Test with 2-3 photos first
2. **Review proposal:** Check extraction accuracy
3. **Test apply:** Use --dry-run first
4. **Full run:** Process entire collection

## Files You'll Modify

- `src/interactive_processor.py` (NEW) - Helper for Claude Code sessions
- `src/orchestrator.py` (MODIFY) - Keep apply_proposal(), update/remove analyze_back_scan()
- `README.md` (UPDATE) - Document interactive workflow
- `requirements.txt` (DONE) - Already removed anthropic package

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

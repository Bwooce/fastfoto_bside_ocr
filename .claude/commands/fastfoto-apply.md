# Apply FastFoto EXIF Updates

Apply extracted metadata to original image files after reviewing the proposal.

## Prerequisites

You should have already run `/fastfoto-analysis` which generated a proposal file at `/tmp/fastfoto_proposal.txt`.

## Step 1: Review the Proposal

Let me first show you the proposal file so you can review the extracted metadata:

```bash
cat /tmp/fastfoto_proposal.txt
```

## Step 2: Apply EXIF Updates (Dry Run First)

Before making actual changes, let's do a dry run to see what would be updated:

```bash
python src/orchestrator.py apply /tmp/fastfoto_proposal.txt ~/Pictures/2025_PeruScanning --dry-run
```

This will show you:
- Which files would be updated
- What EXIF fields would be modified
- What metadata would be added
- Any potential issues or warnings

## Step 3: Apply Real EXIF Updates

If the dry run looks good and you approve the changes, apply them to the actual image files:

```bash
python src/orchestrator.py apply /tmp/fastfoto_proposal.txt ~/Pictures/2025_PeruScanning
```

This will:
- Update EXIF Caption-Abstract with verbatim handwritten text
- Add UserComment with language-tagged transcriptions
- Set Description fields with event/location context
- Add Keywords with parsed dates, names, places
- Update DateTimeOriginal when dates are found
- Apply any rotation corrections identified

## Step 4: Verify Updates

After application, you can verify the updates were applied:

```bash
exiftool ~/Pictures/2025_PeruScanning/[sample_filename.jpg]
```

The EXIF data should now include the extracted handwritten metadata from the back scans.
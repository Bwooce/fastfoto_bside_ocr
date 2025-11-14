# Complete FastFoto OCR Workflow

Complete end-to-end FastPhoto OCR processing: analysis, review, and EXIF application.

## Overview

This is the complete FastFoto workflow that will:

1. **Analyze** your photo collection for orientation issues and extract handwritten metadata
2. **Generate** a human-reviewable proposal file
3. **Apply** approved EXIF updates to your original image files

**Source Directory:** ~/Pictures/2025_PeruScanning (modify as needed)

## Step 1: Run Complete Analysis

First, let's run the full analysis workflow:

```bash
# Prepare back scans for OCR
python src/preprocess_images.py ~/Pictures/2025_PeruScanning --output /tmp/fastfoto_prepared

# Analyze main photos for orientation issues
python batch_orientation_analysis.py
```

Now I'll process all back scans using Read tool for OCR metadata extraction. This will:

- Analyze each back scan individually using Read tool
- Extract verbatim handwritten text in multiple languages
- Parse dates, locations, people names, and events
- Generate a comprehensive proposal file for EXIF updates

**Processing all back scan files now...**

## Step 2: Review Extracted Metadata

After analysis completes, I'll show you the proposal file:

```bash
head -50 /tmp/fastfoto_proposal.txt
```

You can review:
- Extracted handwritten text transcriptions
- Identified dates, locations, and people
- Proposed EXIF field updates
- Confidence scores for each extraction

## Step 3: Apply EXIF Updates

If you approve the extracted metadata, we can apply it:

**Option A: Dry Run (Recommended first)**
```bash
python src/orchestrator.py apply /tmp/fastfoto_proposal.txt ~/Pictures/2025_PeruScanning --dry-run
```

**Option B: Apply Real Updates**
```bash
python src/orchestrator.py apply /tmp/fastfoto_proposal.txt ~/Pictures/2025_PeruScanning
```

## Expected Results

After completion, your photos will have:
- **Caption-Abstract:** Verbatim handwritten text from photo backs
- **UserComment:** Language-tagged transcriptions
- **Description:** Event and location context
- **Keywords:** Parsed dates, names, places
- **DateTimeOriginal:** Corrected dates when found
- **Orientation:** Fixed rotation issues

Let me start the analysis process now...
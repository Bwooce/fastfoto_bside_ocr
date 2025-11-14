# FastFoto Analysis Workflow

Complete FastFoto OCR analysis using hybrid approach: scripts for preparation, Read tool for analysis.

## Step 1: Prepare Images for Analysis

First, let's prepare the back scan images for Read tool compatibility:

```bash
python src/preprocess_images.py ~/Pictures/2025_PeruScanning --output /tmp/fastfoto_prepared
```

## Step 2: Analyze Orientation Issues

Run batch orientation analysis for main photos:

```bash
python batch_orientation_analysis.py
```

## Step 3: Process Back Scans with Read Tool

Now I'll use the Read tool directly to analyze prepared back scan images for OCR metadata extraction. I'll process them in small batches to extract verbatim handwritten text:

**CRITICAL: I will use Read tool directly on INDIVIDUAL files from /tmp/fastfoto_prepared/ to extract:**
- Verbatim handwritten text (exact transcription)
- Language identification (Spanish, German, English)
- Dates found (converted to YYYY-MM-DD format)
- Location names mentioned
- People names
- Event descriptions

**I will process ALL back scan files individually, no sampling, and generate a comprehensive OCR analysis.**

## Step 4: Generate Proposal File

After completing the Read tool analysis of all back scans, I'll create a structured proposal file in the expected format that can be applied using the orchestrator:

**The proposal file will include:**
- Verbatim text transcriptions for each photo
- Language identification and context
- Parsed metadata (dates, names, locations)
- Specific EXIF field mappings
- Confidence scores for each extraction

**Output location:** `/tmp/fastfoto_proposal.txt`

Let me start by discovering all the prepared back scan files and then analyzing each one using Read tool for verbatim text extraction, followed by generating the structured proposal file.
# FastFoto Orientation Analysis

Analyze main photos for rotation issues using Read tool with visual inspection.

## Step 1: Prepare Images for Analysis

First, let's downsample the main photos for efficient Read tool processing:

```bash
mkdir -p /tmp/orientation_analysis
```

Then I'll create downsampled versions and analyze them directly with Read tool (the batch scripts are broken and generate fake simulation data):

## Step 2: Visual Orientation Analysis with Read Tool

Now I'll use the Read tool directly to analyze the downsampled images for orientation issues. I'll examine each image to determine:

- Are people standing upright?
- Do faces appear correctly oriented?
- Are text/signs readable in normal orientation?
- Do horizon lines and buildings appear level?

**CRITICAL: I will use Read tool to visually inspect INDIVIDUAL files from /tmp/orientation_analysis/ to identify:**
- Photos needing 90° clockwise rotation
- Photos needing 90° counter-clockwise rotation
- Photos needing 180° rotation (upside down)
- Photos that are correctly oriented

**I will process files in batches of 10-15 maximum, examining each one individually for actual visual orientation problems, not just EXIF metadata.**

Let me start by checking what files are in the orientation analysis directory and then analyzing them systematically for rotation issues.
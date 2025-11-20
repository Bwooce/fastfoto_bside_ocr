# Apple Photos Metadata Cleanup Scripts

These AppleScript files will help you remove pollution metadata from Apple Photos that may have been imported before we fixed the OCR analysis issue.

## Scripts Included

### 1. `Clean_Apple_Photos_Metadata.applescript` (Comprehensive)
- **Full-featured cleanup script**
- Choose between selected photos or ALL photos in library
- Removes pollution from both descriptions and keywords
- Shows progress notifications for large batches
- Provides detailed completion statistics

### 2. `Simple_Clean_Selected_Photos.applescript` (Quick & Simple)
- **Quick cleanup for selected photos only**
- Simple interface - just select photos and run
- Removes common pollution patterns
- Fast execution

## What These Scripts Clean Up

### Pollution Patterns Removed:
- ✅ "leave empty" / "Leave empty"
- ✅ "no context available"
- ✅ "back scan" references
- ✅ "not extractable" / "no extractable"
- ✅ "none visible"
- ✅ "photo lab processing"
- ✅ "blank" / "degraded"

## How to Use

### Method 1: Script Editor (Recommended)
1. **Open Script Editor** (found in Applications → Utilities)
2. **Open one of the .applescript files**
3. **Click the Run button** (▶️)
4. **Follow the prompts**

### Method 2: Double-Click (Quick)
1. **Double-click** either .applescript file
2. **Choose "Run"** when prompted
3. **Follow the dialog boxes**

### Method 3: Save as Application
1. **Open the script in Script Editor**
2. **File → Export**
3. **File Format: Application**
4. **Save as a clickable app**

## Step-by-Step Workflow

### For Selected Photos:
1. **Open Apple Photos**
2. **Select the contaminated photos** (Cmd+click for multiple)
3. **Run `Simple_Clean_Selected_Photos.applescript`**
4. **Confirm the cleanup**

### For All Photos:
1. **Open Apple Photos**
2. **Run `Clean_Apple_Photos_Metadata.applescript`**
3. **Choose "All Photos"** (be patient - this can take time)
4. **Let it run and review the final statistics**

## Important Notes

### ⚠️ Safety
- **These scripts modify your photos permanently**
- **Photos.app has built-in undo for recent changes**
- **Consider backing up your Photos library first**

### ⏱️ Performance
- **Selected photos**: Very fast (seconds)
- **All photos**: Can take 10+ minutes for large libraries (10,000+ photos)
- **Progress shown**: Every 100 photos for large batches

### 🔍 What Gets Preserved
- **Real handwritten transcriptions**: Kept intact
- **Valid location data**: Preserved
- **Actual dates**: Maintained
- **Legitimate keywords**: Unchanged

## Example Before/After

### Before Cleanup:
- **Description**: "leave empty - no context available from back scan"
- **Keywords**: "none visible", "not extractable", "Madrid", "1993"

### After Cleanup:
- **Description**: "" (empty)
- **Keywords**: "Madrid", "1993" (pollution removed, real content kept)

## Troubleshooting

### "Photos is not allowed to be automated"
1. **System Preferences → Security & Privacy → Privacy**
2. **Select "Automation"**
3. **Check the box next to "Photos"** for Script Editor

### Script runs but nothing happens
- **Check if you have photos selected** (for Simple version)
- **Ensure Photos.app is the frontmost application**
- **Try restarting Photos.app**

### "Can't get selection"
- **Make sure photos are actually selected in Photos.app**
- **Try clicking on a photo first, then running the script**

## After Cleanup

Once you've cleaned your Apple Photos library, the **fixed OCR analysis system** will ensure no future pollution occurs. New photos processed with `/fastfoto-analyze` will only generate clean, standardized metadata.
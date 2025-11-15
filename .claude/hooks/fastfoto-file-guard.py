#!/usr/bin/env python3
"""
FastFoto File Guard Hook - Enforces FastFoto workflow constraints
Blocks creation of forbidden documentation files and scripts
"""
import json
import sys
import re
import os

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")

        # Block script creation (.py, .sh, .js, .rb, etc.) except for specific allowed scripts
        script_extensions = [".py", ".sh", ".js", ".rb", ".pl", ".php"]
        allowed_scripts = ["apply_fastfoto_exif.py"]

        if any(file_path.endswith(ext) for ext in script_extensions):
            # Allow specific required scripts
            if any(file_path.endswith(allowed) for allowed in allowed_scripts):
                pass  # Allow this script
            else:
                deny_with_reason("Script creation blocked - FastFoto workflow requires Read tool only, no automation scripts")
                return

        # Block forbidden documentation files
        forbidden_patterns = [
            r"ANALYSIS_SUMMARY\.txt$",
            r"FASTFOTO_ANALYSIS_SUMMARY\.txt$",
            r"QUICK_REFERENCE.*\.txt$",
            r"ANALYSIS_.*\.txt$",
            r"sample_.*_files\.txt$",
            r".*_summary\.txt$",
            r"implementation.*\.txt$",
            r"README.*\.md$",
            r"GUIDE.*\.md$"
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                deny_with_reason(f"Documentation file blocked - FastFoto workflow requires single JSON output only, not {os.path.basename(file_path)}")
                return

        # Handle /tmp/ directory file creation restrictions
        if file_path.startswith("/tmp/"):
            # Block JSON file creation - agents should use Read tool directly
            if file_path.endswith(".json"):
                deny_with_reason(f"JSON file creation blocked - Use Read tool directly instead of creating custom outputs: {os.path.basename(file_path)}")
                return

            # Allow specific proposal files but block comprehensive reports
            elif file_path.endswith(".txt"):
                allowed_txt_patterns = [
                    r".*_proposal\.txt$",
                    r"exif_updates_proposal.*\.txt$",
                    r"fastfoto_proposal\.txt$",
                    r"proposal\.txt$"
                ]
                if any(re.search(pattern, file_path) for pattern in allowed_txt_patterns):
                    sys.exit(0)  # Allow proposal files
                else:
                    deny_with_reason(f"Custom txt file creation blocked - Use proposal file format or Read tool directly: {os.path.basename(file_path)}")
                    return

            # Block marker files specifically
            elif any(marker in file_path.lower() for marker in ['.done', '.processed', '.complete', '.marker', '.tracking', '.progress']):
                deny_with_reason(f"Marker file creation blocked - No automation tracking systems allowed: {os.path.basename(file_path)}")
                return

            # Block all other file creation in /tmp/ except image files for preparation
            elif not file_path.endswith(".jpg"):
                deny_with_reason(f"Custom file creation blocked in /tmp/ - Use Read tool directly, no automation infrastructure: {os.path.basename(file_path)}")
                return

        # If we reach here, the file write is allowed
        sys.exit(0)

    except Exception as e:
        # On error, allow the write but log the issue
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(0)

def deny_with_reason(reason):
    """Block the write with a clear explanation"""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
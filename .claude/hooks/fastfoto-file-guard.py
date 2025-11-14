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

        # Block script creation (.py, .sh, .js, .rb, etc.)
        script_extensions = [".py", ".sh", ".js", ".rb", ".pl", ".php"]
        if any(file_path.endswith(ext) for ext in script_extensions):
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

        # Allow only specific FastFoto JSON outputs in /tmp/
        if file_path.startswith("/tmp/"):
            allowed_json_patterns = [
                r"fastfoto_.*\.json$",
                r"orientation_.*\.json$",
                r".*_analysis_.*\.json$",
                r"back_scan_.*\.json$"
            ]

            # If it's a JSON file, it must match allowed patterns
            if file_path.endswith(".json"):
                if not any(re.search(pattern, file_path) for pattern in allowed_json_patterns):
                    deny_with_reason(f"Unauthorized JSON file - Only FastFoto workflow outputs allowed: {os.path.basename(file_path)}")
                    return

            # Allow orchestrator-generated proposal files
            elif file_path.endswith(".txt"):
                allowed_txt_patterns = [
                    r".*_proposal\.txt$",
                    r"exif_updates_proposal.*\.txt$",
                    r"fastfoto_proposal\.txt$"
                ]
                if any(re.search(pattern, file_path) for pattern in allowed_txt_patterns):
                    sys.exit(0)  # Allow orchestrator proposal files
                else:
                    deny_with_reason(f"Custom txt file creation blocked - Only orchestrator proposal files allowed: {os.path.basename(file_path)}")
                    return

            # Block all other non-JSON files in /tmp/ except approved workflow files
            elif not file_path.endswith(".jpg"):  # Allow image files for preparation
                deny_with_reason(f"Non-JSON/proposal file creation blocked in /tmp/ - Use orchestrator for txt outputs: {os.path.basename(file_path)}")
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
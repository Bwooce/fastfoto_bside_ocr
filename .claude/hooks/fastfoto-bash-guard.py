#!/usr/bin/env python3
"""
FastFoto Bash Guard Hook - Prevents script creation and automation via Bash
Enforces Read tool only constraint for FastFoto workflows
"""
import json
import sys
import re

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_input = input_data.get("tool_input", {})
        command = tool_input.get("command", "")

        # Block script creation via heredoc or file redirection
        forbidden_patterns = [
            r"cat\s*>\s*.*\.py",          # cat > script.py
            r"cat\s*>\s*.*\.sh",          # cat > script.sh
            r"echo.*>\s*.*\.py",          # echo "code" > script.py
            r"echo.*>\s*.*\.sh",          # echo "code" > script.sh
            r".*<<\s*['\"]?EOF['\"]?",    # heredoc creation
            r".*<<\s*['\"]?END['\"]?",    # heredoc creation
            r"python3?\s+-c.*subprocess", # subprocess automation
            r"python3?\s+-c.*os\.system", # system call automation
            r"find.*-exec",               # find with exec (automation)
            r"xargs.*python",             # xargs automation
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                deny_with_reason(f"Script creation blocked - FastFoto workflow requires Read tool only, not automation via: {pattern}")
                return

        # Block specific automation tools
        automation_commands = [
            "subprocess.run",
            "os.system",
            "exec(",
            "eval(",
        ]

        for cmd in automation_commands:
            if cmd in command:
                deny_with_reason(f"Automation command blocked - FastFoto workflow uses Read tool exclusively: {cmd}")
                return

        # Allow specific commands for FastFoto preparation
        allowed_patterns = [
            r"^mkdir\s+",                 # Directory creation
            r"^magick\s+",                # ImageMagick processing
            r"^python\s+src/preprocess_images\.py",  # Preprocessing script
            r"^ls\s+",                    # File listing
            r"^chmod\s+",                 # Permission changes
            r"^git\s+",                   # Git operations
            r"^grep\s+",                  # Text search
            r"^cat\s+",                   # File display (not creation)
            r"^head\s+",                  # File preview
            r"^tail\s+",                  # File preview
            r"^echo\s+[^>]*$",           # Echo without redirection
        ]

        # If command doesn't match allowed patterns, check if it's safe
        if not any(re.match(pattern, command) for pattern in allowed_patterns):
            # Block complex commands that could be automation
            if any(char in command for char in ["|", "&&", ";", "`", "$("]):
                deny_with_reason(f"Complex bash operation blocked - FastFoto workflow uses simple commands only")
                return

        # If we reach here, the command is allowed
        sys.exit(0)

    except Exception as e:
        # On error, allow the command but log the issue
        print(f"Bash guard hook error: {e}", file=sys.stderr)
        sys.exit(0)

def deny_with_reason(reason):
    """Block the command with a clear explanation"""
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
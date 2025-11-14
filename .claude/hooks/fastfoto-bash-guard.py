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

        # Allow git operations with heredoc (legitimate use case)
        if re.match(r"^git\s+", command) and "<<" in command:
            sys.exit(0)

        # Block script creation via heredoc or file redirection
        forbidden_patterns = [
            r"cat\s*>\s*.*\.py",          # cat > script.py
            r"cat\s*>\s*.*\.sh",          # cat > script.sh
            r"echo.*>\s*.*\.py",          # echo "code" > script.py
            r"echo.*>\s*.*\.sh",          # echo "code" > script.sh
            r"cat\s*<<.*>\s*.*\.py",      # heredoc to script.py
            r"cat\s*<<.*>\s*.*\.sh",      # heredoc to script.sh
            r".*<<.*>\s*.*\.py",          # any heredoc to .py file
            r".*<<.*>\s*.*\.sh",          # any heredoc to .sh file
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

        # Allow specific commands for FastFoto preparation and analysis
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
            r"^find\s+",                  # File finding
            r"^wc\s+",                    # Word/line counting
            r"^sort\s+",                  # Sorting
            r"^uniq\s+",                  # Uniqueness
        ]

        # Allow simple piped operations for data processing
        if "|" in command and not any(danger in command for danger in ["&&", ";", "`", "$("]):
            # Check if it's a safe pipe operation (file processing)
            safe_pipe_patterns = [
                r"find.*\|\s*wc",         # find | wc (counting)
                r"ls.*\|\s*grep",         # ls | grep (filtering)
                r"grep.*\|\s*head",       # grep | head (limiting)
                r"cat.*\|\s*grep",        # cat | grep (searching)
                r".*\|\s*sort",           # anything | sort
                r".*\|\s*uniq",           # anything | uniq
            ]

            if any(re.search(pattern, command) for pattern in safe_pipe_patterns):
                sys.exit(0)  # Allow safe pipe operations

        # Check for specific dangerous patterns instead of blanket blocking
        dangerous_command_patterns = [
            r";\s*(rm|del|format)",       # Semicolon followed by destructive commands
            r"&&.*rm",                    # Command chaining with rm
            r"&&.*del",                   # Command chaining with del
            r"`.*rm",                     # Command substitution with rm
            r"\$\(.*rm",                  # Command substitution with rm
        ]

        for dangerous in dangerous_command_patterns:
            if re.search(dangerous, command, re.IGNORECASE):
                deny_with_reason(f"Dangerous command pattern blocked: {dangerous}")
                return

        # Allow normal bash constructs like for loops, while loops, etc.
        # Focus only on preventing script creation (already covered) and subprocess automation (already covered)

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
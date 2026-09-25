import os
from pathlib import Path

def read_logs(lines: int = 50) -> str:
    """Read the last N lines of the Paris debug log to diagnose issues."""
    log_path = Path(__file__).resolve().parent.parent / "logs" / "paris_debug.log"
    if not log_path.exists():
        return "Log file not found."
    
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            
        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return "".join(recent_lines)
    except Exception as e:
        return f"Error reading logs: {e}"

TOOL = {
    "name": "read_logs",
    "description": "Read the recent system logs of the Paris AI to diagnose errors, crashes, or failed actions (like failed clicks or screenshots). Use this when the user asks what went wrong.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "lines": {
                "type": "INTEGER",
                "description": "Number of recent log lines to read (default 50)."
            }
        },
        "required": []
    },
    "handler": read_logs,
}

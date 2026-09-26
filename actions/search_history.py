import json
from pathlib import Path
import os
import time

def search_history(query: str = "", limit: int = 50) -> str:
    """Search or fetch recent conversation history."""
    log_path = Path(__file__).resolve().parent.parent / "logs" / "session_history.jsonl"
    if not log_path.exists():
        return "No history found."

    results = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Parse lines
        parsed_lines = []
        for line in lines:
            try:
                parsed_lines.append(json.loads(line))
            except Exception:
                pass
                
        if query:
            query = query.lower()
            filtered = [msg for msg in parsed_lines if query in str(msg.get("text", "")).lower()]
        else:
            filtered = parsed_lines
            
        recent = filtered[-limit:]
        if not recent:
            return "No matching history found."
            
        formatted = []
        for msg in recent:
            role = msg.get("role", "unknown")
            text = msg.get("text", "")
            timestamp = msg.get("time", "")
            formatted.append(f"[{timestamp}] {role}: {text}")
            
        return "\n".join(formatted)
    except Exception as e:
        return f"Failed to search history: {e}"

TOOL = {
    "name": "search_history",
    "description": "Search the verbatim transcript of past sessions and earlier conversations for a specific keyword or fetch the recent history.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "Keyword or phrase to search for. Leave empty to just get the most recent N lines of history."
            },
            "limit": {
                "type": "INTEGER",
                "description": "Maximum number of matching lines to return (default 50)."
            }
        }
    },
    "handler": search_history,
    "scope": "local"
}

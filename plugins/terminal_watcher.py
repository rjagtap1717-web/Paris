import os
import time
import threading
from core.llm_client import call_llm_text

PLUGIN = {
    "name": "terminal_watcher",
    "description": (
        "Starts a background watcher on a specific log file or terminal output. "
        "If an error or traceback is detected, it automatically analyzes it and "
        "suggests a fix proactively."
    ),
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "log_file": {
                "type": "STRING", 
                "description": "The absolute path to the log file to monitor."
            },
        },
        "required": ["log_file"],
    },
}

_active_watchers = {}

def _tail_file(filepath: str, player=None):
    """Background thread to tail the file and catch exceptions."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Go to the end of the file
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue
                
                # Simple heuristic for python traceback or generic error
                if "Traceback (most recent call last):" in line or "Error:" in line or "Exception:" in line:
                    error_block = line
                    # Read the next 10 lines to capture the full traceback
                    for _ in range(10):
                        next_line = f.readline()
                        if next_line:
                            error_block += next_line
                        else:
                            break
                            
                    if player:
                        player.write_log(f"🚨 [TerminalWatcher] Detected Error in {os.path.basename(filepath)}:\n{error_block}")
                        
                    # Proactive Analysis
                    prompt = f"I detected this error in a log file:\n\n{error_block}\n\nWhat is the likely cause and how do I fix it? Keep it under 3 sentences."
                    try:
                        analysis = call_llm_text(prompt=prompt)
                        if player:
                            player.write_log(f"🤖 [Auto-Fix Suggestion]:\n{analysis}")
                    except Exception as e:
                        if player:
                            player.write_log(f"⚠️ [TerminalWatcher] Analysis failed: {e}")
    except FileNotFoundError:
        if player:
            player.write_log(f"⚠️ [TerminalWatcher] File not found: {filepath}")

def run(parameters: dict, player=None, session_memory=None) -> str:
    log_file = parameters.get("log_file", "")
    
    if not log_file:
        return "You must provide a valid log_file path."
        
    if log_file in _active_watchers:
        return f"Already watching {log_file}."
        
    if not os.path.exists(log_file):
        # Create an empty file to watch if it doesn't exist
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("")
        except Exception as e:
            return f"Failed to create or read {log_file}: {e}"
            
    t = threading.Thread(target=_tail_file, args=(log_file, player), daemon=True)
    t.start()
    _active_watchers[log_file] = t
    
    msg = f"Started self-healing terminal watcher on {log_file}. I will alert you and suggest fixes if any exceptions occur."
    if player:
        player.write_log(f"PARIS: {msg}")
    return msg

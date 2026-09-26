import threading
import time
import os
from pathlib import Path

def idle_monitor(parameters: dict, player=None, speak=None, **kwargs) -> str:
    """
    Spawns a background thread that monitors a specific condition.
    When the condition is met, it alerts the user.
    """
    monitor_type = parameters.get("monitor_type")
    target = parameters.get("target")
    interval = parameters.get("interval", 5)
    timeout = parameters.get("timeout", 3600)
    
    if not monitor_type or not target:
        return "Error: monitor_type and target are required."
        
    def _worker():
        start_time = time.time()
        while time.time() - start_time < timeout:
            condition_met = False
            msg = ""
            
            try:
                if monitor_type == "file_exists":
                    if os.path.exists(target):
                        condition_met = True
                        msg = f"The file {target} has been created."
                elif monitor_type == "file_contains":
                    # target is expected to be "filepath|search_string"
                    parts = target.split("|", 1)
                    if len(parts) == 2:
                        filepath, search_str = parts
                        if os.path.exists(filepath):
                            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                                if search_str in f.read():
                                    condition_met = True
                                    msg = f"Found '{search_str}' in {filepath}."
                elif monitor_type == "timer":
                    # target is seconds
                    try:
                        seconds = int(target)
                        if time.time() - start_time >= seconds:
                            condition_met = True
                            msg = f"Timer for {seconds} seconds has finished."
                    except ValueError:
                        break
            except Exception as e:
                print(f"[IdleMonitor] Error: {e}")
                
            if condition_met:
                if player:
                    player.write_log(f"🔔 [Monitor Alert] {msg}")
                if speak:
                    speak(f"System: Background monitor alert. {msg} Please inform the user.")
                return
                
            time.sleep(interval)
            
        print(f"[IdleMonitor] Timeout reached for {monitor_type} on {target}")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    
    return f"Started background monitor for {monitor_type} on '{target}'. Will run silently and notify you when triggered."

TOOL = {
    "name": "idle_monitor",
    "scope": "exempt",
    "description": "Spawn a background worker to watch a file or wait for a condition while you sleep.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "monitor_type": {
                "type": "STRING",
                "description": "'file_exists', 'file_contains', or 'timer'."
            },
            "target": {
                "type": "STRING",
                "description": "File path, 'filepath|search_string', or seconds for timer."
            },
            "interval": {
                "type": "INTEGER",
                "description": "Polling interval in seconds (default 5)."
            },
            "timeout": {
                "type": "INTEGER",
                "description": "Maximum time to watch in seconds (default 3600)."
            }
        },
        "required": ["monitor_type", "target"]
    },
    "handler": idle_monitor
}

import json
import time
from pathlib import Path

SCRATCHPAD_FILE = Path(__file__).resolve().parent / "scratchpad.json"
TTL_SECONDS = 4 * 60 * 60 # 4 hours

def get_scratchpad() -> str:
    """Returns the current scratchpad text if < 4 hours old, else empty string."""
    if not SCRATCHPAD_FILE.exists():
        return ""
    try:
        with open(SCRATCHPAD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if time.time() - data.get("timestamp", 0) > TTL_SECONDS:
            return "" # Expired
            
        return data.get("text", "")
    except Exception:
        return ""

def set_scratchpad(text: str):
    if not text.strip():
        SCRATCHPAD_FILE.unlink(missing_ok=True)
        return
        
    data = {
        "timestamp": time.time(),
        "text": text
    }
    with open(SCRATCHPAD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

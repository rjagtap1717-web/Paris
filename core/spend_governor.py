import json
import time
from pathlib import Path
from datetime import datetime

# We place this in the same folder as long_term.json
SPEND_FILE = Path(__file__).resolve().parent.parent / "memory" / "daily_spend.json"
HARD_CAP_DAILY = 200

def _get_today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")

def check_spend_cap(tool_name: str) -> str | None:
    """Returns an error string if the AI has hit its limit, else None."""
    # Always allow these safe diagnostic tools even if cap is reached
    if tool_name in ["read_logs", "send_message", "search_history", "check_token_balance"]:
        return None
        
    if not SPEND_FILE.parent.exists():
        SPEND_FILE.parent.mkdir(parents=True, exist_ok=True)
        
    today = _get_today_str()
    data = {"date": today, "calls": 0, "last_call_time": 0}
    
    if SPEND_FILE.exists():
        try:
            with open(SPEND_FILE, "r") as f:
                saved = json.load(f)
                if saved.get("date") == today:
                    data = saved
        except Exception:
            pass
            
    # Check rate limit (Max 15 calls per minute = ~1 call every 4 seconds)
    now = time.time()
    if now - data.get("last_call_time", 0) < 4:
        return "[RATE_LIMITED] You are calling tools too fast. Please wait 4 seconds before your next action."
        
    # Check hard cap
    if data.get("calls", 0) >= HARD_CAP_DAILY:
        return f"[SPEND_CAP_REACHED] You have reached your hard limit of {HARD_CAP_DAILY} tool calls for today to prevent runaway costs. Stop planning and inform the user."
        
    return None

def record_tool_call():
    """Increments the daily counter."""
    if not SPEND_FILE.parent.exists():
        SPEND_FILE.parent.mkdir(parents=True, exist_ok=True)
        
    today = _get_today_str()
    data = {"date": today, "calls": 0, "last_call_time": time.time()}
    
    if SPEND_FILE.exists():
        try:
            with open(SPEND_FILE, "r") as f:
                saved = json.load(f)
                if saved.get("date") == today:
                    data = saved
                    data["last_call_time"] = time.time()
        except Exception:
            pass
            
    data["calls"] = data.get("calls", 0) + 1
    
    with open(SPEND_FILE, "w") as f:
        json.dump(data, f)

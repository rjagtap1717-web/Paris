import json
import urllib.request
from pathlib import Path

def check_token_balance(
    parameters: dict,
    player=None,
    session_memory=None,
) -> str:
    try:
        config_path = Path("config/api_keys.json")
        if not config_path.exists():
            return "Configuration file not found. Cannot check balance."

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        api_key = config.get("openrouter_api_key", "").strip()
        if not api_key:
            return "No OpenRouter API key found in the configuration."

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if "data" not in data:
            return "Failed to parse OpenRouter response."
            
        key_data = data["data"]
        limit = key_data.get("limit")
        limit_remaining = key_data.get("limit_remaining")
        usage = key_data.get("usage")
        is_free_tier = key_data.get("is_free_tier", False)
        
        if limit is None:
            return f"You are on an unlimited or unmetered plan. Total usage so far: ${usage:.4f}."
            
        msg = f"You have ${limit_remaining:.4f} remaining out of your ${limit:.4f} limit. "
        msg += f"(Total usage: ${usage:.4f}). "
        
        if is_free_tier:
            msg += "You are currently on the free tier."
            
        _log(msg, player)
        return msg

    except Exception as e:
        msg = f"Error checking token balance: {e}"
        _log(msg, player)
        return msg


def _log(message: str, player=None) -> None:
    print(f"[Balance] {message}")
    if player:
        try:
            player.write_log(f"SYS: {message}")
        except Exception:
            pass


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "check_token_balance",
    "description": "Checks the remaining OpenRouter API credits / LLM token balance limits.",
    "parameters": {
        "type": "OBJECT",
        "properties": {}
    },
    "handler": check_token_balance,
}

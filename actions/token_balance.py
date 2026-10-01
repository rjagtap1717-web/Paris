import json
import urllib.request
from pathlib import Path

def _check_openrouter(config: dict) -> dict:
    api_key = config.get("openrouter_api_key", "").strip()
    if not api_key:
        return {"status": "info", "message": "OpenRouter: Not configured (No API key found)."}

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        if "data" not in data:
            return {"status": "error", "message": "OpenRouter: Failed to parse API response."}
            
        key_data = data["data"]
        limit = key_data.get("limit")
        limit_remaining = key_data.get("limit_remaining")
        usage = key_data.get("usage")
        
        if limit is None:
            return {"status": "ok", "message": f"OpenRouter: Unlimited/Unmetered plan. Usage: ${usage:.4f}."}
            
        msg = f"OpenRouter: ${limit_remaining:.4f} remaining out of ${limit:.4f} limit. (Usage: ${usage:.4f})."
        
        # Alert if under $1.00
        if limit_remaining is not None and limit_remaining < 1.0:
            return {"status": "alert", "message": f"⚠️ ALERT: {msg}"}
            
        return {"status": "ok", "message": msg}
        
    except Exception as e:
        return {"status": "error", "message": f"OpenRouter: Error checking balance: {e}"}

def _check_rtrvr() -> dict:
    config_path = Path("config/token_balance.json")
    if not config_path.exists():
        return {"status": "info", "message": "Retriever (rtrvr): Not configured (token file missing)."}
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        tokens = config.get("rtrvr_tokens", 0)
        msg = f"Retriever (rtrvr): {tokens} credits remaining."
        
        if tokens < 20:
            return {"status": "alert", "message": f"⚠️ ALERT: {msg}"}
            
        return {"status": "ok", "message": msg}
    except Exception as e:
        return {"status": "error", "message": f"Retriever (rtrvr): Error reading tokens: {e}"}

def _check_gemini(config: dict) -> dict:
    api_key = config.get("gemini_api_key", "").strip()
    if not api_key:
        return {"status": "info", "message": "Gemini: Not configured (No API key found)."}
    
    # Gemini API operates on a rate-limit rather than a depletable credit pool (unless tied to GCP billing).
    return {
        "status": "info", 
        "message": "Gemini: Operates on rate-limits (e.g. 15 RPM for free tier) rather than a credit balance. Usage is active."
    }

def check_token_balance(parameters: dict, player=None, session_memory=None) -> str:
    service = parameters.get("service", "all").lower()
    
    # Load main config
    config_path = Path("config/api_keys.json")
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    results = []
    
    if service in ["all", "openrouter"]:
        results.append(_check_openrouter(config))
    if service in ["all", "rtrvr", "retriever"]:
        results.append(_check_rtrvr())
    if service in ["all", "gemini"]:
        results.append(_check_gemini(config))
        
    if not results:
        return f"Unknown service requested: {service}. Valid options are: all, openrouter, rtrvr, gemini."
        
    messages = []
    has_alerts = False
    
    for r in results:
        messages.append(r["message"])
        if r["status"] == "alert":
            has_alerts = True
            
    final_report = "\n".join(messages)
    
    if has_alerts:
        final_report = "🚨 URGENT: SOME RESOURCES ARE RUNNING CRITICALLY LOW!\n" + final_report
        
    _log(final_report, player)
    return final_report


def _log(message: str, player=None) -> None:
    print(f"[Balance] {message}")
    if player:
        try:
            player.write_log(f"SYS: {message}")
        except Exception:
            pass


def consume_rtrvr_token(amount: int = 1) -> bool:
    config_path = Path("config/token_balance.json")
    if not config_path.exists():
        return False
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    tokens = config.get("rtrvr_tokens", 0)
    if tokens < amount:
        return False
        
    config["rtrvr_tokens"] = tokens - amount
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        
    return True

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "check_token_balance",
    "scope": "local",
    "description": "Check API balances, credits, and resource limits for integrated services (OpenRouter, Retriever, Gemini). Can be used to proactively monitor costs or answer user queries about their remaining credits.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "service": {
                "type": "STRING",
                "description": "Which service to check. Options: 'all', 'openrouter', 'rtrvr', 'gemini'. Defaults to 'all'."
            }
        },
        "required": ["service"]
    },
    "handler": check_token_balance,
}

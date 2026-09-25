import asyncio
import requests
from config import get_config

EXEMPT_TOOLS = {
    "screen_process", "close_camera", "system_status", "recall_memory", 
    "save_memory", "weather_report", "undo", "manage_monitor", "reminder",
    "web_search", "browser_control", "youtube_video", "file_processor",
    "flight_finder", "open_app"
}

APPROVE_AT = 0.50
BLOCK_AT = 0.15
JEV_MODEL = "typesafe/jev-1.13"

def _ask_jev_sync(state: dict, questions: dict, api_key: str) -> dict:
    url = "https://openrouter.ai/api/alpha/decisions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": JEV_MODEL,
        "state": state,
        "questions": questions
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        answers = data.get("answers", {})
        results = {}
        for key in questions.keys():
            if key in answers and "noul" in answers[key]:
                results[key] = answers[key]["noul"]
            else:
                raise ValueError(f"Jev did not answer question: {key}")
        return results
    except Exception as e:
        print(f"[Jev] Error communicating with Jev API: {e}")
        return None

async def gate_tool_call(tool_name: str, tool_args: dict, context_info: str = "") -> tuple[str, str]:
    """
    Evaluates a tool call using Jev.
    Returns (outcome, reason) where outcome is "approve", "block", "review", or "exempt".
    """
    if tool_name in EXEMPT_TOOLS:
        return "exempt", "Tool is exempt from Jev gating."
        
    if tool_name == "file_controller" and tool_args.get("action") in ["list", "read", "find", "largest", "disk_usage", "info"]:
        return "exempt", "Read actions are exempt from Jev gating."
        
    config = get_config()
    jev_enabled = config.get("jev_enabled", True)
    api_key = config.get("openrouter_api_key", "")
    
    if not jev_enabled or not api_key:
        return "exempt", "Jev is disabled or OpenRouter API key is missing."
        
    state = {
        "tool_name": tool_name,
        "tool_args": tool_args,
        "conversation_context": context_info
    }
    
    questions = {
        "user_requested": {
            "type": "noul",
            "instructions": "The user asked for this action to be taken in the conversation context. The tool call matches the user's intent.",
        },
        "safe_to_run": {
            "type": "noul",
            "instructions": "This action is safe, low-risk, or reversible. It does not cause permanent data loss, send unwanted communications, or break the system.",
        }
    }
    
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, _ask_jev_sync, state, questions, api_key)
    
    if results is None:
        return "exempt", "Jev request failed; failing open."
        
    probs = list(results.values())
    
    if all(p >= APPROVE_AT for p in probs):
        return "approve", f"Jev approved (user_req={results['user_requested']:.2f}, safe={results['safe_to_run']:.2f})"
        
    if any(p <= BLOCK_AT for p in probs):
        failed = [f"{k}={v:.2f}" for k, v in results.items() if v <= BLOCK_AT]
        return "block", f"Jev blocked: {', '.join(failed)}"
        
    return "review", f"Jev uncertain (user_req={results['user_requested']:.2f}, safe={results['safe_to_run']:.2f})"

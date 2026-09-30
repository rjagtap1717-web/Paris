from memory.scratchpad_manager import set_scratchpad, get_scratchpad

def manage_scratchpad(parameters: dict, **kwargs) -> str:
    action = parameters.get("action", "read").lower().strip()
    
    if action == "read":
        pad = get_scratchpad()
        return pad if pad else "Scratchpad is currently empty (or expired)."
    elif action == "set":
        text = parameters.get("text", "")
        set_scratchpad(text)
        return "Scratchpad updated. This goal will remain active in your system prompt for 4 hours and will survive system reboots. The user will not have to repeat this context to you."
    elif action == "clear":
        set_scratchpad("")
        return "Scratchpad cleared."
    return "Invalid action. Use 'read', 'set', or 'clear'."

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "manage_scratchpad",
    "scope": "local",
    "description": "Sets a short-term memory 'scratchpad' or 'active goal' that you will automatically remember for the next 4 hours, even if the system restarts. Use this to remember what you are working on so you can seamlessly resume tasks if interrupted.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "read | set | clear"},
            "text": {"type": "STRING", "description": "The detailed goal or context to remember (only required for 'set')"}
        },
        "required": ["action"]
    },
    "handler": manage_scratchpad
}

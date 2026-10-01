import sys
import os
import time

def system_power(parameters: dict, **kwargs) -> str:
    action = parameters.get("action", "").lower().strip()
    
    if action == "restart":
        print("[PARIS] Initiating self-restart sequence (Exit Code 42)...")
        time.sleep(1)
        os._exit(42)
        
    elif action == "shutdown":
        print("[PARIS] Initiating graceful shutdown (Exit Code 0)...")
        time.sleep(1)
        os._exit(0)
        
    return "Invalid action. Use 'restart' or 'shutdown'."

TOOL = {
    "name": "system_power",
    "scope": "local",
    "description": "Use this to restart yourself to apply new code changes, or to shut yourself down completely if the user asks. CRITICAL: You MUST ask the user for explicit confirmation before calling this tool. (e.g. 'Are you sure you want me to restart?'). Do not execute this tool until they say yes.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'restart' to reboot immediately (applies code changes), or 'shutdown' to exit permanently."
            }
        },
        "required": ["action"]
    },
    "handler": system_power
}

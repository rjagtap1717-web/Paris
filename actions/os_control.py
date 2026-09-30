from actions.computer_control import computer_control as cc_handler
from actions.computer_settings import computer_settings as cs_handler

def os_control(parameters: dict, response=None, player=None, session_memory=None) -> str:
    action = parameters.get("action", "").lower().strip()
    
    # Actions that require visual UI interaction or coordinate/mouse math
    cc_actions = {
        "type", "smart_type", "resume_typing", "click", "double_click", "right_click", 
        "move", "drag", "wait", "clear_field", "focus_window", "screen_find", 
        "screen_click", "random_data", "user_data",
        "hotkey", "press", "scroll", "copy", "paste", "screenshot"
    }
    
    if action in cc_actions:
        return cc_handler(parameters, response, player, session_memory)
    else:
        # Route everything else (volume, brightness, window management, wifi) to settings
        return cs_handler(parameters, response, player, session_memory)

TOOL = {
    "name": "os_control",
    "scope": "local",
    "description": "Unified tool to control the local computer and OS. Use this for ANY local machine interaction. Handles BOTH visual input (mouse clicks, typing, finding elements on screen, scrolling) AND system hardware settings (volume, brightness, dark mode, wifi, window snapping, opening task manager, restarts).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Examples: type, click, scroll, screenshot, hotkey, volume_up, brightness_down, close_window, full_screen, toggle_wifi, sleep_display."
            },
            "text": {"type": "STRING", "description": "Text to type or paste"},
            "x": {"type": "INTEGER", "description": "X coordinate"},
            "y": {"type": "INTEGER", "description": "Y coordinate"},
            "keys": {"type": "STRING", "description": "Hotkey combo e.g. 'ctrl+c'"},
            "key": {"type": "STRING", "description": "Single key e.g. 'enter'"},
            "direction": {"type": "STRING", "description": "up | down | left | right"},
            "amount": {"type": "INTEGER", "description": "Scroll amount"},
            "description": {"type": "STRING", "description": "Element description to find on screen (for screen_click) OR semantic intent (for settings)"},
            "value": {"type": "INTEGER", "description": "Absolute value for volume/brightness"},
            "title": {"type": "STRING", "description": "Window title to focus"}
        },
        "required": ["action"]
    },
    "handler": os_control,
}

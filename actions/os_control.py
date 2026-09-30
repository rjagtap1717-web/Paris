from actions.computer_control import computer_control as cc_handler
from actions.computer_settings import computer_settings as cs_handler
import platform
import subprocess
import time

def _get_active_window_title() -> str:
    os_name = platform.system()
    try:
        if os_name == "Windows":
            script = "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; using System.Text; public class Win32 { [DllImport(\"user32.dll\")] public static extern IntPtr GetForegroundWindow(); [DllImport(\"user32.dll\")] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int count); }'; $hwnd = [Win32]::GetForegroundWindow(); $sb = New-Object System.Text.StringBuilder(256); $null = [Win32]::GetWindowText($hwnd, $sb, $sb.Capacity); $sb.ToString()"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=2)
            return res.stdout.strip()
        elif os_name == "Darwin":
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=2)
            return res.stdout.strip()
        else: # Linux
            res = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True, timeout=2)
            return res.stdout.strip()
    except Exception:
        return ""

def os_control(parameters: dict, response=None, player=None, session_memory=None) -> str:
    action = parameters.get("action", "").lower().strip()
    expected = parameters.get("expected_window", "").strip()
    
    if expected and action in {"type", "smart_type", "click", "double_click", "right_click", "hotkey", "press", "paste", "enter"}:
        current_window = _get_active_window_title()
        if current_window and expected.lower() not in current_window.lower():
            # Attempt to refocus once
            cc_handler({"action": "focus_window", "title": expected}, response, player, session_memory)
            time.sleep(0.5)
            # Re-check
            new_window = _get_active_window_title()
            if new_window and expected.lower() not in new_window.lower():
                return f"[ERROR] Focus Lock failed. Expected window containing '{expected}', but active window is '{new_window}'. Aborting action to prevent blind automation."
    
    # Actions that require visual UI interaction or coordinate/mouse math
    cc_actions = {
        "type", "smart_type", "resume_typing", "click", "double_click", "right_click", 
        "move", "drag", "wait", "clear_field", "focus_window", "screen_find", 
        "screen_click", "random_data", "user_data",
        "hotkey", "press", "scroll", "copy", "paste", "screenshot"
    }
    
    try:
        from core.resource_lock import acquire_lock, release_lock
        locked = acquire_lock("pyautogui", timeout=10)
        if not locked:
            return "[RESOURCE_LOCKED] The mouse/keyboard is currently being used by another background task. Please try again in a moment."
            
        if action in cc_actions:
            res = cc_handler(parameters, response, player, session_memory)
        else:
            # Route everything else (volume, brightness, window management, wifi) to settings
            title = parameters.get("title", "").strip()
            if title and action in {"full_screen", "fullscreen", "minimize", "maximize", "close_window", "snap_left", "snap_right", "switch_window"}:
                cc_handler({"action": "focus_window", "title": title}, response, player, session_memory)
                time.sleep(0.5)
            res = cs_handler(parameters, response, player, session_memory)
            
        return res
    finally:
        try:
            release_lock("pyautogui")
        except Exception:
            pass

TOOL = {
    "name": "os_control",
    "scope": "local",
    "description": "Unified tool to control the local computer and OS. Use this for ANY local machine interaction. Handles BOTH visual input (mouse clicks, typing, finding elements on screen, scrolling) AND system hardware settings (volume, brightness, dark mode, wifi, window snapping, opening task manager, restarts).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "Examples: type, click, scroll, screenshot, hotkey, volume_up, brightness_down, close_window, minimize_window, maximize_window, toggle_wifi, sleep_display. DO NOT use full_screen unless explicitly requested by the user."
            },
            "text": {"type": "STRING", "description": "Text to type or paste"},
            "x": {"type": "INTEGER", "description": "X coordinate"},
            "y": {"type": "INTEGER", "description": "Y coordinate"},
            "keys": {"type": "STRING", "description": "Hotkey combo e.g. 'ctrl+w' to close tabs"},
            "key": {"type": "STRING", "description": "Single key e.g. 'enter'"},
            "direction": {"type": "STRING", "description": "up | down | left | right"},
            "amount": {"type": "INTEGER", "description": "Scroll amount"},
            "description": {"type": "STRING", "description": "Element description to find on screen (for screen_click) OR semantic intent (for settings). CRITICAL RULE: NEVER use screen_click to click taskbar or desktop icons to open apps. ALWAYS use the open_app tool."},
            "value": {"type": "INTEGER", "description": "Absolute value for volume/brightness"},
            "title": {"type": "STRING", "description": "Window title to focus"},
            "expected_window": {"type": "STRING", "description": "Optional: Title fragment (e.g. 'Chrome') to guarantee focus BEFORE typing/clicking. Will auto-abort if a different app is active."}
        },
        "required": ["action"]
    },
    "handler": os_control,
}

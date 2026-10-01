from actions.word_controller import word_controller as word_handler
from actions.excel_controller import excel_controller as excel_handler
from actions.powerpoint_controller import powerpoint_controller as ppt_handler

def office_suite(parameters: dict, response=None, player=None, session_memory=None) -> str:
    app = parameters.get("app", "").lower().strip()
    
    try:
        from core.resource_lock import acquire_lock, release_lock
        locked = acquire_lock(f"com_{app}", timeout=10)
        if not locked:
            return f"[RESOURCE_LOCKED] The {app} app is currently being used by another background task. Please try again in a moment."
            
        if app == "word":
            res = word_handler(parameters, response, player, session_memory)
        elif app == "excel":
            res = excel_handler(parameters, response, player, session_memory)
        elif app in ["powerpoint", "ppt"]:
            res = ppt_handler(parameters, response, player, session_memory)
        else:
            res = "Error: You must specify app as 'word', 'excel', or 'powerpoint'."
            
        return res
    finally:
        try:
            release_lock(f"com_{app}")
        except Exception:
            pass

TOOL = {
    "name": "office_suite",
    "scope": "local",
    "description": "Control Microsoft Office (Word, Excel, PowerPoint) for opening, editing, saving and extracting text or data. Uses COM automation on Windows; requires Office installed.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "app": {
                "type": "STRING",
                "description": "word | excel | powerpoint"
            },
            "action": {
                "type": "STRING",
                "description": "The action to perform in the selected app. E.g. 'new', 'save', 'type' (Word), 'write_cell' (Excel), 'add_slide' (PowerPoint)."
            },
            # Common
            "file_path": {"type": "STRING", "description": "File path for save actions"},
            
            # Word params
            "text": {"type": "STRING", "description": "Text to type (Word)"},
            "format": {"type": "OBJECT", "description": "Formatting options for Word"},
            
            # Excel params
            "cell": {"type": "STRING", "description": "Cell reference like 'A1' (Excel)"},
            "value": {"type": "STRING", "description": "Value to write to cell (Excel)"},
            "format_opts": {"type": "OBJECT", "description": "Formatting options for Excel cell"},
            
            # PowerPoint params
            "slide_index": {"type": "INTEGER", "description": "1-based integer for slide index (PPT)"},
            "title": {"type": "STRING", "description": "Title text for slide (PPT)"},
            "body": {"type": "STRING", "description": "Body text for slide (PPT)"},
            "slide_type": {"type": "STRING", "description": "'title' | 'title_and_content' | 'blank' (PPT)"},
            "theme_name": {"type": "STRING", "description": "Name of the theme or path to .thmx (PPT)"},
            "image_path": {"type": "STRING", "description": "Absolute path to image (PPT)"}
        },
        "required": ["app", "action"]
    },
    "handler": office_suite,
}

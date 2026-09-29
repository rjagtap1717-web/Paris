import time

try:
    import win32com.client
    import pythoncom
    _WIN32 = True
except ImportError:
    _WIN32 = False

def word_controller(parameters: dict, response=None, player=None, session_memory=None) -> str:
    if not _WIN32:
        return "win32com is not installed. Cannot natively control Word."

    action = parameters.get("action", "").lower()
    text = parameters.get("text", "")
    formatting = parameters.get("formatting", {})
    
    try:
        pythoncom.CoInitialize()
        
        # Connect to existing Word or launch a new one
        try:
            word = win32com.client.GetActiveObject("Word.Application")
        except Exception:
            if action in ["new", "open"]:
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = True
            else:
                return "Microsoft Word is not currently open on the computer. Please use action 'new' first."
                
        doc = word.ActiveDocument if word.Documents.Count > 0 else None
        
        if action == "new":
            doc = word.Documents.Add()
            word.Visible = True
            word.Activate()
            return "Created new Word document. Word is now open and active."
            
        if not doc:
            return "Microsoft Word is open, but there is no active document. Use action 'new'."
            
        selection = word.Selection
        
        if action == "type":
            if not text:
                return "Please provide text to type."
            
            # Apply requested formatting
            if formatting:
                if "bold" in formatting: selection.Font.Bold = formatting["bold"]
                if "italic" in formatting: selection.Font.Italic = formatting["italic"]
                if "size" in formatting: selection.Font.Size = formatting["size"]
            
            # Type the text (handles newlines)
            selection.TypeText(text)
            
            # Reset formatting back to normal after typing
            selection.Font.Bold = False
            selection.Font.Italic = False
            
            return f"Typed {len(text)} characters into Word."
            
        elif action == "enter":
            selection.TypeParagraph()
            return "Pressed Enter (new paragraph)."
            
        elif action == "scroll_down":
            word.ActiveWindow.ActivePane.LargeScroll(Down=1)
            return "Scrolled down one page in Word."
            
        elif action == "scroll_up":
            word.ActiveWindow.ActivePane.LargeScroll(Up=1)
            return "Scrolled up one page in Word."
            
        elif action == "read":
            content = doc.Content.Text
            if len(content) > 4000:
                return f"Document is very long. Showing first 4000 characters:\n{content[:4000]}"
            return f"Current document text:\n{content}"
            
        elif action == "save":
            if text: # Using text param as file path
                doc.SaveAs(text)
                return f"Saved document to {text}"
            else:
                try:
                    doc.Save()
                    return "Saved document."
                except Exception:
                    return "Document has no existing path. Please provide a path in the 'text' parameter to save."
                    
        else:
            return f"Unknown action: '{action}'. Try: new, type, enter, scroll_down, scroll_up, read, save."
            
    except Exception as e:
        return f"Word control failed: {e}"
    finally:
        pythoncom.CoUninitialize()

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "word_controller",
    "scope": "local",
    "description": "Natively control Microsoft Word (COM integration). Use this INSTED of computer_control/vision when working in Word. Can flawlessly type, format text, scroll, read, and save.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "new | type | enter | scroll_down | scroll_up | read | save"
            },
            "text": {
                "type": "STRING",
                "description": "Text to type (for 'type') OR file path (for 'save')"
            },
            "formatting": {
                "type": "OBJECT",
                "description": "Optional dict for 'type': {\"bold\": true, \"italic\": false, \"size\": 14}"
            }
        },
        "required": ["action"]
    },
    "handler": word_controller
}

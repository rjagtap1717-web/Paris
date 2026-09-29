import time

try:
    import win32com.client
    import pythoncom
    _WIN32 = True
except ImportError:
    _WIN32 = False

def powerpoint_controller(parameters: dict, response=None, player=None, session_memory=None) -> str:
    if not _WIN32:
        return "win32com is not installed. Cannot natively control PowerPoint."

    action = parameters.get("action", "").lower()
    slide_index = parameters.get("slide_index")
    title = parameters.get("title", "")
    content = parameters.get("content", "")
    layout = parameters.get("layout", "title_and_content").lower()
    file_path = parameters.get("file_path", "")
    
    try:
        pythoncom.CoInitialize()
        
        # Connect to existing PowerPoint or launch a new one
        try:
            ppt = win32com.client.GetActiveObject("PowerPoint.Application")
        except Exception:
            if action in ["new", "open"]:
                ppt = win32com.client.Dispatch("PowerPoint.Application")
                ppt.Visible = True
            else:
                return "Microsoft PowerPoint is not currently open on the computer. Please use action 'new' first."
                
        pres = ppt.ActivePresentation if ppt.Presentations.Count > 0 else None
        
        if action == "new":
            pres = ppt.Presentations.Add()
            return "Created new PowerPoint presentation. PowerPoint is now open and active."
            
        if not pres:
            return "Microsoft PowerPoint is open, but there is no active presentation. Use action 'new'."
            
        if action == "add_slide":
            # 1 = Title Slide, 2 = Title and Content, 12 = Blank
            layouts = {
                "title": 1,
                "title_and_content": 2,
                "blank": 12
            }
            layout_id = layouts.get(layout, 2)
            
            idx = pres.Slides.Count + 1
            slide = pres.Slides.Add(idx, layout_id)
            
            # Select the slide in the UI so the user can see it
            slide.Select()
            
            if title and slide.Shapes.HasTitle:
                slide.Shapes.Title.TextFrame.TextRange.Text = title
                
            if content and slide.Shapes.Count >= 2:
                # Shape 2 is typically the main body content box in Layout 2
                slide.Shapes(2).TextFrame.TextRange.Text = content
                
            return f"Added new slide (index {idx}) with layout '{layout}'."
            
        elif action == "update_slide":
            if not slide_index: 
                return "Please provide 'slide_index' (1-based integer)."
            if slide_index < 1 or slide_index > pres.Slides.Count:
                return f"Slide index {slide_index} out of bounds (1-{pres.Slides.Count})."
                
            slide = pres.Slides(slide_index)
            slide.Select()
            
            if title and slide.Shapes.HasTitle:
                slide.Shapes.Title.TextFrame.TextRange.Text = title
            
            if content and slide.Shapes.Count >= 2:
                slide.Shapes(2).TextFrame.TextRange.Text = content
                
            return f"Updated text on slide {slide_index}."
            
        elif action == "read_slide":
            if not slide_index: 
                return "Please provide 'slide_index'."
            if slide_index < 1 or slide_index > pres.Slides.Count:
                return f"Slide index {slide_index} out of bounds."
                
            slide = pres.Slides(slide_index)
            texts = []
            for i in range(1, slide.Shapes.Count + 1):
                shape = slide.Shapes(i)
                if shape.HasTextFrame and shape.TextFrame.HasText:
                    texts.append(f"Shape {i}: {shape.TextFrame.TextRange.Text}")
            
            out = "\n".join(texts)
            return f"Slide {slide_index} contents:\n{out if out else '[No text on slide]'}"
            
        elif action == "go_to_slide":
            if not slide_index: 
                return "Please provide 'slide_index'."
            if slide_index < 1 or slide_index > pres.Slides.Count:
                return f"Slide index {slide_index} out of bounds."
                
            pres.Slides(slide_index).Select()
            return f"Moved view to slide {slide_index}."
            
        elif action == "save":
            if file_path:
                pres.SaveAs(file_path)
                return f"Saved presentation to {file_path}"
            else:
                try:
                    pres.Save()
                    return "Saved presentation."
                except Exception:
                    return "Presentation has no existing path. Please provide a path in 'file_path' to save."
                    
        else:
            return f"Unknown action: '{action}'. Try: new, add_slide, update_slide, read_slide, go_to_slide, save."
            
    except Exception as e:
        return f"PowerPoint control failed: {e}"
    finally:
        pythoncom.CoUninitialize()

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "powerpoint_controller",
    "scope": "local",
    "description": "Natively control Microsoft PowerPoint (COM integration). Create presentations, add slides, update slide text, and navigate directly without UI automation.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "new | add_slide | update_slide | read_slide | go_to_slide | save"
            },
            "slide_index": {
                "type": "INTEGER",
                "description": "1-based integer for slide index"
            },
            "title": {
                "type": "STRING",
                "description": "Title text for slide"
            },
            "content": {
                "type": "STRING",
                "description": "Body text for slide"
            },
            "layout": {
                "type": "STRING",
                "description": "For add_slide: 'title' | 'title_and_content' | 'blank'"
            },
            "file_path": {
                "type": "STRING",
                "description": "File path for save action"
            }
        },
        "required": ["action"]
    },
    "handler": powerpoint_controller
}

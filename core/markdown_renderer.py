import mistune

_markdown = mistune.create_markdown(
    plugins=['strikethrough', 'table', 'url', 'task_lists']
)

def render_markdown(text: str) -> str:
    """
    Converts raw markdown text to HTML format for display in the PyQt6 QTextEdit.
    Supports tables, bold, italics, code blocks, lists, and URLs.
    """
    if not text:
        return ""
        
    html = _markdown(text)
    
    # Optional styling wrapper can be added here if PyQt6 needs specific font
    # tags to render well, but by default PyQt6 respects basic HTML tags.
    # In ui.py, QTextEdit is typically configured with base fonts via Qt stylesheets.
    styled_html = f"""
    <div style="font-family: 'Inter', 'Segoe UI', sans-serif; line-height: 1.5;">
        {html}
    </div>
    """
    return styled_html

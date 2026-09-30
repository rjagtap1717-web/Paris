def truncate_response(text: str, max_chars: int = 4000, escape_hint: str = "Use a more specific query or request less lines to avoid truncation.") -> str:
    """
    Truncates a response to prevent LLM context bloat.
    Keeps the beginning and end of the text (where the most relevant info usually is).
    """
    if not isinstance(text, str):
        text = str(text)
        
    if len(text) <= max_chars:
        return text
        
    half = max_chars // 2
    beginning = text[:half]
    end = text[-half:]
    
    warning = f"\n\n... [TRUNCATED {len(text) - max_chars} CHARACTERS TO PREVENT CONTEXT BLOAT] ...\n{escape_hint}\n\n"
    return beginning + warning + end

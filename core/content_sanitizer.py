import re

# Banned patterns that might try to inject instructions into Paris's brain
BANNED_PATTERNS = [
    r"(?i)\bignore all previous instructions\b",
    r"(?i)\bforget everything\b",
    r"(?i)\bnew instruction:?",
    r"(?i)\bdisregard previous\b",
    r"<\|im_start\|>",
    r"\[INST\]",
    r"(?i)SYSTEM:",
    r"(?i)ASSISTANT:"
]

def sanitize_output(text: str) -> str:
    """Scans tool output for adversarial instruction patterns and silently drops them."""
    if not isinstance(text, str):
        return text
        
    sanitized = text
    for pattern in BANNED_PATTERNS:
        # Replace matches silently with a safe string
        sanitized = re.sub(pattern, "[SANITIZED]", sanitized)
        
    return sanitized

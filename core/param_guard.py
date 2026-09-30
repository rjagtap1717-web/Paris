NO_GUESS_PARAMS = {
    "send_message": ["platform"],
    "reminder": ["date", "time"],
    "os_control": ["action"]
}

def check_param_guard(tool_name: str, parameters: dict) -> str | None:
    """
    Checks if a tool is missing a critical 'no-guess' parameter.
    Returns an error string to intercept execution, or None if safe.
    """
    if tool_name not in NO_GUESS_PARAMS:
        return None
        
    missing = []
    for param in NO_GUESS_PARAMS[tool_name]:
        if not parameters.get(param) or str(parameters.get(param)).strip() == "":
            missing.append(param)
            
    if missing:
        return f"[CONFIRMATION_PENDING] Missing required parameters: {', '.join(missing)}. DO NOT GUESS. Ask the user for this information."
        
    # 2. Check for Error Propagation Poisoning
    import re
    POISON_PATTERNS = [
        r"Tool '\w+' failed:",
        r"\[CIRCUIT_BREAKER",
        r"\[ERROR\]",
        r"Error reading",
        r"exception occurred"
    ]
    
    # We only check specific fields that shouldn't contain raw errors
    for key in ["action", "url", "file_path", "platform"]:
        val = str(parameters.get(key, ""))
        if val:
            for pattern in POISON_PATTERNS:
                if re.search(pattern, val, re.IGNORECASE):
                    return f"[ERROR] Possible error propagation detected. You passed an error message into the '{key}' parameter: '{val}'. Do not blindly copy-paste errors into parameters."
                    
    return None

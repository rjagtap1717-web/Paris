def check_circuit_breaker(tool_name: str, parameters: dict, result: str, session_memory: dict) -> str:
    """
    Tracks if a tool fails repeatedly. If it fails twice identically, intercepts the result
    and forces the LLM to stop retrying.
    """
    if not isinstance(result, str) or session_memory is None:
        return result
        
    if "circuit_breaker" not in session_memory:
        session_memory["circuit_breaker"] = {}
        
    cb = session_memory["circuit_breaker"]
    
    # We define a failure heuristically: if the word "error" or "failed" is in the output
    is_error = "error" in result.lower() or "failed" in result.lower()
    
    # Identify the exact action
    action = str(parameters.get("action", ""))
    key = f"{tool_name}:{action}"
    
    if is_error:
        cb[key] = cb.get(key, 0) + 1
        
        if cb[key] >= 2:
            return f"[CIRCUIT_BREAKER FATAL] The tool '{tool_name}' failed 2 times in a row. Stop retrying this action! Take a screenshot to diagnose, or ask the user for help. Original error: {result}"
    else:
        # Success! Reset counter
        cb[key] = 0
        
    return result

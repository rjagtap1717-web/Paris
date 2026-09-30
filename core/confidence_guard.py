MUST_VERIFY_BEFORE_CONFIRM = {
    "send_message",
    "reminder",
    "office_suite",
    "coding_agent"
}

def enforce_confidence(tool_name: str, result: str) -> str:
    """
    Appends a behavioral instruction to the tool output for actions that the AI 
    cannot confidently verify itself. This forces the LLM to use hedged language
    instead of false certainty ("Done! It works perfectly!").
    """
    if not isinstance(result, str):
        return result
        
    if tool_name not in MUST_VERIFY_BEFORE_CONFIRM:
        return result
        
    return f"{result}\n\n[CONFIDENCE_GUARD] You just executed a critical action ({tool_name}). When responding to the user, DO NOT declare 100% success (e.g. 'Done! It works perfectly!'). You MUST use hedged, uncertain language (e.g. 'I believe I sent the message, please verify', or 'I wrote the code, but you should test it to be sure')."

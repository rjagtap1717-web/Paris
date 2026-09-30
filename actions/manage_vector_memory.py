from memory.vector_brain import store_fact, search_facts

def manage_vector_memory(parameters: dict, **kwargs) -> str:
    action = parameters.get("action", "").lower().strip()
    text = parameters.get("text", "")
    
    if action == "store":
        if not text:
            return "Error: You must provide 'text' to store a fact."
        return store_fact(text)
        
    elif action == "search":
        if not text:
            return "Error: You must provide 'text' to search for."
        facts = search_facts(text, n_results=3)
        if facts:
            return "Found the following related memories from the semantic vector brain:\n- " + "\n- ".join(facts)
        return "No related memories found."
        
    return "Invalid action. Use 'store' or 'search'."

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "manage_vector_memory",
    "scope": "local",
    "description": "Access your Tier 3 Vector Brain (Semantic Database). Use 'store' to permanently memorize random long-term facts about the user (e.g., 'User hates tailwind', 'User's dog is named Max'). Use 'search' to semantically search your brain when you need to recall context about something.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "'store' or 'search'"},
            "text": {"type": "STRING", "description": "The fact to store, or the query to search for"}
        },
        "required": ["action", "text"]
    },
    "handler": manage_vector_memory
}

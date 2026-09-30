import os
import time
import json
import re
from pathlib import Path
import threading

# Tier 3 Long-Term Memory (Lightweight JSON Store)
DB_PATH = Path(__file__).resolve().parent / "semantic_memory.json"
_lock = threading.Lock()

def _get_facts() -> list:
    if not DB_PATH.exists():
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_facts(facts: list):
    with _lock:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(facts, f, indent=2, ensure_ascii=False)

def store_fact(fact: str) -> str:
    """Stores a fact permanently."""
    if not fact or not fact.strip():
        return "[ERROR] Fact is empty."
        
    facts = _get_facts()
    # Deduplicate
    if fact in [f.get("text") for f in facts]:
        return "Fact is already in memory."
        
    facts.append({
        "text": fact,
        "timestamp": time.time()
    })
    _save_facts(facts)
    return f"Fact memorized permanently: '{fact}'"

def _tokenize(text: str) -> set:
    words = re.findall(r'\b\w+\b', text.lower())
    # Remove common stop words
    stop_words = {"a", "an", "the", "is", "are", "was", "were", "to", "in", "for", "of", "on", "with", "and", "or", "my", "your", "his", "her", "their", "user"}
    return set(w for w in words if w not in stop_words)

def search_facts(query: str, n_results: int = 3) -> list[str]:
    """Searches memory using keyword overlap."""
    facts = _get_facts()
    if not facts:
        return []
        
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []
        
    scored = []
    for f in facts:
        text = f.get("text", "")
        fact_tokens = _tokenize(text)
        overlap = len(query_tokens.intersection(fact_tokens))
        if overlap > 0:
            # Score = overlap count / length of fact to heavily favor precise matches
            score = overlap / max(1.0, len(fact_tokens)**0.5)
            scored.append((score, text))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for score, text in scored[:n_results]]

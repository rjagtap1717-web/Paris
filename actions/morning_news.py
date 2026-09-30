import concurrent.futures
from actions.web_search import web_search

def get_morning_news(parameters: dict, player=None, session_memory=None) -> str:
    """
    Fetches specific morning news in parallel to avoid startup latency.
    """
    queries = [
        "Did Barcelona, Manchester City, or Chelsea win a trophy recently?",
        "MAJOR global breaking news today crisis nuclear alien world-changing"
    ]
    
    results = []
    
    # Run the web searches in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_query = {
            executor.submit(web_search, {"query": q}): q for q in queries
        }
        for future in concurrent.futures.as_completed(future_to_query):
            try:
                res = future.result()
                results.append(res)
            except Exception as e:
                results.append(f"Search failed: {e}")
                
    return (
        "--- FOOTBALL TROPHY CHECK ---\n"
        f"{results[0]}\n\n"
        "--- MAJOR CRAZY NEWS CHECK ---\n"
        f"{results[1]}"
    )

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "get_morning_news",
    "scope": "local",
    "description": "Quickly checks if Barcelona, Man City, or Chelsea won a trophy, and if there is any major crazy world news (nuclear, alien, etc).",
    "parameters": {
        "type": "OBJECT",
        "properties": {}
    },
    "handler": get_morning_news,
}

import asyncio
import os
import sys
from pathlib import Path
sys.path.insert(0, r"E:\Paris")

from core.action_loader import ActionRegistry


async def test_actions():
    print("Loading actions...")
    loader = ActionRegistry()
    loader.discover("E:\\Paris\\actions")
    
    memory = {}
    ctx = {"session_memory": memory}
    
    print(f"Loaded {len(loader.names())} actions.")
    
    test_cases = {
        "read_logs": {"lines": 5},
        "system_monitor": {},
        "file_processor": {"action": "read", "path": "E:\\Paris\\requirements.txt"},
        "browser_control": {"action": "get_url"},
        "computer_control": {"action": "wait", "seconds": 1},
        "computer_settings": {"action": "focus_search"},
        "open_app": {"app_name": "notepad"},
        "web_search": {"query": "test"},
        "weather_report": {"location": "New York"},
        "youtube_video": {"action": "search", "query": "never gonna give you up"},
    }
    
    failed = []
    
    for action_name, params in test_cases.items():
        print(f"\n--- Testing {action_name} ---")
        try:
            # Check if handler is async or sync
            rec = loader._actions.get(action_name)
            if not rec:
                print(f"Action {action_name} not found!")
                failed.append(action_name)
                continue
                
            from core.action_loader import _call_handler
            import inspect
            
            res = _call_handler(rec.handler, params, ctx)
            if inspect.iscoroutine(res):
                res = await res
                
            print(f"Result: str length {len(str(res))}")
        except Exception as e:
            print(f"FAILED {action_name}: {e}")
            failed.append(action_name)
            
    print("\n====================")
    if failed:
        print(f"Failed actions: {failed}")
    else:
        print("All tested actions passed!")
        
    os._exit(0) if not failed else os._exit(1)

if __name__ == "__main__":
    asyncio.run(test_actions())

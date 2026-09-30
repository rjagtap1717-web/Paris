import json
import os
import subprocess
from pathlib import Path
from actions.token_balance import consume_rtrvr_token

def rtrvr_control(parameters: dict, player=None, session_memory=None) -> str:
    action = parameters.get("action", "scrape")
    url = parameters.get("url", "")
    task = parameters.get("task", "")
    target = parameters.get("target", "extension")
    schema = parameters.get("schema", None)
    
    if not url and action == "scrape":
        return "Error: URL is required for scraping."
    if not task and action == "agent":
        return "Error: Task description is required for agent runs."
        
    # Prevent consuming tokens if in cloud mode without balance
    if target == "cloud":
        if not consume_rtrvr_token(1):
            return "Error: Insufficient Retriever tokens to run in Cloud mode. Your balance is zero."
            
    command = ["rtrvr"]
    if action == "scrape":
        command.extend(["scrape", "--url", url, "--target", target, "--json"])
    elif action == "agent":
        command.extend(["run", task, "--url", url, "--target", target, "--json"])
    else:
        return f"Error: Unknown action '{action}'"
        
    # Handle Structured Data Extraction (Schema)
    schema_path = "rtrvr_temp_schema.json"
    if schema and isinstance(schema, dict):
        try:
            with open(schema_path, "w", encoding="utf-8") as f:
                json.dump(schema, f)
            command.extend(["--schema-file", schema_path])
        except Exception as e:
            return f"Error writing schema file: {e}"

    try:
        if player:
            player.write_log(f"SYS: Running Retriever {action} on {url} (Target: {target})...")
            
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Cleanup temporary schema file
        if os.path.exists(schema_path):
            os.remove(schema_path)
        
        # Automatic Failover for Extension Mode
        if result.returncode != 0:
            err_msg = result.stderr.strip().lower()
            if target == "extension" and ("extension" in err_msg or "timeout" in err_msg or "offline" in err_msg or "not found" in err_msg):
                return "[CONFIRMATION_PENDING] Your browser extension isn't responding or is closed. Should I use 1 cloud token to continue, or will you open the browser?"
            return f"Retriever execution failed. Error:\n{result.stderr.strip()}"
            
        try:
            parsed = json.loads(result.stdout)
            if isinstance(parsed, dict) and "data" in parsed:
                data = str(parsed["data"])
                if len(data) > 4000:
                    return f"Result (Truncated):\n{data[:4000]}...\n[Content truncated to save tokens]"
                return f"Result:\n{data}"
            return result.stdout.strip()
        except json.JSONDecodeError:
            out = result.stdout.strip()
            if len(out) > 4000:
                return f"Result (Truncated):\n{out[:4000]}...\n[Content truncated to save tokens]"
            return out
            
    except subprocess.TimeoutExpired:
        if os.path.exists(schema_path):
            os.remove(schema_path)
        if target == "extension":
            return "[CONFIRMATION_PENDING] Your browser extension isn't responding. Should I use 1 cloud token to continue, or will you open the browser?"
        return "Error: Retriever execution timed out after 120 seconds."
    except FileNotFoundError:
        return "Error: 'rtrvr' command not found. Please ensure @rtrvr-ai/cli is installed globally."
    except Exception as e:
        if os.path.exists(schema_path):
            os.remove(schema_path)
        return f"Unexpected error during Retriever execution: {e}"


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "rtrvr_control",
    "scope": "local",
    "description": "Automate the web using Retriever AI. Best for complex DOM extraction, bypassing Captchas, and interacting with authenticated sites (via 'extension' target). NOTE: If there is ambiguity (e.g. multiple accounts to choose from), return [CONFIRMATION_PENDING] and ask the user BEFORE calling this.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "'scrape' for extracting the page data, or 'agent' for complex tasks like filling forms."
            },
            "url": {
                "type": "STRING",
                "description": "The target URL."
            },
            "task": {
                "type": "STRING",
                "description": "If action is 'agent', describe what the AI agent should do."
            },
            "target": {
                "type": "STRING",
                "description": "Execution mode: 'extension' (uses local authenticated browser, free) or 'cloud' (headless, uses credits). Default should be 'extension'."
            },
            "schema": {
                "type": "OBJECT",
                "description": "Optional. A JSON schema defining the exact fields you want to extract. e.g. {\"type\": \"object\", \"properties\": {\"price\": {\"type\": \"string\"}}}"
            }
        },
        "required": ["action", "url"]
    },
    "handler": rtrvr_control,
}

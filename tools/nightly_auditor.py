import os
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime

# Setup paths relative to the Paris root
BASE_DIR = Path(__file__).resolve().parent.parent
ACTIONS_DIR = BASE_DIR / "actions"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = BASE_DIR / "config" / "api_keys.json"
MEMORY_FILE = LOGS_DIR / "audit_memory.json"
REPORT_FILE = LOGS_DIR / "audit_report.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

PROMPT = """You are a Senior Python Developer and Security Auditor working on the 'Paris' AI assistant framework.
Your task is to review the following Python files. Find bugs, unhandled exceptions, unused features, or bad performance logic.

CRITICAL FOCUS (TOOL OVERLAPS): Pay special attention to the `TOOL` dictionary at the bottom of these files. If two different tools have overlapping capabilities (e.g. two tools can 'browse the web' or 'edit excel'), flag it! You must suggest updating the "description" fields to strictly demarcate them so the Paris AI never gets confused about which one to use.

IMPORTANT: Do not just run the same test. Look for edge cases, missing error boundaries, and race conditions.

You must output your findings EXACTLY as a JSON array of objects. Do not wrap it in markdown. Do not include any intro text.
Each object must strictly follow this JSON schema:
{
  "severity": "CRITICAL" | "MEDIUM" | "LOW",
  "resolution_track": "AUTO_FIXABLE" | "PAIR_PROGRAMMING",
  "file": "<filename>",
  "issue": "<detailed explanation of the bug or code smell>",
  "ai_recommendation": "<exact technical steps to fix>"
}

Rules for 'resolution_track':
- 'AUTO_FIXABLE': Missing imports, syntax errors, PEP 8 fixes, unused variables, minor deterministic logic.
- 'PAIR_PROGRAMMING': Tool overlaps/ambiguities, core architectural changes, UI/UX flows, delicate timing logic, plugin refactors.

Files to analyze:
"""

def get_api_key():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg.get("openrouter_api_key", "").strip()
    except Exception:
        return ""

def get_target_files(num_files=3):
    """Picks files that haven't been audited recently to ensure dynamic testing."""
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    else:
        memory = {}

    all_files = list(ACTIONS_DIR.glob("*.py"))
    
    # Sort files by least recently audited
    def get_audit_time(fpath):
        return memory.get(fpath.name, 0)
        
    sorted_files = sorted(all_files, key=get_audit_time)
    
    # Pick top N files
    targets = sorted_files[:num_files]
    
    # Update memory
    now = time.time()
    for t in targets:
        memory[t.name] = now
        
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)
        
    return targets

def run_audit():
    print("Starting Paris Nightly Audit...")
    api_key = get_api_key()
    if not api_key:
        print("No OpenRouter API key found. Aborting audit.")
        return

    targets = get_target_files(3)
    if not targets:
        print("No files found to audit.")
        return

    print(f"Auditing files: {[t.name for t in targets]}")
    
    # Combine file contents for the LLM context
    file_contents = ""
    for target in targets:
        try:
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
            file_contents += f"\n\n--- FILE: {target.name} ---\n{content}\n"
        except Exception as e:
            print(f"Could not read {target.name}: {e}")

    full_prompt = PROMPT + file_contents

    # Call OpenRouter API
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": "anthropic/claude-3.5-sonnet", # High intelligence for auditing
            "messages": [{"role": "user", "content": full_prompt}],
            "temperature": 0.2
        }).encode("utf-8")
    )
    
    print("Analyzing codebase (this may take a minute)...")
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode())
            result_text = data["choices"][0]["message"]["content"]
            
            # Clean up potential markdown formatting wrapping the JSON
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
                
            report_data = json.loads(result_text.strip())
            
            # Add metadata
            final_report = {
                "timestamp": datetime.now().isoformat(),
                "files_audited": [t.name for t in targets],
                "findings": report_data
            }
            
            with open(REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(final_report, f, indent=4)
                
            print(f"Audit complete! Found {len(report_data)} issues. Report saved to {REPORT_FILE}")
            
    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    run_audit()

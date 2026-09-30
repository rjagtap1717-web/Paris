import os
import json
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
CONFIG_FILE = BASE_DIR / "config" / "api_keys.json"
REPORT_FILE = LOGS_DIR / "audit_report.json"

PROMPT_TEMPLATE = """You are an automated code fixer. Your job is to safely apply the following recommended fix to the Python file.
IMPORTANT RULES:
1. You must output the ENTIRE modified Python file.
2. DO NOT include any markdown formatting like ```python or ```. Just the raw code.
3. DO NOT add any conversational text.
4. Only apply the fix requested. Do not change other architecture.

--- ISSUE TO FIX ---
{issue}

--- RECOMMENDATION ---
{recommendation}

--- ORIGINAL FILE CONTENT ---
{content}
"""

def get_api_key():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            return cfg.get("openrouter_api_key", "").strip()
    except Exception:
        return ""

def apply_fix_with_llm(api_key: str, file_path: Path, issue: str, recommendation: str) -> bool:
    print(f"  -> Attempting to fix {file_path.name}...")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        full_prompt = PROMPT_TEMPLATE.format(
            issue=issue,
            recommendation=recommendation,
            content=content
        )
        
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "anthropic/claude-3.5-sonnet", # High precision for coding
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.0
            }).encode("utf-8")
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode())
            new_code = data["choices"][0]["message"]["content"]
            
            # Strip markdown if the LLM ignores instructions
            new_code = new_code.strip()
            if new_code.startswith("```python"):
                new_code = new_code[9:]
            elif new_code.startswith("```"):
                new_code = new_code[3:]
            if new_code.endswith("```"):
                new_code = new_code[:-3]
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_code.strip() + "\n")
                
        print(f"  [SUCCESS] Patched {file_path.name}")
        return True
        
    except Exception as e:
        print(f"  [FAILED] Could not fix {file_path.name}: {e}")
        return False

def run_auto_fixer():
    print("Starting Paris Auto-Fixer...")
    
    if not REPORT_FILE.exists():
        print("No audit report found. Run the nightly auditor first.")
        return
        
    with open(REPORT_FILE, "r", encoding="utf-8") as f:
        report = json.load(f)
        
    findings = report.get("findings", [])
    auto_fixes = [f for f in findings if f.get("resolution_track") == "AUTO_FIXABLE"]
    
    if not auto_fixes:
        print("No AUTO_FIXABLE issues found in the report.")
        return
        
    api_key = get_api_key()
    if not api_key:
        print("OpenRouter API key is required to run the auto-fixer.")
        return
        
    print(f"Found {len(auto_fixes)} Auto-Fixable issues. Applying patches...\n")
    
    success_count = 0
    for fix in auto_fixes:
        file_rel_path = fix.get("file")
        if not file_rel_path:
            continue
            
        file_path = BASE_DIR / file_rel_path
        if not file_path.exists():
            print(f"  [FAILED] File {file_rel_path} does not exist.")
            continue
            
        if apply_fix_with_llm(api_key, file_path, fix.get("issue"), fix.get("ai_recommendation")):
            success_count += 1
            
    print(f"\nAuto-Fixer complete! Successfully patched {success_count}/{len(auto_fixes)} issues.")
    
    # Optionally, we could remove the fixed items from the JSON report here so they aren't read twice.
    # For now, we leave the report as a historic record until the next night.

if __name__ == "__main__":
    run_auto_fixer()

import json
from core import gemini

def critic_agent(parameters: dict, response=None, player=None, session_memory=None) -> str:
    task = parameters.get("task", "")
    work = parameters.get("work", "")
    
    if not task or not work:
        return "Please provide both 'task' (the original goal) and 'work' (the output to be reviewed)."
        
    prompt = f"""You are a strict, senior Peer Reviewer Critic AI.
Your job is to review the following WORK against the original TASK.

CRITICAL RULES:
1. If the 'WORK TO REVIEW' appears to be a summary, outline, or high-level description of the work rather than the literal exact raw text/code of the work itself, you MUST fail it immediately. Tell the agent they must submit the exact raw content for peer review.
2. If the work completely satisfies the task and has no critical errors, set "status": "PASS".
3. If the work involves OS control or window management (minimize, maximize, fullscreen, close), VERIFY that the agent intends to use explicit target window titles/locks. If they plan to fire blind keystrokes without specifying the `title` parameter in `os_control`, FAIL them.
4. If the work fails, is incomplete, has typos, or misses any subtle details from the task, set "status": "FAIL" and provide a detailed "feedback" string.

You must return your response in purely valid JSON format.

TASK:
{task}

WORK TO REVIEW:
{work}

Return only JSON:
{{
    "status": "PASS" | "FAIL",
    "feedback": "Your detailed feedback here (empty if PASS)"
}}
"""
    
    try:
        resp = gemini.call(prompt, tier=gemini.SMART, timeout_ms=30000)
        if not resp:
            return "Critic Agent failed to generate a response."
            
        text = resp.text.strip()
        
        # Clean up JSON formatting
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        data = json.loads(text.strip())
        
        status = data.get("status", "FAIL")
        feedback = data.get("feedback", "")
        
        if status == "PASS":
            return "CRITIC REVIEW: PASS. The work is excellent and ready to deliver to the user."
        else:
            return f"CRITIC REVIEW: FAIL.\nFEEDBACK: {feedback}\n\nYou MUST fix these issues using your tools before completing the task."
            
    except Exception as e:
        return f"Critic Agent encountered an error while reviewing: {e}"

# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "critic_agent",
    "scope": "local",
    "description": "An internal senior peer-reviewer. Use this to double-check your own work (e.g., text, code, document content, or planned OS window control actions) BEFORE delivering it to the user. It will grade your work PASS or FAIL. WARNING: You MUST submit the EXACT raw text or exact planned action parameters to the 'work' parameter. Do NOT submit a summary. If you submit a summary or plan blind keystrokes without explicit window targets, the critic will automatically fail you.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "task": {
                "type": "STRING",
                "description": "The original goal or request from the user."
            },
            "work": {
                "type": "STRING",
                "description": "The EXACT raw text/content of your generated output, code, or draft that needs to be reviewed. DO NOT SUMMARIZE."
            }
        },
        "required": ["task", "work"]
    },
    "handler": critic_agent
}

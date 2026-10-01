# Paris Error Registry & Bug History

This file is an append-only registry of critical bugs, crashes, and logic errors resolved in Paris.
By documenting the Root Cause and the exact Fix, we ensure future AI agents do not accidentally revert structural workarounds.

## Format
```markdown
### [YYYY-MM-DD] Error/Symptom
- **Root Cause**: What fundamentally broke.
- **Fix**: How it was resolved.
- **Files Changed**: `file.py`
- **DO NOT REVERT**: <Reason why this specific fix must remain intact>
```

---

### [2026-10-01] UI Automation Whack-a-Mole (Taskbar Clicking)
- **Root Cause**: `browser_control.py` instructed the agent to use `computer_control` for open browsers. The agent used PyAutoGUI to blindly click the taskbar, failing to open Chrome properly.
- **Fix**: Updated `os_control.py` and `open_app.py` descriptions to strictly enforce native app launching for URLs. Added Critic rules to fail taskbar click attempts.
- **Files Changed**: `actions/os_control.py`, `actions/open_app.py`, `actions/critic_agent.py`
- **DO NOT REVERT**: Never instruct the agent to use visual taskbar clicking to launch apps. It breaks focus and ruins downstream macros.

### [2026-10-01] ImportError: cannot import name 'genai'
- **Root Cause**: Python 3.9 namespace package resolution fails with `from google import genai`.
- **Fix**: Changed the import statement to `import google.genai as genai`.
- **Files Changed**: `main.py`
- **DO NOT REVERT**: Python 3.9 on Windows requires this exact import style for this specific library version.

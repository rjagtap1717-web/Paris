# Antigravity Agent History Log

This file tracks the overarching features, sessions, and architectural decisions made by Antigravity across days.

## Format
```markdown
### [YYYY-MM-DD] - Session Summary
- **Features Implemented/Modified**: <Brief list>
- **Architectural Decisions & Why**: <Structural changes made>
- **Locked Code/Fragile Zones**: <Components to be careful with next time>
```

---

### [2026-10-01] - Session Summary
- **Features Implemented/Modified**:
  - Replaced `chromadb` with local zero-dependency `vector_brain.py`.
  - Added crash-loop recovery to `run.bat`.
  - Created `system_power` action for Paris self-restart.
  - Implemented multi-tier context tracking (`error_registry`, `agent_history`).
- **Architectural Decisions & Why**:
  - `vector_brain.py` uses simple overlapping keyword overlap instead of heavy tensor math, dodging SQLite version mismatch issues on this machine.
  - Context rules are placed in `.agents/rules/paris_workflow.md` so Antigravity loads them natively without prompting.
- **Locked Code/Fragile Zones**:
  - Do not use `&&` in shell commands; this environment runs PowerShell by default. Use `;`.
  - The dependency chain in window management is fragile: `os_control` passes intents to `computer_control` (PyAutoGUI) and `computer_settings` (system calls). Ensure changes to UI rules are reflected in `critic_agent.py`.

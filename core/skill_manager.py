"""
Skill Manager — Paris's capability grouping layer.

Rather than always sending every action's tool declaration to the LLM (costing
tokens on tools the user may not use for days), actions are grouped into named
"skills".  Only enabled skills have their declarations injected into the Live
session. The action code is still imported at boot (so startup stays fast); it
just doesn't appear in the model's tool schema until you turn the skill on.

SKILL_CATALOG is the single source of truth — no action file needs modifying.
Add a new action here when you create one.  Unknown tool names default to "core"
so they are always visible (safe fall-through).

Skill states are persisted in config/api_keys.json under "skills_enabled".
Always-on skills cannot be disabled; they are never written to that dict.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Skill catalog
# ---------------------------------------------------------------------------
# Each entry:
#   label           - Human-readable name shown in UI
#   description     - One-line summary shown in UI
#   icon            - Emoji for the UI tile
#   always_on       - If True, cannot be disabled
#   default_enabled - First-run default when always_on is False
#   tools           - Set of TOOL["name"] values that belong to this skill

SKILL_CATALOG: dict = {
    "core": {
        "label": "Core",
        "description": "Always-on essentials: search, reminders, memory, news, messaging",
        "icon": "zap",
        "always_on": True,
        "default_enabled": True,
        "tools": {
            "web_search",
            "weather_report",
            "reminder",
            "manage_scratchpad",
            "manage_vector_memory",
            "open_app",
            "read_logs",
            "search_history",
            "send_message",
            "os_control",
            "check_token_balance",
            "get_morning_news",
            "read_audit_report",
            "system_power",
        },
    },
    "browser": {
        "label": "Browser & Video",
        "description": "Web browser automation, YouTube playback and control",
        "icon": "globe",
        "always_on": False,
        "default_enabled": True,
        "tools": {
            "browser_control",
            "youtube_video",
            "rtrvr_control",
        },
    },
    "coding": {
        "label": "Coding & Dev Agents",
        "description": "Code writing, editing, running, and multi-step dev agent tasks",
        "icon": "code",
        "always_on": False,
        "default_enabled": False,
        "tools": {
            "coding_agent",
            "ide_agent",
            "critic_agent",
            "autonomous_planner",
        },
    },
    "office": {
        "label": "Office Suite",
        "description": "Excel, Word, PowerPoint, and advanced file operations",
        "icon": "document",
        "always_on": False,
        "default_enabled": False,
        "tools": {
            "excel_controller",
            "office_suite",
            "file_processor",
            "file_controller",
        },
    },
    "desktop": {
        "label": "Desktop Control",
        "description": "Mouse, keyboard, window management and system settings",
        "icon": "monitor",
        "always_on": False,
        "default_enabled": True,
        "tools": {
            "computer_control",
            "computer_settings",
            "desktop",
        },
    },
    "vision": {
        "label": "Vision & Sensing",
        "description": "Ambient presence detection, gesture control and idle monitor",
        "icon": "eye",
        "always_on": False,
        "default_enabled": False,
        "tools": {
            "ambient_presence",
            "gesture_control",
            "idle_monitor",
        },
    },
    "monitoring": {
        "label": "Background Monitoring",
        "description": "Passive background topic watchers that alert you to changes",
        "icon": "radar",
        "always_on": False,
        "default_enabled": True,
        "tools": {
            "manage_monitor",
        },
    },
}

# ---------------------------------------------------------------------------
# Internal reverse-map: tool_name -> skill_name  (built once at import time)
# ---------------------------------------------------------------------------
_TOOL_TO_SKILL: dict = {}
for _skill_name, _skill_data in SKILL_CATALOG.items():
    for _tool in _skill_data.get("tools", set()):
        _TOOL_TO_SKILL[_tool] = _skill_name


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_skill_for_tool(tool_name: str) -> str:
    """Return which skill owns this tool. Falls back to 'core' (always visible)."""
    return _TOOL_TO_SKILL.get(tool_name, "core")


def is_skill_always_on(skill_name: str) -> bool:
    return bool(SKILL_CATALOG.get(skill_name, {}).get("always_on", False))


def get_skill_default(skill_name: str) -> bool:
    """First-run default for a skill (True unless explicitly set to False)."""
    skill = SKILL_CATALOG.get(skill_name, {})
    if skill.get("always_on"):
        return True
    return bool(skill.get("default_enabled", True))


def get_all_skills() -> dict:
    """Full catalog — used by the UI to render the Skills panel."""
    return SKILL_CATALOG


def list_skills_for_ui(enabled_resolver) -> list:
    """
    Returns one dict per skill, ready for UI rendering.
    enabled_resolver is a callable(skill_name) -> bool (from config_manager).
    """
    out = []
    for name, data in SKILL_CATALOG.items():
        out.append({
            "name":        name,
            "label":       data["label"],
            "description": data["description"],
            "icon":        data.get("icon", "tool"),
            "always_on":   data.get("always_on", False),
            "enabled":     enabled_resolver(name),
            "tool_count":  len(data.get("tools", set())),
            "tools":       sorted(data.get("tools", set())),
        })
    return out


def describe_active_skills(enabled_resolver) -> str:
    """
    Short summary for the system prompt so the model knows which capabilities
    are available without scanning every declaration.
    """
    active, disabled = [], []
    for name, data in SKILL_CATALOG.items():
        label = data["label"]
        if data.get("always_on"):
            active.append(label + " (always on)")
        elif enabled_resolver(name):
            active.append(label)
        else:
            disabled.append(label)

    lines = ["[ACTIVE SKILL PACKS]"]
    if active:
        lines.append("Enabled: " + ", ".join(active))
    if disabled:
        lines.append("Disabled (tools hidden): " + ", ".join(disabled))
    return "\n".join(lines)

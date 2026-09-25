# Paris AI Metadata Reference Map

This file provides a structured overview of the Paris (Paris) codebase to help AI assistants locate functionality without needing full repository searches. Use this index to jump directly to the relevant files.

## Core Application
*   `main.py`: The entry point and main orchestration logic. Manages the event loop, system prompts, microphone/speaker setup, Gemini live session connectivity, tool dispatching, and system/OS context injection (developer-level access details like user home, download paths, OS info).
*   `ui.py`: PyQt6-based user interface. Features the futuristic Iron Man HUD with live CPU/RAM/NET telemetry arcs, floating tactical status stream, targeting reticles, holographic avatar rendering, settings overlays, clipboard UI, plugin panel, and persistent event logging to `logs/paris_debug.log`.
*   `setup.py`: OS-specific installation script for Python dependencies and Playwright browsers. 
*   `run.bat`: Windows batch script to launch the application.

## Core Libraries (`core/`)
Contains fundamental infrastructure for the assistant.
*   `avatar.py` & `avatar_mesh.py`: Controls the holographic face, animations, lip-sync mapping, blinking, and mesh geometry.
*   `confirm.py`: Asynchronous PyQt6 confirmation popup overlay for high-risk actions. Includes `on_resolve` callbacks to feed approval/rejection results directly back into PARIS's active session.
*   `gemini.py` & `llm_client.py`: Interfaces with Gemini APIs, managing connections, text/audio generation, and model selection.
*   `wake_word.py`: Local wake-word detection thread using `openwakeword`.
*   `jev_gate.py`: Safety decision layer evaluating whether tool calls require user confirmation (strictness set to `0.50`). Explicitly exempts safe read/query operations (`list`, `read`, `find`, `largest`, `disk_usage`, `info`) from confirmation popup dialogs.
*   `audio_devices.py`, `tts.py`, `stt.py`: Audio hardware selection, text-to-speech, and speech-to-text handling.
*   `action_loader.py` & `plugin_loader.py`: Discovers and loads tools from the `actions/` and `plugins/` directories.
*   `prompt.txt`: The core protocol and system prompt loaded by the LLM.

## Action Tools (`actions/`)
Modular capabilities that the assistant can invoke.
*   `browser_control.py`: Web automation (Playwright), tab navigation, searching.
*   `computer_control.py` & `computer_settings.py`: Volume, brightness, wifi, power commands, screenshots.
*   `code_helper.py`: Code review, saving scripts, debugging.
*   `desktop.py`: Taskbar/window management, executing custom desktop scripts.
*   `dev_agent.py`: High-level multi-step project generation and coding agent.
*   `file_processor.py` & `file_controller.py`: File system management (read, summarize, move, rename, delete). Enforces Python 3.9 compatibility (`typing.Optional`/`Union`) and bypasses confirmation for read operations.
*   `game_updater.py`: Steam/Epic Games updater and scheduler.
*   `open_app.py`: Application launcher and window management.
*   `proactive.py`: Logic for deciding when to speak unprompted.
*   `reminder.py`: Setting OS-native notifications and reminders.
*   `token_balance.py`: Checks OpenRouter API credit limits and usage.
*   `youtube_video.py`: YouTube search, playback, and transcript summarization.
*   `web_search.py`: Internet search logic (DDG fallback).
*   `background_monitor.py` & `system_monitor.py`: Background telemetry and news watching.

## Configuration, Memory & Logs
*   `config/api_keys.json`: Global configuration storing API keys, assistant name ("PARIS"), voice choice, HUD color theme, and toggle states.
*   `logs/paris_debug.log`: Central debug and event log file capturing UI events, tool calls, confirmation status, and diagnostic output.
*   `memory/`: Contains the SQLite database and `memory_manager.py` for long-term and session memory.

## Plugins (`plugins/`)
*   `_template.py`: A drop-in template for creating new custom skills.

---
**Usage Tip for AI**: Use `view_file` on these specific paths rather than running a global `grep_search` when dealing with known features. Python 3.9 compatibility rules apply (`from typing import Optional, Union`).

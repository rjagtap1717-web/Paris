from actions.code_helper import code_helper as helper_handler
from actions.dev_agent import dev_agent as dev_handler

def coding_agent(parameters: dict, response=None, player=None, session_memory=None) -> str:
    action = parameters.get("action", "").lower().strip()
    
    if action == "scaffold_project":
        # Route to dev_agent for multi-file project creation
        return dev_handler(parameters, response, player, session_memory)
    else:
        # Route everything else (single file edits, running, explaining) to code_helper
        return helper_handler(parameters, response, player, session_memory)

TOOL = {
    "name": "coding_agent",
    "scope": "local",
    "description": "The unified agent for writing, editing, running, or explaining code. Use this for ANY software development task. It can handle single-file tweaks (edit, run) or completely scaffold multi-file projects from scratch.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": "write | edit | explain | run | build | scaffold_project"
            },
            "description": {
                "type": "STRING",
                "description": "What the code should do, what change to make, or the project spec"
            },
            "language": {
                "type": "STRING",
                "description": "Programming language (default: python)"
            },
            "output_path": {
                "type": "STRING",
                "description": "Where to save the file (for write/build)"
            },
            "file_path": {
                "type": "STRING",
                "description": "Path to existing file (for edit/explain/run)"
            },
            "project_name": {
                "type": "STRING",
                "description": "Folder name (ONLY for scaffold_project action)"
            },
            "code": {
                "type": "STRING",
                "description": "Raw code string for explain"
            },
            "args": {
                "type": "STRING",
                "description": "CLI arguments for run/build"
            },
            "timeout": {
                "type": "INTEGER",
                "description": "Execution timeout in seconds (default: 30)"
            }
        },
        "required": ["action", "description"]
    },
    "handler": coding_agent,
}

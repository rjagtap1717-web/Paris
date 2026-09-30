import asyncio
import threading
import sys
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

def ide_agent(parameters: dict, response=None, player=None, session_memory=None, speak=None, **kwargs) -> str:
    prompt = parameters.get("prompt", "")
    if not prompt:
        return "Error: No prompt provided."
        
    if player:
        player.write_log(f"SYS: Dispatching IDE Agent in background...")

    def _background_worker():
        try:
            async def run_agent():
                config = LocalAgentConfig(
                    system_instructions="You are an expert AI software engineer. Follow the user's instructions carefully.",
                    capabilities=CapabilitiesConfig(),
                )
                output_chunks = []
                async with Agent(config) as agent:
                    resp = await agent.chat(prompt)
                    async for token in resp:
                        output_chunks.append(token)
                return "".join(output_chunks)
            
            result = asyncio.run(run_agent())
            if player:
                player.write_log("IDE Task Complete.")
            if speak:
                speak("System: The background IDE task has just finished successfully. Please notify the user about it naturally.")
        except Exception as e:
            if player:
                player.write_log(f"IDE Task Failed: {e}")
            if speak:
                speak(f"System: The background IDE task failed. Please inform the user. Error: {e}")

    threading.Thread(target=_background_worker, daemon=True).start()

    return "Task dispatched to Antigravity IDE in the background. Tell the user you've started the task and will let them know when it's finished."

TOOL = {
    "name": "antigravity_delegate",
    "scope": "exempt",
    "description": "Use this tool to delegate complex coding tasks, scaffolding projects, or multi-file edits to the Antigravity IDE Agent. The agent will run autonomously and has full filesystem and execution capabilities.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "prompt": {
                "type": "STRING",
                "description": "The detailed task instructions for the Antigravity IDE agent."
            }
        },
        "required": ["prompt"]
    }
}

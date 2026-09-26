import threading
from core.planner import Planner

def planner_agent(parameters: dict, player=None, speak=None, action_registry=None, **kwargs) -> str:
    goal = parameters.get("goal", "")
    if not goal:
        return "Error: No goal provided."
        
    if not action_registry:
        return "Error: Action registry not provided to planner."
        
    if player:
        player.write_log(f"SYS: Dispatching Autonomous Planner for goal: {goal}")
        
    def _background_worker():
        try:
            planner = Planner(action_registry=action_registry)
            result = planner.execute_goal(goal)
            if player:
                player.write_log(f"Planner Task Complete.\n{result}")
            if speak:
                speak("System: The background planner task has just finished successfully.")
        except Exception as e:
            if player:
                player.write_log(f"Planner Task Failed: {e}")
            if speak:
                speak(f"System: The background planner task failed. Error: {e}")

    threading.Thread(target=_background_worker, daemon=True).start()

    return f"Dispatched the Planner agent in the background for goal: {goal}. It will run autonomously and report back when finished."

TOOL = {
    "name": "autonomous_planner",
    "scope": "exempt",
    "description": "Use this tool to delegate long-running, multi-step goals to an autonomous background planner. The planner will break the goal into steps and call tools iteratively.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "goal": {
                "type": "STRING",
                "description": "The high-level goal to achieve (e.g. 'Build a React app in /test_app')."
            }
        },
        "required": ["goal"]
    },
    "handler": planner_agent
}

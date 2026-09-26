import json
import time
from core.llm_client import call_llm_text, call_llm
from core.action_loader import ActionRegistry

class Planner:
    def __init__(self, action_registry: ActionRegistry):
        self.action_registry = action_registry
        
    def execute_goal(self, goal: str, context: str = "") -> str:
        """
        Takes a high-level goal, breaks it into steps, and executes them 
        one by one using available tools.
        """
        # Step 1: Create a plan
        plan_prompt = f"""
        You are an expert autonomous planner. The user wants to achieve this goal: {goal}
        Context: {context}
        
        Break this down into 1-5 concrete steps. Return ONLY a JSON list of strings representing the steps.
        Example: ["Search the web for weather in Paris", "Save the result to weather.txt"]
        """
        
        try:
            plan_json = call_llm_text(prompt=plan_prompt, system="Output only valid JSON.")
            # Basic cleanup if model wraps in markdown
            if "```json" in plan_json:
                plan_json = plan_json.split("```json")[1].split("```")[0].strip()
            elif "```" in plan_json:
                plan_json = plan_json.split("```")[1].strip()
                
            steps = json.loads(plan_json)
        except Exception as e:
            return f"Failed to generate a plan: {e}"
            
        if not isinstance(steps, list):
            return "Failed to parse plan as a list."
            
        # Extract available tools
        tools_schema = [t.schema for t in self.action_registry.get_all().values()]
        
        # Step 2: Execute steps
        execution_log = []
        for i, step in enumerate(steps, 1):
            print(f"[Planner] Executing Step {i}/{len(steps)}: {step}")
            execution_log.append(f"\nStep {i}: {step}")
            
            prompt = f"""
            Goal: {goal}
            Current Step: {step}
            Previous execution logs:
            {chr(10).join(execution_log)}
            
            Call the appropriate tool to achieve the Current Step.
            If no tool is needed, respond with a summary of what you did.
            """
            
            try:
                response = call_llm(
                    messages=[{"role": "user", "content": prompt}],
                    tools=tools_schema
                )
                
                content = response.get("content", "")
                tool_calls = response.get("tool_calls", [])
                
                if tool_calls:
                    for tc in tool_calls:
                        name = tc["function"]["name"]
                        args = tc["function"]["arguments"]
                        print(f"[Planner] Calling tool {name}")
                        action = self.action_registry.get(name)
                        if not action:
                            res = f"Tool {name} not found."
                        else:
                            try:
                                res = action.handler(**args)
                            except Exception as e:
                                res = f"Tool failed: {e}"
                                
                        execution_log.append(f"-> Tool {name} returned: {str(res)[:500]}")
                else:
                    execution_log.append(f"-> Agent notes: {content}")
                    
            except Exception as e:
                execution_log.append(f"-> Failed step {i}: {e}")
                
            time.sleep(1) # Rate limiting buffer
            
        return "\n".join(execution_log)

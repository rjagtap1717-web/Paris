import difflib
import logging

logger = logging.getLogger("PARIS.ToolRepair")

def repair_tool_call(name: str, args: dict, registry) -> tuple[str, dict]:
    """
    Attempts to repair a hallucinated or malformed tool call using fuzzy matching
    and schema validation/coercion.
    """
    valid_names = registry.names()
    
    # 1. Repair Tool Name
    if name not in valid_names:
        matches = difflib.get_close_matches(name, valid_names, n=1, cutoff=0.6)
        if matches:
            logger.info(f"Auto-corrected tool name '{name}' to '{matches[0]}'")
            name = matches[0]
            
    # If still not valid, return as is (it will fail cleanly in execution)
    if name not in valid_names:
        return name, args
        
    # 2. Repair Arguments
    rec = registry._actions.get(name)
    if not rec:
        return name, args
        
    schema = rec.parameters
    props = schema.get("properties", {})
    
    repaired_args = dict(args)
    
    for key, val in list(repaired_args.items()):
        # Fuzzy match key
        if key not in props:
            matches = difflib.get_close_matches(key, props.keys(), n=1, cutoff=0.7)
            if matches:
                new_key = matches[0]
                repaired_args[new_key] = val
                del repaired_args[key]
                logger.info(f"Auto-corrected argument '{key}' to '{new_key}' in tool '{name}'")
                key = new_key
            else:
                continue # Key doesn't exist in schema, ignore and let it pass/fail
                
        # Type Coercion
        expected_type = props[key].get("type", "").upper()
        
        if expected_type == "STRING" and not isinstance(val, str):
            repaired_args[key] = str(val)
            logger.info(f"Coerced argument '{key}' to STRING in tool '{name}'")
            
        elif expected_type == "BOOLEAN" and isinstance(val, str):
            repaired_args[key] = val.lower() in ("true", "1", "yes", "y")
            logger.info(f"Coerced argument '{key}' to BOOLEAN in tool '{name}'")
            
        elif expected_type in ("INTEGER", "NUMBER") and isinstance(val, str):
            try:
                if expected_type == "NUMBER":
                    repaired_args[key] = float(val)
                else:
                    repaired_args[key] = int(float(val))
                logger.info(f"Coerced argument '{key}' to {expected_type} in tool '{name}'")
            except ValueError:
                pass
                
    return name, repaired_args

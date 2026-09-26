from dataclasses import dataclass, asdict
from typing import Any, Optional
import json

@dataclass
class ToolResult:
    success: bool
    data: Any
    error: Optional[str] = None
    summary: str = ""
    
    def to_json(self) -> str:
        # Returns the dict as a JSON string so that it seamlessly plugs into current LLM returns
        return json.dumps(asdict(self), default=str)

    def to_dict(self) -> dict:
        return asdict(self)

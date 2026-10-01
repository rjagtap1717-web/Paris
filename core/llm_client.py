import json
import abc
from typing import Generator, Optional
import requests

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def call(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> dict:
        """Returns {'content': str, 'tool_calls': list}"""
        pass

    @abc.abstractmethod
    def stream(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> Generator[dict, None, None]:
        """Yields {'type': 'sentence', 'text': str} and finishes with {'type': 'done', 'content': str, 'tool_calls': list}"""
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.url = url.rstrip("/")
        self.model = model

    def call(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> dict:
        endpoint = f"{self.url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools: payload["tools"] = tools
        resp = requests.post(endpoint, json=payload, timeout=timeout)
        resp.raise_for_status()
        msg = resp.json().get("message", {})
        return {"content": (msg.get("content") or "").strip(), "tool_calls": msg.get("tool_calls") or []}

    def stream(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> Generator[dict, None, None]:
        # Basic mock-up for Ollama stream
        raise NotImplementedError("Streaming not yet ported in this refactor.")

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model

    def call(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> dict:
        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools: payload["tools"] = tools
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=timeout)
        resp.raise_for_status()
        choice = resp.json().get("choices", [{}])[0].get("message", {})
        return {"content": (choice.get("content") or "").strip(), "tool_calls": choice.get("tool_calls") or []}

    def stream(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> Generator[dict, None, None]:
        raise NotImplementedError()

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20240620"):
        self.api_key = api_key
        self.model = model
        
    def call(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> dict:
        # Implementation for Anthropic API
        raise NotImplementedError()
        
    def stream(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> Generator[dict, None, None]:
        raise NotImplementedError()

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        pass

    def call(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> dict:
        # Implementation for Gemini API
        raise NotImplementedError()

    def stream(self, messages: list, tools: Optional[list] = None, timeout: int = 120) -> Generator[dict, None, None]:
        raise NotImplementedError()

def get_default_provider() -> LLMProvider:
    return OllamaProvider()

def call_llm_text(prompt: str, system: str = "") -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    provider = get_default_provider()
    return provider.call(messages)["content"]

def call_llm(messages: list, tools: Optional[list] = None) -> dict:
    provider = get_default_provider()
    return provider.call(messages, tools=tools)

"""
LLM client abstraction with OpenAI and Ollama backends.
Keeps a clean interface for sending chat messages.
"""
from __future__ import annotations

from typing import List, Dict, Literal, Any, cast
import requests

try:
    # OpenAI Python SDK v1.x
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from backend.src.settings import get_settings

Role = Literal["system", "user", "assistant"]

class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._provider = self.settings.model_provider

        if self._provider == "openai" and OpenAI is None:
            raise RuntimeError("OpenAI SDK not installed. Add `openai` to requirements and pip install.")

        if self._provider == "openai" and not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Send a list of messages: [{role: system|user|assistant, content: str}, ...]
        Returns assistant text content.
        """
        if self._provider == "openai":
            return self._openai_chat(messages)
        elif self._provider == "ollama":
            return self._ollama_chat(messages)
        else:
            raise ValueError(f"Unknown model provider: {self._provider}")

    def _openai_chat(self, messages: List[Dict[str, str]]) -> str:
        # Cast to satisfy static analysis; runtime guard ensures OpenAI is available
        OpenAIClient = cast(Any, OpenAI)
        client = OpenAIClient(api_key=self.settings.openai_api_key)
        resp = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

    def _ollama_chat(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.settings.ollama_base_url}/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"]
        if "messages" in data and data["messages"]:
            return data["messages"][-1].get("content", "")
        return ""

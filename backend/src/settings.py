"""
Centralized configuration for the AdultingOS backend.
Reads environment variables and provides sensible defaults.
"""
import os
from dataclasses import dataclass
from typing import Optional

try:
    # Load variables from backend/.env if present
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # Optional dependency; safe to continue without .env
    pass

@dataclass(frozen=True)
class Settings:
    # Model provider: "openai" or "ollama"
    model_provider: str = os.getenv("MODEL_PROVIDER", "openai").lower()

    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # cost-effective, capable

    # Ollama (local inference)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # System prompt for the assistant
    system_prompt: str = os.getenv(
        "ASSISTANT_SYSTEM_PROMPT",
        "You are AdultingOS, a helpful, concise assistant for life admin. "
        "Prefer clear steps, avoid fluff, and call slash-commands when explicit user intent is detected."
    )

def get_settings() -> Settings:
    return Settings()

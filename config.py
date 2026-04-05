# config.py — Temple configuration & environment

import os
from functools import lru_cache


class Settings:
    # OpenAI-compatible API key (OpenAI, OpenRouter, etc.)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Model to use
    model_name: str = os.getenv("THRONE_MODEL_NAME", "gpt-4.1-mini")

    # Optional: base URL override for OpenRouter / local gateways
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None

    # Simple per-IP rate limit (requests per minute)
    max_requests_per_minute: int = int(os.getenv("THRONE_RPM_LIMIT", "60"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()
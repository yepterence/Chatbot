from __future__ import annotations

from .base import LLMProvider


def build_llm_provider(settings) -> LLMProvider:
    """Return the appropriate LLMProvider based on ``settings.llm_backend``.

    Supported backends:
    - ``"local"`` (default): Ollama-based LocalProvider.
    - ``"google"``: Google GenAI (Gemini) GoogleGenAIProvider.

    All provider-specific config (model name, API key, base URL) is read from
    ``settings`` so the switch is purely configuration-driven.
    """
    backend = getattr(settings, "llm_backend", "local").lower()

    if backend == "google":
        from .google_genai import GoogleGenAIProvider

        return GoogleGenAIProvider(
            api_key=getattr(settings, "google_api_key", ""),
            model=getattr(settings, "llm_model", "gemini-2.0-flash"),
        )

    from .local import LocalProvider

    return LocalProvider(
        model=getattr(settings, "llm_model", "gemma3"),
        base_url=getattr(settings, "ollama_base_url", None) or None,
    )

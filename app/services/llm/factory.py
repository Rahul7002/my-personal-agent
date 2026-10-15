from functools import lru_cache
from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.groq_provider import GroqProvider

@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "groq":
        return GroqProvider()
    if provider == "ollama":
        return OllamaProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
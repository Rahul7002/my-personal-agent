from app.services.llm.base import BaseLLMProvider
from app.core.config import settings

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        # Initialized only when selected
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        # Placeholder illustrating how any provider conforms to the same interface
        return f"[Simulated OpenAI ({self.model}) reply to: {prompt}]"
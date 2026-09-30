from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Takes a prompt and returns the generated text."""
        pass

    @abstractmethod
    async def generate_stream(
        self, prompt: str, system_prompt: str | None = None, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        pass
import ollama
from typing import AsyncGenerator
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        # Async client for non-blocking streaming
        self.async_client = ollama.AsyncClient(host=settings.OLLAMA_HOST)
        self.model = settings.OLLAMA_MODEL


    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(model=self.model, messages=messages)
        return response["message"]["content"]
    
    async def generate_stream(
        self, prompt: str, system_prompt: str | None = None, model: str | None = None
    ) -> AsyncGenerator[str, None]:
        chosen_model = model or settings.OLLAMA_MODEL
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Request an async stream from the Ollama engine
        stream_response = await self.async_client.chat(
            model=chosen_model,
            messages=messages,
            stream=True,
        )

        async for chunk in stream_response:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content
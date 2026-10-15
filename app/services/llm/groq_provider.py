from typing import AsyncGenerator

from groq import Groq, AsyncGroq

from app.services.llm.base import BaseLLMProvider
from app.core.config import settings


class GroqProvider(BaseLLMProvider):
    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

        # Async client for non-blocking streaming
        self.async_client = AsyncGroq(
            api_key=settings.GROQ_API_KEY
        )

        self.model = settings.GROQ_MODEL

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> str:

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return response.choices[0].message.content or ""

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        model: str | None = None
    ) -> AsyncGenerator[str, None]:

        chosen_model = model or settings.GROQ_MODEL

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        stream_response = await self.async_client.chat.completions.create(
            model=chosen_model,
            messages=messages,
            stream=True,
        )

        async for chunk in stream_response:
            content = chunk.choices[0].delta.content

            if content:
                yield content
from typing import AsyncGenerator, List, Dict, Any
from openai import AsyncOpenAI

from smartcareerpro.config import config


class GLMClient:
    def __init__(self):
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=config.api_key or "placeholder",
                base_url=config.base_url,
            )
        return self._client

    async def chat(self, messages: List[Dict[str, Any]]) -> str:
        response = await self.client.chat.completions.create(
            model=config.model,
            messages=messages,
            max_tokens=4096,
        )
        return response.choices[0].message.content or ""

    async def stream(self, messages: List[Dict[str, Any]]) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=config.model,
            messages=messages,
            stream=True,
            max_tokens=4096,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


glm_client = GLMClient()

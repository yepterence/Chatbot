from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict = Field(default_factory=dict)  # JSON Schema object


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict = Field(default_factory=dict)


class LLMResponse(BaseModel):
    text: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    thinking: str | None = None


class LLMChunk(BaseModel):
    delta: str
    finished: bool = False


class LLMConfig(BaseModel):
    temperature: float = 0.7
    max_tokens: int | None = None


@runtime_checkable
class LLMProvider(Protocol):
    """Structural protocol for LLM backends.

    Implementations must provide:
    - generate: a coroutine returning a complete LLMResponse.
    - stream: an async generator yielding LLMChunk objects.

    Both local (Ollama) and cloud (Google GenAI) providers implement this protocol,
    allowing the calling code to switch backends via LLM_BACKEND env config only.
    """

    async def generate(
        self,
        messages: list[LLMMessage],
        tools: list[ToolSpec] | None = None,
        config: LLMConfig | None = None,
    ) -> LLMResponse: ...

    def stream(
        self,
        messages: list[LLMMessage],
        tools: list[ToolSpec] | None = None,
        config: LLMConfig | None = None,
    ) -> AsyncIterator[LLMChunk]: ...

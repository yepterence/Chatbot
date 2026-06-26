from __future__ import annotations

from collections.abc import AsyncGenerator

from ollama import AsyncClient
from ollama import chat as ollama_chat_sync

from .base import LLMChunk, LLMConfig, LLMMessage, LLMResponse, ToolCall, ToolSpec


class LocalProvider:
    """LLMProvider backed by a local Ollama server.

    Supports any model served by Ollama (default: gemma3).
    Tool/function calling is forwarded to the Ollama tool API where supported.
    """

    def __init__(self, model: str = "gemma3", base_url: str | None = None) -> None:
        self._model = model
        self._base_url = base_url

    def _client(self) -> AsyncClient:
        if self._base_url:
            return AsyncClient(host=self._base_url)
        return AsyncClient()

    @staticmethod
    def _format_messages(messages: list[LLMMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    @staticmethod
    def _format_tools(tools: list[ToolSpec]) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in tools
        ]

    @staticmethod
    def _parse_tool_calls(raw_tool_calls: list | None) -> list[ToolCall]:
        if not raw_tool_calls:
            return []
        result = []
        for i, tc in enumerate(raw_tool_calls):
            fn = tc.get("function", {}) if isinstance(tc, dict) else getattr(tc, "function", {})
            if hasattr(fn, "name"):
                name = fn.name
                arguments = dict(fn.arguments) if fn.arguments else {}
            else:
                name = fn.get("name", "")
                arguments = fn.get("arguments", {})
            result.append(ToolCall(id=str(i), name=name, arguments=arguments))
        return result

    async def generate(
        self,
        messages: list[LLMMessage],
        tools: list[ToolSpec] | None = None,
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        kwargs: dict = {
            "model": self._model,
            "messages": self._format_messages(messages),
            "stream": False,
        }
        if tools:
            kwargs["tools"] = self._format_tools(tools)
        if config and config.temperature is not None:
            kwargs["options"] = {"temperature": config.temperature}

        response = ollama_chat_sync(**kwargs)
        msg = response["message"] if isinstance(response, dict) else response.message

        raw_content = msg.get("content", "") if isinstance(msg, dict) else (msg.content or "")
        raw_tool_calls = msg.get("tool_calls") if isinstance(msg, dict) else getattr(msg, "tool_calls", None)

        return LLMResponse(
            text=raw_content,
            tool_calls=self._parse_tool_calls(raw_tool_calls),
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        tools: list[ToolSpec] | None = None,
        config: LLMConfig | None = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        """Async generator that yields LLMChunk objects from the Ollama stream."""
        kwargs: dict = {
            "model": self._model,
            "messages": self._format_messages(messages),
            "stream": True,
        }
        if tools:
            kwargs["tools"] = self._format_tools(tools)
        if config and config.temperature is not None:
            kwargs["options"] = {"temperature": config.temperature}

        client = self._client()
        stream_iter = await client.chat(**kwargs)
        async for chunk in stream_iter:
            msg = chunk.get("message", {}) if isinstance(chunk, dict) else chunk.message
            delta = msg.get("content", "") if isinstance(msg, dict) else (msg.content or "")
            finished = chunk.get("done", False) if isinstance(chunk, dict) else getattr(chunk, "done", False)
            yield LLMChunk(delta=delta, finished=finished)

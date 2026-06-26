from __future__ import annotations

from collections.abc import AsyncGenerator

from .base import LLMChunk, LLMConfig, LLMMessage, LLMResponse, ToolCall, ToolSpec

try:
    from google import genai
    from google.genai import types as genai_types

    _GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    _GOOGLE_GENAI_AVAILABLE = False


class GoogleGenAIProvider:
    """LLMProvider backed by the Google GenAI API (Gemini models).

    Requires the ``google-genai`` package and either:
    - ``GOOGLE_API_KEY`` env / ``api_key`` constructor arg (public Gemini API), or
    - Vertex AI credentials configured via ``GOOGLE_CLOUD_PROJECT`` / ADC.

    Tool/function calling uses the google-genai FunctionDeclaration API.
    System messages are promoted to the ``system_instruction`` config field.
    """

    def __init__(self, api_key: str = "", model: str = "gemini-2.0-flash") -> None:
        if not _GOOGLE_GENAI_AVAILABLE:
            raise ImportError(
                "google-genai is not installed. "
                "Run: pip install google-genai>=1.0.0"
            )
        self._model = model
        self._client = genai.Client(api_key=api_key) if api_key else genai.Client()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_system(messages: list[LLMMessage]) -> tuple[str | None, list[LLMMessage]]:
        """Separate the (optional) first system message from the rest."""
        system_instruction: str | None = None
        rest: list[LLMMessage] = []
        for msg in messages:
            if msg.role == "system" and system_instruction is None:
                system_instruction = msg.content
            else:
                rest.append(msg)
        return system_instruction, rest

    @staticmethod
    def _to_contents(messages: list[LLMMessage]) -> list:
        contents = []
        for msg in messages:
            role = "model" if msg.role == "assistant" else msg.role
            contents.append(
                genai_types.Content(
                    role=role,
                    parts=[genai_types.Part(text=msg.content)],
                )
            )
        return contents

    @staticmethod
    def _to_tools(tools: list[ToolSpec]) -> list:
        declarations = [
            genai_types.FunctionDeclaration(
                name=t.name,
                description=t.description,
                parameters=t.parameters or {},
            )
            for t in tools
        ]
        return [genai_types.Tool(function_declarations=declarations)]

    @staticmethod
    def _parse_tool_calls(response) -> list[ToolCall]:
        tool_calls: list[ToolCall] = []
        try:
            parts = response.candidates[0].content.parts
        except (AttributeError, IndexError, TypeError):
            return tool_calls
        for i, part in enumerate(parts):
            fc = getattr(part, "function_call", None)
            if fc:
                tool_calls.append(
                    ToolCall(
                        id=getattr(fc, "id", str(i)),
                        name=fc.name,
                        arguments=dict(fc.args) if fc.args else {},
                    )
                )
        return tool_calls

    def _make_config(
        self,
        system_instruction: str | None,
        tools: list[ToolSpec] | None,
        config: LLMConfig | None,
    ):
        kwargs: dict = {}
        if system_instruction:
            kwargs["system_instruction"] = system_instruction
        if tools:
            kwargs["tools"] = self._to_tools(tools)
        if config:
            if config.temperature is not None:
                kwargs["temperature"] = config.temperature
            if config.max_tokens is not None:
                kwargs["max_output_tokens"] = config.max_tokens
        return genai_types.GenerateContentConfig(**kwargs) if kwargs else None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def generate(
        self,
        messages: list[LLMMessage],
        tools: list[ToolSpec] | None = None,
        config: LLMConfig | None = None,
    ) -> LLMResponse:
        system_instruction, rest = self._split_system(messages)
        contents = self._to_contents(rest)
        gen_config = self._make_config(system_instruction, tools, config)

        kwargs: dict = {"model": self._model, "contents": contents}
        if gen_config:
            kwargs["config"] = gen_config

        response = await self._client.aio.models.generate_content(**kwargs)
        text = response.text or ""
        tool_calls = self._parse_tool_calls(response)
        return LLMResponse(text=text, tool_calls=tool_calls)

    async def stream(
        self,
        messages: list[LLMMessage],
        tools: list[ToolSpec] | None = None,
        config: LLMConfig | None = None,
    ) -> AsyncGenerator[LLMChunk, None]:
        """Async generator that yields LLMChunk objects from the Gemini stream."""
        system_instruction, rest = self._split_system(messages)
        contents = self._to_contents(rest)
        gen_config = self._make_config(system_instruction, tools, config)

        kwargs: dict = {"model": self._model, "contents": contents}
        if gen_config:
            kwargs["config"] = gen_config

        stream_iter = await self._client.aio.models.generate_content_stream(**kwargs)
        async for chunk in stream_iter:
            delta = chunk.text or ""
            yield LLMChunk(delta=delta, finished=False)
        yield LLMChunk(delta="", finished=True)

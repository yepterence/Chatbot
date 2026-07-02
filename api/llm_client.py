#!/usr/bin/python3

from .models import StreamChunk
from .logger import get_logger
from .database import session_context
from .repositories import ChatRepo
from .llm.base import LLMConfig, LLMMessage, LLMProvider

logger = get_logger(__name__)
logger.setLevel("DEBUG")


class Chat:
    """Manages a single in-flight chat exchange.

    Provider-agnostic: receives an LLMProvider at construction time so the
    same class works with both local Ollama and Google GenAI backends.
    """

    def __init__(self, chat_id: str, prompt: list, provider: LLMProvider) -> None:
        self.title: str | None = None
        self.prompt = prompt
        self.chunks_buffer: list[str] = []
        self.llm_response_done = False
        self.cancel_signal = False
        self.chat_id = chat_id
        self.prompt_request_finalized = False
        self.finalized_message = ""
        self._provider = provider

    def aggregate_chunks(self, delta: str) -> None:
        self.chunks_buffer.append(delta)

    def _to_llm_messages(self, messages: list) -> list[LLMMessage]:
        result = []
        for m in messages:
            role = m.role if hasattr(m, "role") else m["role"]
            content = m.content if hasattr(m, "content") else m["content"]
            result.append(LLMMessage(role=role, content=content))
        return result

    async def stream_chat(self):
        """Yield SSE-formatted data lines from the LLM stream.

        Format: ``data: {"content": "...", "finished": false}\\n\\n``
        """
        llm_messages = self._to_llm_messages(self.prompt)
        stream = self._provider.stream(llm_messages, config=LLMConfig())
        logger.info("Chat activated")

        async for chunk in stream:
            if self.cancel_signal:
                logger.info("Chat request canceled. Stopping.")
                return
            logger.debug("Received chunk: %s", chunk.delta)
            self.aggregate_chunks(chunk.delta)
            self.llm_response_done = chunk.finished
            response_data = StreamChunk(content=chunk.delta, finished=chunk.finished)
            logger.debug("Streaming chunk: %s", response_data)
            yield f"data: {response_data.model_dump_json()}\n\n"

        logger.info("LLM Response stream concluded.")

    async def persist_chat(self, title: str) -> None:
        async with session_context() as db:
            repo = ChatRepo(db)
            chat_history = await repo.create_chat_session(title=title)
            history_id = chat_history.id
            last = self.prompt[-1]
            user_prompt_content = last.content if hasattr(last, "content") else last["content"]
            await repo.add_message(
                chat_id=history_id,
                role="user",
                content=user_prompt_content,
                created_at=None,
            )
            await repo.add_message(
                chat_id=history_id,
                role="assistant",
                content=self.finalized_message,
                created_at=None,
            )

    async def generate_title(self) -> str:
        system_msg = LLMMessage(
            role="system",
            content="Generate a short, clear title (max 5 words) summarizing the user's message and return strictly that.",
        )
        title_messages = [system_msg] + self._to_llm_messages(self.prompt)
        response = await self._provider.generate(title_messages, config=LLMConfig(temperature=0.3))
        return response.text.strip()

    async def finalize_streams(self) -> None:
        if self.cancel_signal or self.prompt_request_finalized:
            return
        if not self.llm_response_done:
            logger.error("Failed to conclude LLM response stream")
            return
        self.finalized_message = "".join(self.chunks_buffer)
        self.prompt_request_finalized = True

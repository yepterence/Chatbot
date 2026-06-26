#!/usr/bin/python3

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import uvicorn

from api import logger
from .config import Settings
from .database import get_chat_history, get_session, init_db, get_chat_messages
from .llm.factory import build_llm_provider
from .llm.base import LLMProvider
from .llm_client import Chat
from .models import CancelRequest, ChatRequest

app = FastAPI()

api_logger = logger.get_logger("api_main")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = Settings()
_provider: LLMProvider = build_llm_provider(settings)


class ChatManager:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider
        self.chats: dict[str, Chat] = {}

    def create_chat_instance(self, prompt) -> Chat:
        chat_execution_id = str(uuid4())
        chat_instance = Chat(chat_execution_id, prompt, self._provider)
        self.chats[chat_execution_id] = chat_instance
        return chat_instance

    def get_chat(self, chat_id: str) -> Chat | None:
        return self.chats.get(chat_id)

    def cancel_chat(self, chat_id: str) -> None:
        chat = self.get_chat(chat_id)
        if chat:
            chat.cancel_signal = True

    def remove_chat(self, chat_id: str) -> None:
        self.chats.pop(chat_id, None)

    async def stream_and_cleanup(self, chat: Chat):
        """Stream the LLM response, then generate a title and persist on completion."""
        try:
            async for chunk in chat.stream_chat():
                yield chunk
            if chat.llm_response_done and not chat.cancel_signal:
                await chat.finalize_streams()
                api_logger.info("Finished streaming. Generating title and persisting.")
                title = await chat.generate_title()
                await chat.persist_chat(title)
                api_logger.info("Chat persisted.")
        except Exception as e:
            api_logger.exception("Failed to stream llm response", exc_info=e)
        finally:
            self.remove_chat(chat.chat_id)


chat_manager = ChatManager(_provider)


@app.on_event("startup")
async def startup_event():
    await init_db()
    api_logger.info(
        "Backend started — LLM backend: %s, model: %s",
        settings.llm_backend,
        settings.llm_model,
    )


@app.post("/chat")
async def chat(request: ChatRequest):
    chat_instance = chat_manager.create_chat_instance(request.messages)
    return StreamingResponse(
        chat_manager.stream_and_cleanup(chat_instance),
        media_type="text/event-stream",
        headers={"X-Chat-Id": chat_instance.chat_id},
    )


@app.post("/chat/cancel")
async def cancel_prompt(request: CancelRequest):
    chat_manager.cancel_chat(request.chat_id)
    api_logger.info("Cancelling chat for %s", request.chat_id)
    return {"status": "cancelled"}


@app.get("/chat/get/{chat_id}")
async def get_chat_messages_by_id(chat_id, session: AsyncSession = Depends(get_session)):
    chat = await get_chat_messages(session, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat messages couldnt be found for id")
    return chat.chat_messages


@app.get("/chat/history")
async def get_history(session: AsyncSession = Depends(get_session)):
    chat_history = await get_chat_history(session)
    if not chat_history:
        return []
    return [{"id": obj.id, "chat_title": obj.chat_title} for obj in chat_history]


@app.get("/")
async def root():
    return {"message": "Welcome to my Chatbot"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

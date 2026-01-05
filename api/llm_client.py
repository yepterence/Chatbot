#!/usr/bin/python3

from ollama import AsyncClient, ChatResponse, chat
from .models import StreamChunk
from .logger import get_logger
from .database import AsyncSessionLocal
from .database import create_chat_session, add_message

logger = get_logger(__name__)
logger.setLevel("DEBUG")
MODEL = "gemma3"

class Chat:
    def __init__(self, chat_id, prompt) -> None:
        self.title = None
        self.prompt = prompt
        self.chunks_buffer = []
        self.llm_response_done = False
        self.cancel_signal = False
        self.chat_id = chat_id
        self.prompt_request_finalized = False
        self.finalized_message = ""

    def aggregate_chunks(self, delta):
        self.chunks_buffer.append(delta)


    async def stream_chat(self):
        """
        Streams dicts like {"data": { ... }} for the SSE endpoint to serialize.
        """

        client = AsyncClient()

        stream = await client.chat(
            model=MODEL,
            messages=self.prompt,
            stream=True,
        )
        logger.info("Chat activated")

        
        if not self.llm_response_done:
            async for chunk in stream:
                if self.cancel_signal:
                    logger.info("Chat request canceled. Stopping.")
                    return
                
                delta = chunk['message']['content']
                logger.debug("Received chunk: %s", delta)
                response_data = StreamChunk(
                    content=delta,
                    finished=chunk.get('done', False)
                )
                self.llm_response_done = chunk.get('done', False)
                self.aggregate_chunks(delta)
                logger.debug("Streaming chunk: %s", response_data)
                yield f"data: {response_data.model_dump_json()}\n\n"

        logger.info("LLM Response stream concluded.")

    async def write_msg_to_db(self, title, role, db):
        async with AsyncSessionLocal() as db:
            chat_history = await create_chat_session(title, db)
            await add_message(chat_history.id, role, db)

    async def generate_title(self):
        system_msg = [{"role": "system",
                    "content": "Generate a short, clear title (max 5 words) summarizing the user's message."}]
        title_messages = system_msg + self.prompt
        title = await self.non_stream_response(title_messages)
        return title

    async def non_stream_response(self, messages):
        response: ChatResponse = chat(
            model=MODEL,
            messages=messages,
            stream=False,
        )
        return response["message"]["content"]
    
    def finalize_streams(self):
        if self.cancel_signal or self.prompt_request_finalized:
            return
        
        if not self.llm_response_done:
            logger.error("Failed to conclude LLM response stream")
            return
        
        self.finalized_message = "".join(self.chunks_buffer)
        self.prompt_request_finalized = True

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import Dict, List
import json
from fastapi.middleware.cors import CORSMiddleware
from chatbot import stream_chat

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

async def event_stream(messages):
    async for chunk in stream_chat(messages):
        yield f"data: {json.dumps({'delta': chunk})}\n\n"

@app.get("/")
async def root():
    return {"message": "Welcome to my server"}

@app.post("/chat")
async def chat(payload: Dict):
    """Stream chat response. Expected message body format:
    {
        "messages": [
            {"role":"user", "content": "some messages"}
        ]
    }
    """
    messages: List[Dict] = payload.get("messages", [])
    return StreamingResponse(
        event_stream(messages),
        media_type="text/event-stream"
    )

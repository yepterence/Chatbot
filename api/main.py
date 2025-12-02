#!/usr/bin/python3

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .llm_client import stream_chat
from .models import ChatRequest

app = FastAPI()
origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_chat(request.messages),
        media_type="text/event-stream"
    )

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

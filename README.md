# Chatbot

A privacy-first chat app that runs on local LLMs. Responses stream token by token from a FastAPI backend to a React/TypeScript client, and conversations are saved in Postgres so you can pick any of them back up later. One setting switches the backend from a local Ollama model to Google Gemini, with no other code changes.

I built it to understand, end to end, the parts of an LLM product that don't show up in a demo: streaming, persistence, and keeping the model provider swappable.

<!-- Add a 5–10 second GIF here: type a prompt, watch it stream, switch chats. -->

## What it does

- **Streams responses in real time.** The backend sends tokens over server-sent events (`text/event-stream`), and the client renders them as they arrive.
- **Saves conversations.** Chats and messages are stored in Postgres through SQLAlchemy (async), with Alembic migrations. The sidebar lists past chats, and you can open one and keep talking in it.
- **Titles each new chat.** The model writes a short title from your first message.
- **Swaps providers.** Ollama and Google GenAI both sit behind one provider interface (`api/llm/base.py`), and `LLM_BACKEND` chooses between them.
- **Runs as a desktop app.** An Electron build wraps the same React client.

## How it's built

```
React + TypeScript (Vite, Electron)
        │  fetch + ReadableStream (SSE)
        ▼
FastAPI ── LLM provider interface ──┬── Ollama (local, default: gemma3)
   │                                └── Google GenAI (Gemini)
   ▼
Postgres (SQLAlchemy async, Alembic)
```

Design choices worth calling out:

- **Provider adapter.** Each backend's streaming format is normalized into one chunk shape, so the API and the UI never need to know which model is answering.
- **Async iteration end to end.** Tokens move from the provider through FastAPI's `StreamingResponse` to the browser without buffering the whole reply.
- **Repository layer.** Database access lives in `api/repositories.py`, apart from the route handlers.

## Run it locally

Prerequisites: Python 3.10+, Node.js 22.12+, Postgres, and [Ollama](https://ollama.com) with a model pulled (`ollama pull gemma3`).

1. Create a `.env` file in the project root:

   ```
   DB_USER=...
   DB_PASS=...
   DB_NAME=...
   DB_HOST=localhost
   DB_PORT=5432
   LLM_BACKEND=local        # or "google"
   LLM_MODEL=gemma3
   GOOGLE_API_KEY=          # only needed when LLM_BACKEND=google
   ```

2. Start the API. This applies migrations, then starts the server on port 8000:

   ```bash
   pip install -r requirements.txt
   ./start.sh
   ```

3. Start the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Tests

- Backend: `test/run_tests.sh` creates a throwaway Postgres database and runs pytest. It needs local `sudo -u postgres` access.
- Frontend: `cd frontend && npm test`

## What's next

- Retrieval over past conversations with pgvector (the dependency is already in place)
- Summarizing context so long conversations stay within the model's window
- Choosing the model from the UI instead of the environment
- Docker Compose for a one-command setup

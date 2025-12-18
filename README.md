# Streaming Chat Application

A full-stack, end-to-end streaming chat application that integrates a Python backend (Sanic or FastAPI) with a React frontend to deliver real-time LLM responses using server-sent events (SSE).  
This project demonstrates practical streaming architecture, clean separation of concerns, and modern UI/UX patterns inspired by ChatGPT.

---

## Features

### **Real-Time Streaming**

- The backend streams tokenized responses from the LLM using async iteration.
- The frontend receives continuous updates over **Server-Sent Events (SSE)**.
- Text appears incrementally, replicating ChatGPT’s streaming interface.

### **Conversation Management**

- Chat history is persisted locally (browser storage or backend DB).
- Users can resume previous conversations and view message history.

### **Retry & Cancellation**

- Requests can be retried on failure.
- In-flight responses can be cancelled by the user.

### **Async Prompt Generation**

- Long-running prompt processing can execute asynchronously.
- Users can continue interacting with the UI while a response is being prepared.

### **Model Selection**

- UI dropdown allows users to choose between local models (Ollama) or remote models.
- Backend adapts chunk formats to send a consistent `{ delta, done }` structure.

### **Docker Deployment**

- Fully containerized backend + frontend.
- Production-ready Dockerfile and docker-compose configuration.

---

## Architecture Overview

This project demonstrates several practical patterns used in modern distributed and streaming systems:

### **Backend**

- Adapter pattern to normalize differing LLM provider formats into a unified structure.
- Uses async iterator pattern for real-time token generation
- Pipe and Filter for LLM chunk flow through a streaming pipeline.

### **Frontend**

- Pub/Sub-style streaming - Application subscribes to continual SSE updates.
- MVC-inspired layout

## Local Development

### API

Launch api from project root using

`uvicorn api.main:app --reload`

### Frontend

Launch frontend from frontend/ folder using

`npm run dev`

### Test

Run `test/run_tests.sh` from the project root

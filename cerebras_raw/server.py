#!/usr/bin/env python3
"""
Cerebras Raw API with AG-UI Wrapper

Provides AG-UI streaming interface for Cerebras ultra-fast LLM inference.
Supports multiple models: llama-3.3-70b, llama-3.1-70b, llama-3.1-8b
Uses OpenAI-compatible API from Cerebras.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import json
import time
from typing import AsyncIterator
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Cerebras API configuration
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
if not CEREBRAS_API_KEY:
    raise ValueError("CEREBRAS_API_KEY environment variable is required")

CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"

# Available Cerebras models
CEREBRAS_MODELS = {
    "llama-3.3-70b": "llama-3.3-70b",      # Latest, fastest
    "llama-3.1-70b": "llama-3.1-70b",      # Previous 70B
    "llama-3.1-8b": "llama-3.1-8b",        # Smaller, faster
}

# Default model (can be overridden via env or request)
DEFAULT_MODEL = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")


async def stream_cerebras_to_agui(request_data: dict) -> AsyncIterator[str]:
    """Convert Cerebras streaming to AG-UI events."""

    messages = request_data.get("messages", [])
    thread_id = request_data.get("thread_id", "default-thread")
    run_id = request_data.get("run_id", f"run-{int(time.time())}")

    # Allow model override in request, otherwise use default
    model = request_data.get("model", DEFAULT_MODEL)
    if model not in CEREBRAS_MODELS:
        model = DEFAULT_MODEL

    # Yield RUN_STARTED
    yield f"data: {json.dumps({'type': 'RUN_STARTED', 'threadId': thread_id, 'runId': run_id, 'model': model})}\n\n"

    # Prepare Cerebras API request
    cerebras_request = {
        "model": model,
        "messages": [
            {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            for msg in messages
        ],
        "stream": True,
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    message_id = f"msg-{int(time.time())}"

    # Yield TEXT_MESSAGE_START
    yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_START', 'messageId': message_id, 'role': 'assistant'})}\n\n"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{CEREBRAS_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=cerebras_request,
            ) as response:
                async for line in response.aiter_lines():
                    if not line or line.startswith(":"):
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]

                        if data_str == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                # Yield TEXT_MESSAGE_CONTENT
                                yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_CONTENT', 'messageId': message_id, 'delta': content})}\n\n"

                        except json.JSONDecodeError:
                            continue

    except Exception as e:
        # Yield ERROR
        yield f"data: {json.dumps({'type': 'ERROR', 'error': str(e)})}\n\n"

    # Yield TEXT_MESSAGE_END
    yield f"data: {json.dumps({'type': 'TEXT_MESSAGE_END', 'messageId': message_id})}\n\n"

    # Yield RUN_FINISHED
    yield f"data: {json.dumps({'type': 'RUN_FINISHED', 'threadId': thread_id, 'runId': run_id})}\n\n"


@app.post("/agent")
async def agent_endpoint(request_data: dict):
    """AG-UI compatible endpoint for Cerebras."""
    return StreamingResponse(
        stream_cerebras_to_agui(request_data),
        media_type="text/event-stream",
    )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "provider": "cerebras",
        "default_model": DEFAULT_MODEL,
        "available_models": list(CEREBRAS_MODELS.keys()),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "7778"))
    print(f"🧠 Starting Cerebras Raw AG-UI Agent on port {port}")
    print(f"   Default Model: {DEFAULT_MODEL}")
    print(f"   Available Models: {', '.join(CEREBRAS_MODELS.keys())}")
    print(f"   Endpoint: http://localhost:{port}/agent")
    print(f"   Health: http://localhost:{port}/health")

    uvicorn.run(app, host="0.0.0.0", port=port)

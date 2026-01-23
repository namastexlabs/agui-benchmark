"""
Google ADK Agent with AG-UI Protocol Support
Port: 7782
Endpoint: POST /agent

Google ADK has AG-UI support via the ag-ui-adk package.
This implementation wraps Google ADK with a custom AG-UI adapter.
"""

import os
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# AG-UI Event Types
class EventType:
    RUN_STARTED = "RUN_STARTED"
    RUN_FINISHED = "RUN_FINISHED"
    RUN_ERROR = "RUN_ERROR"
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"
    TOOL_CALL_START = "TOOL_CALL_START"
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"
    TOOL_CALL_END = "TOOL_CALL_END"
    TOOL_CALL_RESULT = "TOOL_CALL_RESULT"


def encode_sse_event(event: dict) -> str:
    """Encode an event as SSE format."""
    return f"data: {json.dumps(event)}\n\n"


# Define tools for the agent
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A math expression like "2 + 2" or "10 * 5"
    """
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"{expression} = {result}"
        return "Invalid expression - only basic math allowed"
    except Exception as e:
        return f"Error: {str(e)}"


# Create the Google ADK agent
agent = LlmAgent(
    name="google_adk_assistant",
    model="gemini-3-flash",
    instruction="""You are a helpful assistant running on the Google ADK framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses.""",
    tools=[get_current_time, calculator],
)

# Create session service
session_service = InMemorySessionService()


async def run_agent_with_agui(
    thread_id: str,
    run_id: str,
    user_message: str
) -> AsyncGenerator[str, None]:
    """Run the Google ADK agent and emit AG-UI protocol events."""

    # Emit RUN_STARTED
    yield encode_sse_event({
        "type": EventType.RUN_STARTED,
        "threadId": thread_id,
        "runId": run_id,
    })

    message_id = str(uuid.uuid4())

    try:
        # Create or get session first (required by Google ADK)
        session = await session_service.create_session(
            app_name="google_adk_benchmark",
            user_id="benchmark-user",
        )

        # Create runner for this request
        runner = Runner(
            agent=agent,
            app_name="google_adk_benchmark",
            session_service=session_service,
        )

        # Create content message
        content = types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        )

        # Emit TEXT_MESSAGE_START
        yield encode_sse_event({
            "type": EventType.TEXT_MESSAGE_START,
            "messageId": message_id,
            "role": "assistant",
        })

        # Run the agent and collect response
        response_text = ""
        async for event in runner.run_async(
            user_id="benchmark-user",
            session_id=session.id,
            new_message=content,
        ):
            # Extract text from event.content.parts
            text_delta = ""
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_delta = part.text.strip()
                            break

            if text_delta and text_delta not in response_text:
                response_text += text_delta
                yield encode_sse_event({
                    "type": EventType.TEXT_MESSAGE_CONTENT,
                    "messageId": message_id,
                    "delta": text_delta,
                })

        # Emit TEXT_MESSAGE_END
        yield encode_sse_event({
            "type": EventType.TEXT_MESSAGE_END,
            "messageId": message_id,
        })

        # Emit RUN_FINISHED
        yield encode_sse_event({
            "type": EventType.RUN_FINISHED,
            "threadId": thread_id,
            "runId": run_id,
        })

    except Exception as e:
        # Emit RUN_ERROR
        yield encode_sse_event({
            "type": EventType.RUN_ERROR,
            "threadId": thread_id,
            "runId": run_id,
            "error": str(e),
        })


# Create FastAPI app
app = FastAPI(
    title="Google ADK AG-UI Test Agent",
    description="Google ADK agent with AG-UI protocol support"
)


@app.post("/agent")
async def run_agent_endpoint(request: Request):
    """AG-UI compatible endpoint."""
    body = await request.json()

    thread_id = body.get("thread_id", str(uuid.uuid4()))
    run_id = body.get("run_id", str(uuid.uuid4()))
    messages = body.get("messages", [])

    # Get the last user message
    user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_message = msg.get("content", "")
            break

    if not user_message:
        user_message = "Hello"

    return StreamingResponse(
        run_agent_with_agui(thread_id, run_id, user_message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "google-adk",
        "port": 7782,
        "agui_endpoint": "/agent",
        "native_agui": True,
    }


@app.get("/")
async def root():
    return {
        "name": "Google ADK AG-UI Test Agent",
        "framework": "google-adk",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health",
        "native_agui": True,
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Google ADK Agent on port 7782...")
    print("AG-UI Endpoint: POST http://localhost:7782/agent")
    print("Using Google ADK with AG-UI support")
    uvicorn.run(app, host="0.0.0.0", port=7782)

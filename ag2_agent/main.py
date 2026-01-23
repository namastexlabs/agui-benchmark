"""
AG2 (AutoGen) Agent with AG-UI Protocol Support
Port: 7781
Endpoint: POST /agent

AG2 requires a custom AG-UI adapter to translate between AG2 events and AG-UI protocol.
This implementation wraps an AG2 AssistantAgent with async support.
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

from autogen import AssistantAgent


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


# Define tools
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


# LLM config for AG2
llm_config = {
    "model": "gpt-5.2-mini",
    "api_key": os.getenv("OPENAI_API_KEY"),
}

# Create the AG2 agent
agent = AssistantAgent(
    name="ag2-assistant",
    system_message="""You are a helpful assistant running on the AG2 (AutoGen) framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses.""",
    llm_config=llm_config,
)

# Register tools
agent.register_function(
    function_map={
        "get_current_time": get_current_time,
        "calculator": calculator,
    }
)


async def run_agent_with_agui(
    thread_id: str,
    run_id: str,
    user_message: str
) -> AsyncGenerator[str, None]:
    """Run the AG2 agent and emit AG-UI protocol events."""

    # Emit RUN_STARTED
    yield encode_sse_event({
        "type": EventType.RUN_STARTED,
        "threadId": thread_id,
        "runId": run_id,
    })

    message_id = str(uuid.uuid4())

    try:
        # Generate reply using async method
        response = await agent.a_generate_reply(
            messages=[{"role": "user", "content": user_message}],
        )

        # Get the response content
        response_text = ""
        if isinstance(response, str):
            response_text = response
        elif isinstance(response, dict):
            response_text = response.get("content", str(response))
        else:
            response_text = str(response) if response else ""

        # Emit TEXT_MESSAGE_START
        yield encode_sse_event({
            "type": EventType.TEXT_MESSAGE_START,
            "messageId": message_id,
            "role": "assistant",
        })

        # Emit content
        if response_text:
            yield encode_sse_event({
                "type": EventType.TEXT_MESSAGE_CONTENT,
                "messageId": message_id,
                "delta": response_text,
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
    title="AG2 AG-UI Test Agent",
    description="AG2 (AutoGen) agent with AG-UI protocol support"
)


@app.post("/agent")
async def run_agent(request: Request):
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
        "framework": "ag2",
        "port": 7781,
        "agui_endpoint": "/agent",
        "native_agui": False,  # Using custom adapter
    }


@app.get("/")
async def root():
    return {
        "name": "AG2 AG-UI Test Agent",
        "framework": "ag2 (autogen)",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health",
        "native_agui": False,
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting AG2 Agent on port 7781...")
    print("AG-UI Endpoint: POST http://localhost:7781/agent")
    print("Using custom AG-UI adapter for AG2")
    uvicorn.run(app, host="0.0.0.0", port=7781)

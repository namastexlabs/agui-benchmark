"""
Raw Anthropic Claude Agent with AG-UI Protocol Support
Port: 7776
Endpoint: POST /agent

Direct Anthropic API wrapped with AG-UI events - no framework needed.
"""

import os
import uuid
import json
from datetime import datetime
from typing import Optional, List, AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anthropic


# AG-UI Request models
class Message(BaseModel):
    id: Optional[str] = None
    role: str
    content: str


class RunAgentInput(BaseModel):
    thread_id: str
    run_id: str
    messages: List[Message]
    state: Optional[dict] = None
    tools: Optional[list] = None
    context: Optional[list] = None
    forwardedProps: Optional[dict] = None


def encode_sse(event_type: str, data: dict) -> str:
    """Encode an event as SSE format."""
    payload = {"type": event_type, **data}
    return f"data: {json.dumps(payload)}\n\n"


# Initialize Anthropic client
client = anthropic.Anthropic()

# Define tools for Claude
tools = [
    {
        "name": "get_current_time",
        "description": "Get the current date and time",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "calculator",
        "description": "Evaluate a mathematical expression",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression like '2 + 2' or '10 * 5'"
                }
            },
            "required": ["expression"]
        }
    }
]


def execute_tool(name: str, args: dict) -> str:
    """Execute a tool and return the result."""
    if name == "get_current_time":
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif name == "calculator":
        expression = args.get("expression", "")
        try:
            allowed_chars = set("0123456789+-*/.() ")
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"{expression} = {result}"
            return "Invalid expression"
        except Exception as e:
            return f"Error: {str(e)}"
    return "Unknown tool"


app = FastAPI(
    title="Anthropic Raw AG-UI Agent",
    description="Direct Anthropic Claude API with AG-UI protocol wrapper"
)


@app.post("/agent")
async def agent_endpoint(input_data: RunAgentInput):
    """AG-UI compatible endpoint using raw Anthropic API."""

    async def event_generator() -> AsyncGenerator[str, None]:
        # === RUN_STARTED ===
        yield encode_sse("RUN_STARTED", {
            "thread_id": input_data.thread_id,
            "run_id": input_data.run_id
        })

        # Build messages for Claude
        messages = []
        for msg in input_data.messages:
            messages.append({"role": msg.role, "content": msg.content})

        try:
            msg_id = str(uuid.uuid4())
            message_started = False

            # Call Claude with streaming
            with client.messages.stream(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system="""You are a helpful assistant using raw Anthropic Claude API wrapped with AG-UI protocol.
                You can tell the current time and do basic math calculations.
                Be concise and friendly.""",
                messages=messages,
                tools=tools
            ) as stream:
                current_tool_id = None
                current_tool_name = None
                tool_input_buffer = ""

                for event in stream:
                    # Handle content block start
                    if event.type == "content_block_start":
                        if event.content_block.type == "tool_use":
                            current_tool_id = event.content_block.id
                            current_tool_name = event.content_block.name
                            tool_input_buffer = ""
                            yield encode_sse("TOOL_CALL_START", {
                                "toolCallId": current_tool_id,
                                "toolCallName": current_tool_name
                            })
                        elif event.content_block.type == "text":
                            if not message_started:
                                yield encode_sse("TEXT_MESSAGE_START", {
                                    "message_id": msg_id,
                                    "role": "assistant"
                                })
                                message_started = True

                    # Handle content block delta
                    elif event.type == "content_block_delta":
                        if event.delta.type == "text_delta":
                            yield encode_sse("TEXT_MESSAGE_CONTENT", {
                                "message_id": msg_id,
                                "delta": event.delta.text
                            })
                        elif event.delta.type == "input_json_delta":
                            tool_input_buffer += event.delta.partial_json
                            yield encode_sse("TOOL_CALL_ARGS", {
                                "toolCallId": current_tool_id,
                                "delta": event.delta.partial_json
                            })

                    # Handle content block stop
                    elif event.type == "content_block_stop":
                        if current_tool_id:
                            yield encode_sse("TOOL_CALL_END", {
                                "toolCallId": current_tool_id
                            })

                            # Execute tool
                            try:
                                args = json.loads(tool_input_buffer) if tool_input_buffer else {}
                            except:
                                args = {}

                            result = execute_tool(current_tool_name, args)
                            yield encode_sse("TOOL_CALL_RESULT", {
                                "toolCallId": current_tool_id,
                                "result": result
                            })

                            current_tool_id = None
                            current_tool_name = None
                            tool_input_buffer = ""

                # Get the final message to check if we need follow-up
                final_message = stream.get_final_message()

                # If there were tool uses, make a follow-up call
                if final_message.stop_reason == "tool_use":
                    tool_results = []
                    for block in final_message.content:
                        if block.type == "tool_use":
                            result = execute_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            })

                    # Follow-up call
                    messages.append({"role": "assistant", "content": final_message.content})
                    messages.append({"role": "user", "content": tool_results})

                    with client.messages.stream(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1024,
                        messages=messages
                    ) as follow_stream:
                        for event in follow_stream:
                            if event.type == "content_block_start" and event.content_block.type == "text":
                                if not message_started:
                                    yield encode_sse("TEXT_MESSAGE_START", {
                                        "message_id": msg_id,
                                        "role": "assistant"
                                    })
                                    message_started = True
                            elif event.type == "content_block_delta" and event.delta.type == "text_delta":
                                yield encode_sse("TEXT_MESSAGE_CONTENT", {
                                    "message_id": msg_id,
                                    "delta": event.delta.text
                                })

            # End message
            if message_started:
                yield encode_sse("TEXT_MESSAGE_END", {"message_id": msg_id})

        except Exception as e:
            yield encode_sse("RUN_ERROR", {
                "message": str(e),
                "code": "ANTHROPIC_ERROR"
            })

        # === RUN_FINISHED ===
        yield encode_sse("RUN_FINISHED", {
            "thread_id": input_data.thread_id,
            "run_id": input_data.run_id
        })

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "anthropic-raw",
        "model": "claude-haiku-4-5-20251001",
        "port": 7776,
        "agui_endpoint": "/agent",
        "native_agui": False,
        "note": "Direct Anthropic Claude API with AG-UI wrapper"
    }


@app.get("/")
async def root():
    return {
        "name": "Anthropic Raw AG-UI Agent",
        "framework": "anthropic-raw",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Anthropic Raw Agent on port 7776...")
    print("AG-UI Endpoint: POST http://localhost:7776/agent")
    uvicorn.run(app, host="0.0.0.0", port=7776)

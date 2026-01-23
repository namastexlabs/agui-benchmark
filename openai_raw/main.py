"""
Raw OpenAI Agent with AG-UI Protocol Support
Port: 7775
Endpoint: POST /agent

Direct OpenAI API wrapped with AG-UI events - no framework needed.
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
from openai import OpenAI


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


# Initialize OpenAI client
client = OpenAI()

# Define tools for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression",
            "parameters": {
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
    title="OpenAI Raw AG-UI Agent",
    description="Direct OpenAI API with AG-UI protocol wrapper"
)


@app.post("/agent")
async def agent_endpoint(input_data: RunAgentInput):
    """AG-UI compatible endpoint using raw OpenAI API."""

    async def event_generator() -> AsyncGenerator[str, None]:
        # === RUN_STARTED ===
        yield encode_sse("RUN_STARTED", {
            "thread_id": input_data.thread_id,
            "run_id": input_data.run_id
        })

        # Build messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant using raw OpenAI API wrapped with AG-UI protocol.
                You can tell the current time and do basic math calculations.
                Be concise and friendly."""
            }
        ]

        for msg in input_data.messages:
            messages.append({"role": msg.role, "content": msg.content})

        try:
            # Call OpenAI with streaming
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=messages,
                tools=tools,
                stream=True
            )

            msg_id = str(uuid.uuid4())
            message_started = False
            tool_calls_buffer = {}  # Buffer for tool calls

            for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None

                if delta:
                    # Handle tool calls
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            tc_id = tc.id or list(tool_calls_buffer.keys())[-1] if tool_calls_buffer else str(uuid.uuid4())

                            if tc.id:  # New tool call
                                tool_calls_buffer[tc_id] = {
                                    "name": tc.function.name if tc.function else "",
                                    "args": ""
                                }
                                yield encode_sse("TOOL_CALL_START", {
                                    "toolCallId": tc_id,
                                    "toolCallName": tc.function.name if tc.function else ""
                                })

                            if tc.function and tc.function.arguments:
                                tool_calls_buffer[tc_id]["args"] += tc.function.arguments
                                yield encode_sse("TOOL_CALL_ARGS", {
                                    "toolCallId": tc_id,
                                    "delta": tc.function.arguments
                                })

                    # Handle content
                    if delta.content:
                        if not message_started:
                            yield encode_sse("TEXT_MESSAGE_START", {
                                "message_id": msg_id,
                                "role": "assistant"
                            })
                            message_started = True

                        yield encode_sse("TEXT_MESSAGE_CONTENT", {
                            "message_id": msg_id,
                            "delta": delta.content
                        })

            # End tool calls and execute them
            for tc_id, tc_data in tool_calls_buffer.items():
                yield encode_sse("TOOL_CALL_END", {"toolCallId": tc_id})

                # Execute tool
                try:
                    args = json.loads(tc_data["args"]) if tc_data["args"] else {}
                except:
                    args = {}

                result = execute_tool(tc_data["name"], args)
                yield encode_sse("TOOL_CALL_RESULT", {
                    "toolCallId": tc_id,
                    "result": result
                })

            # If we had tool calls, make a follow-up call
            if tool_calls_buffer and not message_started:
                # Add tool results to messages
                tool_results = []
                for tc_id, tc_data in tool_calls_buffer.items():
                    try:
                        args = json.loads(tc_data["args"]) if tc_data["args"] else {}
                    except:
                        args = {}
                    result = execute_tool(tc_data["name"], args)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": result
                    })

                # Follow-up call
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tc_id,
                            "type": "function",
                            "function": {"name": tc_data["name"], "arguments": tc_data["args"]}
                        }
                        for tc_id, tc_data in tool_calls_buffer.items()
                    ]
                })
                messages.extend(tool_results)

                follow_up = client.chat.completions.create(
                    model="gpt-5.2",
                    messages=messages,
                    stream=True
                )

                for chunk in follow_up:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        if not message_started:
                            yield encode_sse("TEXT_MESSAGE_START", {
                                "message_id": msg_id,
                                "role": "assistant"
                            })
                            message_started = True
                        yield encode_sse("TEXT_MESSAGE_CONTENT", {
                            "message_id": msg_id,
                            "delta": delta.content
                        })

            # End message
            if message_started:
                yield encode_sse("TEXT_MESSAGE_END", {"message_id": msg_id})

        except Exception as e:
            yield encode_sse("RUN_ERROR", {
                "message": str(e),
                "code": "OPENAI_ERROR"
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
        "framework": "openai-raw",
        "model": "gpt-5.2",
        "port": 7775,
        "agui_endpoint": "/agent",
        "native_agui": False,
        "note": "Direct OpenAI API with AG-UI wrapper"
    }


@app.get("/")
async def root():
    return {
        "name": "OpenAI Raw AG-UI Agent",
        "framework": "openai-raw",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting OpenAI Raw Agent on port 7775...")
    print("AG-UI Endpoint: POST http://localhost:7775/agent")
    uvicorn.run(app, host="0.0.0.0", port=7775)

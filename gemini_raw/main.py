"""
Raw Google Gemini Agent with AG-UI Protocol Support
Port: 7777
Endpoint: POST /agent

Direct Google Gemini API wrapped with AG-UI events - no framework needed.
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
import google.generativeai as genai


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


# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Define tools for Gemini
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"{expression} = {result}"
        return "Invalid expression"
    except Exception as e:
        return f"Error: {str(e)}"


# Create model with tools
model = genai.GenerativeModel(
    model_name="gemini-3-flash",
    tools=[get_current_time, calculator],
    system_instruction="""You are a helpful assistant using raw Google Gemini API wrapped with AG-UI protocol.
    You can tell the current time and do basic math calculations.
    Be concise and friendly."""
)


app = FastAPI(
    title="Gemini Raw AG-UI Agent",
    description="Direct Google Gemini API with AG-UI protocol wrapper"
)


@app.post("/agent")
async def agent_endpoint(input_data: RunAgentInput):
    """AG-UI compatible endpoint using raw Gemini API."""

    async def event_generator() -> AsyncGenerator[str, None]:
        # === RUN_STARTED ===
        yield encode_sse("RUN_STARTED", {
            "thread_id": input_data.thread_id,
            "run_id": input_data.run_id
        })

        # Build history for Gemini
        history = []
        user_message = ""

        for msg in input_data.messages:
            role = "user" if msg.role == "user" else "model"
            if msg.role == "user":
                user_message = msg.content
            else:
                history.append({"role": role, "parts": [msg.content]})

        try:
            msg_id = str(uuid.uuid4())
            message_started = False

            # Create chat and send message with streaming
            chat = model.start_chat(history=history)
            response = chat.send_message(user_message, stream=True)

            accumulated_text = ""
            function_calls = []

            for chunk in response:
                # Check for function calls
                if chunk.candidates and chunk.candidates[0].content.parts:
                    for part in chunk.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            tool_call_id = str(uuid.uuid4())

                            yield encode_sse("TOOL_CALL_START", {
                                "toolCallId": tool_call_id,
                                "toolCallName": fc.name
                            })

                            # Convert args to JSON
                            args_dict = dict(fc.args) if fc.args else {}
                            args_json = json.dumps(args_dict)

                            yield encode_sse("TOOL_CALL_ARGS", {
                                "toolCallId": tool_call_id,
                                "delta": args_json
                            })

                            yield encode_sse("TOOL_CALL_END", {
                                "toolCallId": tool_call_id
                            })

                            # Execute the function
                            if fc.name == "get_current_time":
                                result = get_current_time()
                            elif fc.name == "calculator":
                                result = calculator(args_dict.get("expression", ""))
                            else:
                                result = "Unknown function"

                            yield encode_sse("TOOL_CALL_RESULT", {
                                "toolCallId": tool_call_id,
                                "result": result
                            })

                            function_calls.append({
                                "name": fc.name,
                                "args": args_dict,
                                "result": result
                            })

                        elif hasattr(part, 'text') and part.text:
                            if not message_started:
                                yield encode_sse("TEXT_MESSAGE_START", {
                                    "message_id": msg_id,
                                    "role": "assistant"
                                })
                                message_started = True

                            # Stream new text
                            new_text = part.text[len(accumulated_text):] if part.text.startswith(accumulated_text) else part.text
                            if new_text:
                                yield encode_sse("TEXT_MESSAGE_CONTENT", {
                                    "message_id": msg_id,
                                    "delta": new_text
                                })
                                accumulated_text = part.text

            # If we had function calls, send tool results back
            if function_calls and not message_started:
                # Build function response parts
                function_responses = []
                for fc in function_calls:
                    function_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fc["name"],
                                response={"result": fc["result"]}
                            )
                        )
                    )

                # Send function results back to get final response
                follow_up = chat.send_message(function_responses, stream=True)

                for chunk in follow_up:
                    if chunk.text:
                        if not message_started:
                            yield encode_sse("TEXT_MESSAGE_START", {
                                "message_id": msg_id,
                                "role": "assistant"
                            })
                            message_started = True

                        new_text = chunk.text[len(accumulated_text):] if chunk.text.startswith(accumulated_text) else chunk.text
                        if new_text:
                            yield encode_sse("TEXT_MESSAGE_CONTENT", {
                                "message_id": msg_id,
                                "delta": new_text
                            })
                            accumulated_text = chunk.text

            # End message
            if message_started:
                yield encode_sse("TEXT_MESSAGE_END", {"message_id": msg_id})

        except Exception as e:
            yield encode_sse("RUN_ERROR", {
                "message": str(e),
                "code": "GEMINI_ERROR"
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
        "framework": "gemini-raw",
        "model": "gemini-3-flash",
        "port": 7777,
        "agui_endpoint": "/agent",
        "native_agui": False,
        "note": "Direct Google Gemini API with AG-UI wrapper"
    }


@app.get("/")
async def root():
    return {
        "name": "Gemini Raw AG-UI Agent",
        "framework": "gemini-raw",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Gemini Raw Agent on port 7777...")
    print("AG-UI Endpoint: POST http://localhost:7777/agent")
    uvicorn.run(app, host="0.0.0.0", port=7777)

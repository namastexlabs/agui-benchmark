"""
PydanticAI Agent with AG-UI Protocol Support
Port: 7774
Endpoint: POST /

PydanticAI has native AG-UI support via AGUIAdapter.
"""

import os
from datetime import datetime
from http import HTTPStatus
import json
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from pydantic import ValidationError
from pydantic_ai import Agent
from pydantic_ai.tools import Tool
from pydantic_ai.ui import SSE_CONTENT_TYPE
from pydantic_ai.ui.ag_ui import AGUIAdapter


# Define tools as functions
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


# Create PydanticAI agent
agent = Agent(
    'anthropic:claude-haiku-4-5-20251001',
    tools=[
        Tool(get_current_time, takes_ctx=False),
        Tool(calculator, takes_ctx=False),
    ],
    instructions="""You are a helpful assistant running on the PydanticAI framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses."""
)


app = FastAPI(
    title="PydanticAI AG-UI Test Agent",
    description="PydanticAI agent with AG-UI protocol support"
)


@app.post("/")
async def run_agent(request: Request) -> Response:
    """AG-UI compatible endpoint using PydanticAI's native adapter."""
    accept = request.headers.get('accept', SSE_CONTENT_TYPE)

    try:
        # Build run input from AG-UI request
        run_input = AGUIAdapter.build_run_input(await request.body())
    except ValidationError as e:
        return Response(
            content=json.dumps({"error": e.errors()}),
            media_type='application/json',
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        )

    # Create adapter and run
    adapter = AGUIAdapter(agent=agent, run_input=run_input, accept=accept)
    event_stream = adapter.run_stream()
    sse_event_stream = adapter.encode_stream(event_stream)

    return StreamingResponse(
        sse_event_stream,
        media_type=accept,
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "pydantic-ai",
        "port": 7774,
        "agui_endpoint": "/"
    }


@app.get("/info")
async def info():
    return {
        "name": "PydanticAI AG-UI Test Agent",
        "framework": "pydantic-ai",
        "agui_endpoint": "POST /",
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting PydanticAI Agent on port 7774...")
    print("AG-UI Endpoint: POST http://localhost:7774/")
    uvicorn.run(app, host="0.0.0.0", port=7774)

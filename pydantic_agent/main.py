"""
PydanticAI Agent with AG-UI Protocol Support
Port: 7774
Endpoints:
  - POST /anthropic - Claude (Anthropic)
  - POST /openai - GPT (OpenAI)
  - POST /gemini - Gemini (Google)

PydanticAI has native AG-UI support via AGUIAdapter.
"""

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


# Shared tools and instructions for all agents
TOOLS = [
    Tool(get_current_time, takes_ctx=False),
    Tool(calculator, takes_ctx=False),
]

INSTRUCTIONS = """You are a helpful assistant running on the PydanticAI framework.
You can tell the current time and do basic math calculations.
Be concise and friendly in your responses."""


# Create agents for different providers
anthropic_agent = Agent(
    'anthropic:claude-haiku-4-5-20251001',
    tools=TOOLS,
    instructions=INSTRUCTIONS,
)

openai_agent = Agent(
    'openai:gpt-5-mini',
    tools=TOOLS,
    instructions=INSTRUCTIONS,
)

gemini_agent = Agent(
    'google-gla:gemini-2.5-flash',
    tools=TOOLS,
    instructions=INSTRUCTIONS,
)


app = FastAPI(
    title="PydanticAI AG-UI Test Agent",
    description="PydanticAI agent with AG-UI protocol support for multiple providers"
)


async def run_agent_with_model(request: Request, agent: Agent) -> Response:
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


@app.post("/anthropic")
async def run_anthropic_agent(request: Request) -> Response:
    """AG-UI endpoint using Anthropic Claude."""
    return await run_agent_with_model(request, anthropic_agent)


@app.post("/openai")
async def run_openai_agent(request: Request) -> Response:
    """AG-UI endpoint using OpenAI GPT."""
    return await run_agent_with_model(request, openai_agent)


@app.post("/gemini")
async def run_gemini_agent(request: Request) -> Response:
    """AG-UI endpoint using Google Gemini."""
    return await run_agent_with_model(request, gemini_agent)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "pydantic-ai",
        "port": 7774,
        "providers": {
            "anthropic": {
                "endpoint": "/anthropic",
                "model": "claude-haiku-4-5-20251001"
            },
            "openai": {
                "endpoint": "/openai",
                "model": "gpt-5-mini"
            },
            "gemini": {
                "endpoint": "/gemini",
                "model": "gemini-2.5-flash"
            }
        }
    }


@app.get("/info")
async def info():
    return {
        "name": "PydanticAI AG-UI Test Agent",
        "framework": "pydantic-ai",
        "agui_endpoints": [
            "POST /anthropic",
            "POST /openai",
            "POST /gemini"
        ],
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting PydanticAI Agent on port 7774...")
    print("AG-UI Endpoints:")
    print("  - POST http://localhost:7774/anthropic (Claude)")
    print("  - POST http://localhost:7774/openai (GPT)")
    print("  - POST http://localhost:7774/gemini (Gemini)")
    uvicorn.run(app, host="0.0.0.0", port=7774)

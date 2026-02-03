"""
LlamaIndex Agent with AG-UI Protocol Support
Port: 7780
Endpoints:
  - POST /agent/openai/run (OpenAI GPT-4o-mini)
  - POST /agent/anthropic/run (Claude Haiku)
  - POST /agent/gemini/run (Gemini 2.0 Flash)

LlamaIndex has native AG-UI support via llama-index-protocols-ag-ui package.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from llama_index.protocols.ag_ui.router import get_ag_ui_workflow_router
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.gemini import Gemini


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


# Common configuration
BACKEND_TOOLS = [get_current_time, calculator]
SYSTEM_PROMPT = """You are a helpful assistant running on the LlamaIndex framework.
You can tell the current time and do basic math calculations.
Be concise and friendly in your responses."""

# Create AG-UI routers for each LLM provider
openai_router = get_ag_ui_workflow_router(
    llm=OpenAI(model="gpt-5-mini"),
    frontend_tools=[],
    backend_tools=BACKEND_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    initial_state=None,
)

anthropic_router = get_ag_ui_workflow_router(
    llm=Anthropic(model="claude-haiku-4-5-20251001"),
    frontend_tools=[],
    backend_tools=BACKEND_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    initial_state=None,
)

gemini_router = get_ag_ui_workflow_router(
    llm=Gemini(model="gemini-2.5-flash"),
    frontend_tools=[],
    backend_tools=BACKEND_TOOLS,
    system_prompt=SYSTEM_PROMPT,
    initial_state=None,
)

# Create FastAPI app
app = FastAPI(
    title="LlamaIndex AG-UI Test Agent",
    description="LlamaIndex agent with native AG-UI protocol support for multiple LLM providers"
)

# Include the AG-UI routers for each provider
app.include_router(openai_router, prefix="/agent/openai")
app.include_router(anthropic_router, prefix="/agent/anthropic")
app.include_router(gemini_router, prefix="/agent/gemini")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "llamaindex",
        "port": 7780,
        "providers": {
            "openai": {
                "model": "gpt-5-mini",
                "endpoint": "/agent/openai/run"
            },
            "anthropic": {
                "model": "claude-haiku-4-5-20251001",
                "endpoint": "/agent/anthropic/run"
            },
            "gemini": {
                "model": "gemini-2.5-flash",
                "endpoint": "/agent/gemini/run"
            }
        },
        "native_agui": True
    }


@app.get("/")
async def root():
    return {
        "name": "LlamaIndex AG-UI Test Agent",
        "framework": "llamaindex",
        "agui_endpoints": {
            "openai": "POST /agent/openai/run",
            "anthropic": "POST /agent/anthropic/run",
            "gemini": "POST /agent/gemini/run"
        },
        "health_endpoint": "GET /health",
        "native_agui": True
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting LlamaIndex Agent on port 7780...")
    print("AG-UI Endpoints:")
    print("  - OpenAI:    POST http://localhost:7780/agent/openai/run")
    print("  - Anthropic: POST http://localhost:7780/agent/anthropic/run")
    print("  - Gemini:    POST http://localhost:7780/agent/gemini/run")
    print("Using NATIVE llama-index-protocols-ag-ui package")
    uvicorn.run(app, host="0.0.0.0", port=7780)

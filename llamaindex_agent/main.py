"""
LlamaIndex Agent with AG-UI Protocol Support
Port: 7780
Endpoint: POST /agent

LlamaIndex has native AG-UI support via llama-index-protocols-ag-ui package.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from llama_index.protocols.ag_ui.router import get_ag_ui_workflow_router
from llama_index.llms.openai import OpenAI


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


# Create the AG-UI router with LlamaIndex
# Using OpenAI since LlamaIndex's AG-UI adapter works well with it
agentic_chat_router = get_ag_ui_workflow_router(
    llm=OpenAI(model="gpt-5.2-mini"),
    frontend_tools=[],  # Tools that trigger UI actions
    backend_tools=[get_current_time, calculator],  # Tools executed on server
    system_prompt="""You are a helpful assistant running on the LlamaIndex framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses.""",
    initial_state=None,
)

# Create FastAPI app
app = FastAPI(
    title="LlamaIndex AG-UI Test Agent",
    description="LlamaIndex agent with native AG-UI protocol support"
)

# Include the AG-UI router
app.include_router(agentic_chat_router, prefix="/agent")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "llamaindex",
        "port": 7780,
        "agui_endpoint": "/agent",
        "native_agui": True
    }


@app.get("/")
async def root():
    return {
        "name": "LlamaIndex AG-UI Test Agent",
        "framework": "llamaindex",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health",
        "native_agui": True
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting LlamaIndex Agent on port 7780...")
    print("AG-UI Endpoint: POST http://localhost:7780/agent")
    print("Using NATIVE llama-index-protocols-ag-ui package")
    uvicorn.run(app, host="0.0.0.0", port=7780)

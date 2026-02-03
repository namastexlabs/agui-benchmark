"""
Agno Agent with AG-UI Protocol Support
Port: 7771
Endpoints:
  - POST /agui/anthropic (Claude)
  - POST /agui/openai (GPT-4o-mini)
  - POST /agui/gemini (Gemini 2.0 Flash)

Agno has native AG-UI support via the AGUI() interface.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agno.agent.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI
from agno.tools import tool


@tool()
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool()
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A math expression like "2 + 2" or "10 * 5"
    """
    try:
        # Safe eval for basic math
        allowed_chars = set("0123456789+-*/.() ")
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"{expression} = {result}"
        return "Invalid expression - only basic math allowed"
    except Exception as e:
        return f"Error: {str(e)}"


# Common instructions for all agents
COMMON_INSTRUCTIONS = """You are a helpful assistant running on the Agno framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses."""

# Common tools for all agents
COMMON_TOOLS = [get_current_time, calculator]

# Create the Anthropic agent (Claude)
anthropic_agent = Agent(
    model=Claude(id="claude-haiku-4-5-20251001"),
    tools=COMMON_TOOLS,
    instructions=COMMON_INSTRUCTIONS,
    name="agno-anthropic",
    description="Agno agent with Claude (Anthropic)",
)

# Create the OpenAI agent (GPT-4o-mini)
openai_agent = Agent(
    model=OpenAIChat(id="gpt-5-mini"),
    tools=COMMON_TOOLS,
    instructions=COMMON_INSTRUCTIONS,
    name="agno-openai",
    description="Agno agent with GPT-4o-mini (OpenAI)",
)

# Create the Gemini agent (Gemini 2.0 Flash)
gemini_agent = Agent(
    model=Gemini(id="gemini-2.5-flash"),
    tools=COMMON_TOOLS,
    instructions=COMMON_INSTRUCTIONS,
    name="agno-gemini",
    description="Agno agent with Gemini 2.0 Flash (Google)",
)

# Create AgentOS with multiple AGUI interfaces at different prefixes
agent_os = AgentOS(
    agents=[anthropic_agent, openai_agent, gemini_agent],
    interfaces=[
        AGUI(agent=anthropic_agent, prefix="/agui/anthropic"),
        AGUI(agent=openai_agent, prefix="/agui/openai"),
        AGUI(agent=gemini_agent, prefix="/agui/gemini"),
    ]
)

# Get the FastAPI app
app = agent_os.get_app()


# Add a health endpoint for testing
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "agno",
        "port": 7771,
        "providers": ["anthropic", "openai", "gemini"],
        "agui_endpoints": {
            "anthropic": "/agui/anthropic",
            "openai": "/agui/openai",
            "gemini": "/agui/gemini",
        },
        "models": {
            "anthropic": "claude-haiku-4-5-20251001",
            "openai": "gpt-5-mini",
            "gemini": "gemini-2.5-flash",
        }
    }


@app.get("/")
async def root():
    return {
        "name": "Agno AG-UI Test Agent",
        "framework": "agno",
        "providers": ["anthropic", "openai", "gemini"],
        "agui_endpoints": {
            "anthropic": "POST /agui/anthropic",
            "openai": "POST /agui/openai",
            "gemini": "POST /agui/gemini",
        },
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    print("Starting Agno Agent on port 7771...")
    print("AG-UI Endpoints:")
    print("  - POST http://localhost:7771/agui/anthropic (Claude)")
    print("  - POST http://localhost:7771/agui/openai (GPT-4o-mini)")
    print("  - POST http://localhost:7771/agui/gemini (Gemini 2.0 Flash)")
    agent_os.serve(app="main:app", host="0.0.0.0", port=7771, reload=False)

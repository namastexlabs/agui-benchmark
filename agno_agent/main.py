"""
Agno Agent with AG-UI Protocol Support
Port: 7771
Endpoint: POST /agui

Agno has native AG-UI support via the AGUI() interface.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agno.agent.agent import Agent
from agno.models.anthropic import Claude
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


# Create the agent
agent = Agent(
    model=Claude(id="claude-haiku-4-5-20251001"),
    tools=[get_current_time, calculator],
    instructions="""You are a helpful assistant running on the Agno framework.
    You can tell the current time and do basic math calculations.
    Be concise and friendly in your responses.""",
    name="agno-assistant",
    description="Agno test agent with AG-UI support",
)

# Create AgentOS with AGUI interface
agent_os = AgentOS(
    agents=[agent],
    interfaces=[AGUI(agent=agent)]
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
        "agui_endpoint": "/agui"
    }


@app.get("/")
async def root():
    return {
        "name": "Agno AG-UI Test Agent",
        "framework": "agno",
        "agui_endpoint": "POST /agui",
        "health_endpoint": "GET /health"
    }


if __name__ == "__main__":
    print("Starting Agno Agent on port 7771...")
    print("AG-UI Endpoint: POST http://localhost:7771/agui")
    agent_os.serve(app="main:app", host="0.0.0.0", port=7771, reload=False)

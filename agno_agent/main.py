"""
Agno Agent with AG-UI Protocol Support
Port: 7771
Endpoints:
  - POST /agui/anthropic (Claude)
  - POST /agui/openai (GPT-4o-mini)
  - POST /agui/gemini (Gemini 2.0 Flash)
  - POST /agui/cerebras (Cerebras Llama 3.3 70B via OpenAI-compatible API)

Agno has native AG-UI support via the AGUI() interface.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@tool()
def request_approval(action: str, reason: str = "") -> str:
    """
    Request human approval before proceeding with an action.

    Args:
        action: The action that requires approval (e.g., "delete important data")
        reason: Optional reason for the action

    Returns:
        Approval status and message
    """
    approval_message = f"APPROVAL_REQUESTED: Action '{action}' requires human approval"
    if reason:
        approval_message += f" (Reason: {reason})"
    return approval_message


# Common instructions for all agents
COMMON_INSTRUCTIONS = """You are a helpful assistant running on the Agno framework.
    You can tell the current time, do basic math calculations, and request approval for sensitive actions.
    IMPORTANT: When a user asks to do something potentially dangerous or sensitive (like deleting data),
    you MUST use the request_approval tool first to ask for human approval before proceeding.
    Be concise and friendly in your responses."""

# Common tools for all agents
COMMON_TOOLS = [get_current_time, calculator, request_approval]

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

# Create the Cerebras agent (Llama 3.3 70B via OpenAI-compatible API)
cerebras_api_key = os.getenv("CEREBRAS_API_KEY")
cerebras_agent = None
agui_interfaces = [
    AGUI(agent=anthropic_agent, prefix="/agui/anthropic"),
    AGUI(agent=openai_agent, prefix="/agui/openai"),
    AGUI(agent=gemini_agent, prefix="/agui/gemini"),
]

if cerebras_api_key:
    try:
        logger.info("Initializing Cerebras agent with API key...")
        cerebras_agent = Agent(
            model=OpenAIChat(
                id="llama-3.3-70b",
                api_key=cerebras_api_key,
                base_url="https://api.cerebras.ai/v1"
            ),
            tools=COMMON_TOOLS,
            instructions=COMMON_INSTRUCTIONS,
            name="agno-cerebras",
            description="Agno agent with Cerebras Llama 3.3 70B (OpenAI-compatible)",
        )
        logger.info("✅ Cerebras agent initialized successfully")
        agui_interfaces.append(AGUI(agent=cerebras_agent, prefix="/agui/cerebras"))
    except Exception as e:
        logger.error(f"❌ Failed to initialize Cerebras agent: {str(e)}")
        cerebras_agent = None
else:
    logger.warning("⚠️  CEREBRAS_API_KEY not set, skipping Cerebras agent")

# Create AgentOS with multiple AGUI interfaces at different prefixes
agents_list = [anthropic_agent, openai_agent, gemini_agent]
if cerebras_agent:
    agents_list.append(cerebras_agent)

agent_os = AgentOS(
    agents=agents_list,
    interfaces=agui_interfaces
)

# Get the FastAPI app
app = agent_os.get_app()


# Add a health endpoint for testing
@app.get("/health")
async def health():
    providers = ["anthropic", "openai", "gemini"]
    endpoints = {
        "anthropic": "/agui/anthropic",
        "openai": "/agui/openai",
        "gemini": "/agui/gemini",
    }
    models = {
        "anthropic": "claude-haiku-4-5-20251001",
        "openai": "gpt-5-mini",
        "gemini": "gemini-2.5-flash",
    }

    if cerebras_agent:
        providers.append("cerebras")
        endpoints["cerebras"] = "/agui/cerebras"
        models["cerebras"] = "llama-3.3-70b"

    return {
        "status": "healthy",
        "framework": "agno",
        "port": 7771,
        "providers": providers,
        "agui_endpoints": endpoints,
        "models": models,
        "cerebras_enabled": cerebras_agent is not None,
    }


@app.get("/")
async def root():
    providers = ["anthropic", "openai", "gemini"]
    endpoints = {
        "anthropic": "POST /agui/anthropic",
        "openai": "POST /agui/openai",
        "gemini": "POST /agui/gemini",
    }

    if cerebras_agent:
        providers.append("cerebras")
        endpoints["cerebras"] = "POST /agui/cerebras"

    return {
        "name": "Agno AG-UI Test Agent",
        "framework": "agno",
        "providers": providers,
        "agui_endpoints": endpoints,
        "health_endpoint": "GET /health",
        "cerebras_enabled": cerebras_agent is not None,
    }


if __name__ == "__main__":
    print("Starting Agno Agent on port 7771...")
    print("AG-UI Endpoints:")
    print("  ✅ POST http://localhost:7771/agui/anthropic (Claude)")
    print("  ✅ POST http://localhost:7771/agui/openai (GPT-4o-mini)")
    print("  ✅ POST http://localhost:7771/agui/gemini (Gemini 2.0 Flash)")
    if cerebras_agent:
        print("  ✅ POST http://localhost:7771/agui/cerebras (Cerebras Llama 3.3 70B)")
    else:
        print("  ⚠️  POST http://localhost:7771/agui/cerebras (Cerebras - NOT ENABLED)")
    agent_os.serve(app="main:app", host="0.0.0.0", port=7771, reload=False)

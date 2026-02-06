"""
LangGraph Agent with AG-UI Protocol Support (NATIVE)
Port: 7772
Endpoints:
  - POST /agent/anthropic (Claude)
  - POST /agent/openai (GPT)
  - POST /agent/gemini (Gemini)
  - POST /agent/cerebras (Cerebras Llama via OpenAI-compatible API)

Uses ag-ui-langgraph package for native AG-UI integration.
Supports multiple LLM providers via separate endpoints.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool

# Native AG-UI integration
from ag_ui_langgraph import LangGraphAgent, add_langgraph_fastapi_endpoint


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
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


# Tools list (shared across all agents)
tools = [get_current_time, calculator]


def create_graph(llm):
    """
    Factory function to create a compiled LangGraph with the given LLM.

    Args:
        llm: A LangChain chat model with tools bound

    Returns:
        A compiled LangGraph ready for use with AG-UI
    """
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        """Call the LLM with the current messages."""
        system_message = {
            "role": "system",
            "content": """You are a helpful assistant running on LangGraph framework.
            You can tell the current time and do basic math calculations.
            Be concise and friendly in your responses."""
        }
        messages = [system_message] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: MessagesState):
        """Determine if we should continue to tools or end."""
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools))
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")

    # Create memory checkpointer (required by ag-ui-langgraph)
    memory = MemorySaver()

    # Compile the graph with checkpointer
    return workflow.compile(checkpointer=memory)


# Create LLM instances for each provider
llm_anthropic = ChatAnthropic(model="claude-haiku-4-5-20251001")
llm_openai = ChatOpenAI(model="gpt-5-mini")
llm_gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm_cerebras = ChatOpenAI(
    model="llama-3.3-70b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1"
)

# Create compiled graphs for each LLM
graph_anthropic = create_graph(llm_anthropic)
graph_openai = create_graph(llm_openai)
graph_gemini = create_graph(llm_gemini)
graph_cerebras = create_graph(llm_cerebras)

# Create LangGraphAgent instances for each provider
agent_anthropic = LangGraphAgent(
    name="langgraph-anthropic",
    graph=graph_anthropic,
    description="LangGraph agent with Claude (Anthropic)"
)

agent_openai = LangGraphAgent(
    name="langgraph-openai",
    graph=graph_openai,
    description="LangGraph agent with GPT (OpenAI)"
)

agent_gemini = LangGraphAgent(
    name="langgraph-gemini",
    graph=graph_gemini,
    description="LangGraph agent with Gemini (Google)"
)

agent_cerebras = LangGraphAgent(
    name="langgraph-cerebras",
    graph=graph_cerebras,
    description="LangGraph agent with Cerebras Llama (OpenAI-compatible)"
)

# Create FastAPI app
app = FastAPI(
    title="LangGraph AG-UI Test Agent",
    description="LangGraph agent with native AG-UI protocol support for multiple LLM providers"
)

# Add native AG-UI endpoints for each provider
add_langgraph_fastapi_endpoint(app, agent_anthropic, "/agent/anthropic")
add_langgraph_fastapi_endpoint(app, agent_openai, "/agent/openai")
add_langgraph_fastapi_endpoint(app, agent_gemini, "/agent/gemini")
add_langgraph_fastapi_endpoint(app, agent_cerebras, "/agent/cerebras")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "langgraph",
        "port": 7772,
        "providers": {
            "anthropic": {
                "endpoint": "/agent/anthropic",
                "model": "claude-haiku-4-5-20251001"
            },
            "openai": {
                "endpoint": "/agent/openai",
                "model": "gpt-5-mini"
            },
            "gemini": {
                "endpoint": "/agent/gemini",
                "model": "gemini-2.5-flash"
            },
            "cerebras": {
                "endpoint": "/agent/cerebras",
                "model": "llama-3.3-70b"
            }
        },
        "native_agui": True
    }


@app.get("/")
async def root():
    return {
        "name": "LangGraph AG-UI Test Agent",
        "framework": "langgraph",
        "agui_endpoints": {
            "anthropic": "POST /agent/anthropic",
            "openai": "POST /agent/openai",
            "gemini": "POST /agent/gemini",
            "cerebras": "POST /agent/cerebras"
        },
        "health_endpoint": "GET /health",
        "native_agui": True
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting LangGraph Agent on port 7772...")
    print("AG-UI Endpoints:")
    print("  - POST http://localhost:7772/agent/anthropic (Claude)")
    print("  - POST http://localhost:7772/agent/openai (GPT)")
    print("  - POST http://localhost:7772/agent/gemini (Gemini)")
    print("  - POST http://localhost:7772/agent/cerebras (Cerebras Llama 3.3 70B)")
    print("  - POST http://localhost:7772/agent/openai (GPT)")
    print("  - POST http://localhost:7772/agent/gemini (Gemini)")
    print("Using NATIVE ag-ui-langgraph package")
    uvicorn.run(app, host="0.0.0.0", port=7772)

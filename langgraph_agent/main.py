"""
LangGraph Agent with AG-UI Protocol Support (NATIVE)
Port: 7772
Endpoint: POST /agent

Uses ag-ui-langgraph package for native AG-UI integration.
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


# Tools list
tools = [get_current_time, calculator]

# Create LLM with tools bound
llm = ChatAnthropic(model="claude-haiku-4-5-20251001").bind_tools(tools)


def call_model(state: MessagesState):
    """Call the LLM with the current messages."""
    system_message = {
        "role": "system",
        "content": """You are a helpful assistant running on LangGraph framework.
        You can tell the current time and do basic math calculations.
        Be concise and friendly in your responses."""
    }
    messages = [system_message] + state["messages"]
    response = llm.invoke(messages)
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
compiled_graph = workflow.compile(checkpointer=memory)

# Wrap in LangGraphAgent for AG-UI compatibility
langgraph_agent = LangGraphAgent(
    name="langgraph-assistant",
    graph=compiled_graph,
    description="LangGraph test agent with AG-UI support"
)

# Create FastAPI app
app = FastAPI(
    title="LangGraph AG-UI Test Agent",
    description="LangGraph agent with native AG-UI protocol support"
)

# Add native AG-UI endpoint
add_langgraph_fastapi_endpoint(app, langgraph_agent, "/agent")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "langgraph",
        "port": 7772,
        "agui_endpoint": "/agent",
        "native_agui": True
    }


@app.get("/")
async def root():
    return {
        "name": "LangGraph AG-UI Test Agent",
        "framework": "langgraph",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health",
        "native_agui": True
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting LangGraph Agent on port 7772...")
    print("AG-UI Endpoint: POST http://localhost:7772/agent")
    print("Using NATIVE ag-ui-langgraph package")
    uvicorn.run(app, host="0.0.0.0", port=7772)

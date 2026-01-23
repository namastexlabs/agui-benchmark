"""
CrewAI Agent with AG-UI Protocol Support (NATIVE)
Port: 7773
Endpoint: POST /agent

Uses ag-ui-crewai package for native AG-UI integration with Flow API.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from crewai import Agent, Task, Crew
from crewai.flow.flow import Flow, listen, start
from crewai.tools import tool

# Native AG-UI integration
from ag_ui_crewai import (
    CopilotKitState,
    add_crewai_flow_fastapi_endpoint,
    copilotkit_stream,
    copilotkit_emit_state,
)


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


# Create CrewAI agent
assistant_agent = Agent(
    role="Helpful Assistant",
    goal="Help users with questions, tell time, and do math calculations",
    backstory="""You are a friendly AI assistant running on the CrewAI framework.
    You can tell the current time and do basic math calculations.
    Be concise and helpful in your responses.""",
    tools=[get_current_time, calculator],
    verbose=False,
    allow_delegation=False,
    llm="anthropic/claude-haiku-4-5-20251001",
)


class AssistantFlow(Flow[CopilotKitState]):
    """CrewAI Flow with AG-UI support."""

    @start()
    def handle_message(self):
        """Entry point - handles incoming messages."""
        # Get the last user message from state
        user_message = ""
        if self.state.messages:
            for msg in reversed(self.state.messages):
                if hasattr(msg, 'role') and msg.role == "user":
                    user_message = msg.content if hasattr(msg, 'content') else str(msg)
                    break
                elif isinstance(msg, dict) and msg.get('role') == "user":
                    user_message = msg.get('content', '')
                    break

        if not user_message:
            user_message = "Hello"

        # Create task for this message
        task = Task(
            description=f"Respond to this user request: {user_message}",
            expected_output="A helpful, concise response to the user's request",
            agent=assistant_agent
        )

        # Create and execute crew with streaming
        crew = Crew(
            agents=[assistant_agent],
            tasks=[task],
            verbose=False
        )

        # Execute with AG-UI streaming wrapper
        result = copilotkit_stream(crew.kickoff())

        return str(result)


# Create the flow instance
assistant_flow = AssistantFlow()

# Create FastAPI app
app = FastAPI(
    title="CrewAI AG-UI Test Agent",
    description="CrewAI agent with native AG-UI protocol support"
)

# Add native AG-UI endpoint
add_crewai_flow_fastapi_endpoint(app, assistant_flow, "/agent")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "framework": "crewai",
        "port": 7773,
        "agui_endpoint": "/agent",
        "native_agui": True
    }


@app.get("/")
async def root():
    return {
        "name": "CrewAI AG-UI Test Agent",
        "framework": "crewai",
        "agui_endpoint": "POST /agent",
        "health_endpoint": "GET /health",
        "native_agui": True
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting CrewAI Agent on port 7773...")
    print("AG-UI Endpoint: POST http://localhost:7773/agent")
    print("Using NATIVE ag-ui-crewai package")
    uvicorn.run(app, host="0.0.0.0", port=7773)

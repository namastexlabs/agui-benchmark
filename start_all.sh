#!/bin/bash
# Start all AG-UI test agents in background

cd /tmp/agui-test-frameworks

echo "🚀 Starting AG-UI Test Agents..."
echo ""

# Create log directory
mkdir -p logs

# Agent Frameworks (Native AG-UI)
echo "=== Agent Frameworks (Native AG-UI) ==="

echo "Starting Agno agent on port 7771..."
uv run python agno_agent/main.py > logs/agno.log 2>&1 &
echo $! > logs/agno.pid

echo "Starting LangGraph agent on port 7772..."
uv run python langgraph_agent/main.py > logs/langgraph.log 2>&1 &
echo $! > logs/langgraph.pid

echo "Starting CrewAI agent on port 7773..."
uv run python crewai_agent/main.py > logs/crewai.log 2>&1 &
echo $! > logs/crewai.pid

echo "Starting PydanticAI agent on port 7774..."
uv run python pydantic_agent/main.py > logs/pydantic.log 2>&1 &
echo $! > logs/pydantic.pid

echo "Starting LlamaIndex agent on port 7780..."
uv run python llamaindex_agent/main.py > logs/llamaindex.log 2>&1 &
echo $! > logs/llamaindex.pid

echo "Starting AG2 agent on port 7781..."
uv run python ag2_agent/main.py > logs/ag2.log 2>&1 &
echo $! > logs/ag2.pid

echo "Starting Google ADK agent on port 7782..."
uv run python google_adk_agent/main.py > logs/google_adk.log 2>&1 &
echo $! > logs/google_adk.pid

# Raw LLM APIs (AG-UI Wrapped)
echo ""
echo "=== Raw LLM APIs (AG-UI Wrapped) ==="

echo "Starting OpenAI Raw agent on port 7775..."
uv run python openai_raw/main.py > logs/openai.log 2>&1 &
echo $! > logs/openai.pid

echo "Starting Anthropic Raw agent on port 7776..."
uv run python anthropic_raw/main.py > logs/anthropic.log 2>&1 &
echo $! > logs/anthropic.pid

echo "Starting Gemini Raw agent on port 7777..."
uv run python gemini_raw/main.py > logs/gemini.log 2>&1 &
echo $! > logs/gemini.pid

# TypeScript Agents (AG-UI Wrapped)
echo ""
echo "=== TypeScript Agents ==="

# Check if node_modules exists, if not install
if [ ! -d "ts-agents/node_modules" ]; then
    echo "Installing TypeScript dependencies..."
    (cd ts-agents && npm install --legacy-peer-deps) > logs/npm-install.log 2>&1
fi

# Copy .env to ts-agents if it exists
if [ -f ".env" ]; then
    cp .env ts-agents/.env
fi

echo "Starting Vercel AI SDK agent on port 7779..."
(cd ts-agents && npx tsx vercel_agent/main.ts) > logs/vercel.log 2>&1 &
echo $! > logs/vercel.pid

echo ""
echo "✅ All agents starting..."
echo ""
echo "=== Python Agent Frameworks (Native AG-UI) ==="
echo "  - Agno:       http://localhost:7771/agui"
echo "  - LangGraph:  http://localhost:7772/agent"
echo "  - CrewAI:     http://localhost:7773/agent"
echo "  - PydanticAI: http://localhost:7774/"
echo "  - LlamaIndex: http://localhost:7780/agent"
echo "  - AG2:        http://localhost:7781/agent"
echo "  - Google ADK: http://localhost:7782/agent"
echo ""
echo "=== Raw LLM APIs (AG-UI Wrapped) ==="
echo "  - OpenAI:     http://localhost:7775/agent"
echo "  - Anthropic:  http://localhost:7776/agent"
echo "  - Gemini:     http://localhost:7777/agent"
echo ""
echo "=== TypeScript Agents (AG-UI Wrapped) ==="
echo "  - Vercel AI SDK: http://localhost:7779/agent"
echo ""
echo "Logs: /tmp/agui-test-frameworks/logs/"
echo ""
echo "To test: uv run python test_agents.py"
echo "To stop: ./stop_all.sh"

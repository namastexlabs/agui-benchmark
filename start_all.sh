#!/bin/bash
# Start all AG-UI test agents in background and measure startup times

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting AG-UI Test Agents..."
echo ""

# Create log directory
mkdir -p logs

# Record global start time (nanoseconds)
GLOBAL_START=$(date +%s%N)

# Function to get milliseconds since global start
ms_since_start() {
    local now=$(date +%s%N)
    echo $(( (now - GLOBAL_START) / 1000000 ))
}

# Arrays to track agents
declare -A AGENT_HEALTH_URLS
declare -A AGENT_START_TIMES

# Function to start an agent and record start time
start_agent() {
    local name=$1
    local cmd=$2
    local log=$3
    local health_url=$4

    AGENT_START_TIMES[$name]=$(ms_since_start)
    eval "$cmd" > "logs/$log.log" 2>&1 &
    echo $! > "logs/$log.pid"
    AGENT_HEALTH_URLS[$name]=$health_url
    echo "  Starting $name..."
}

# Agent Frameworks (Native AG-UI)
echo "=== Agent Frameworks (Native AG-UI) ==="
start_agent "agno" "uv run python agno_agent/main.py" "agno" "http://localhost:7771/health"
start_agent "langgraph" "uv run python langgraph_agent/main.py" "langgraph" "http://localhost:7772/health"
start_agent "crewai" "uv run python crewai_agent/main.py" "crewai" "http://localhost:7773/health"
start_agent "pydantic-ai" "uv run python pydantic_agent/main.py" "pydantic" "http://localhost:7774/health"
start_agent "llamaindex" "uv run python llamaindex_agent/main.py" "llamaindex" "http://localhost:7780/health"
start_agent "ag2" "uv run python ag2_agent/main.py" "ag2" "http://localhost:7781/health"
start_agent "google-adk" "uv run python google_adk_agent/main.py" "google_adk" "http://localhost:7782/health"

# Raw LLM APIs (AG-UI Wrapped)
echo ""
echo "=== Raw LLM APIs (AG-UI Wrapped) ==="
start_agent "openai-raw" "uv run python openai_raw/main.py" "openai" "http://localhost:7775/health"
start_agent "anthropic-raw" "uv run python anthropic_raw/main.py" "anthropic" "http://localhost:7776/health"
start_agent "gemini-raw" "uv run python gemini_raw/main.py" "gemini" "http://localhost:7777/health"

# TypeScript Agents (AG-UI Wrapped)
echo ""
echo "=== TypeScript Agents ==="

# Check if node_modules exists, if not install
if [ ! -d "ts-agents/node_modules" ]; then
    echo "  Installing TypeScript dependencies..."
    (cd ts-agents && npm install --legacy-peer-deps) > logs/npm-install.log 2>&1
fi

# Copy .env to ts-agents if it exists
if [ -f ".env" ]; then
    cp .env ts-agents/.env
fi

AGENT_START_TIMES["vercel-ai-sdk"]=$(ms_since_start)
(cd ts-agents && npx tsx vercel_agent/main.ts) > logs/vercel.log 2>&1 &
echo $! > logs/vercel.pid
AGENT_HEALTH_URLS["vercel-ai-sdk"]="http://localhost:7779/health"
echo "  Starting vercel-ai-sdk..."

echo ""
echo "⏱️  Measuring startup times..."

# Wait for agents and measure startup times
declare -A AGENT_STARTUP_TIMES
MAX_WAIT=60  # Maximum seconds to wait for each agent
POLL_INTERVAL=0.1  # Poll every 100ms

# Initialize JSON output
echo "{" > logs/startup_times.json

first=true
for name in "${!AGENT_HEALTH_URLS[@]}"; do
    url="${AGENT_HEALTH_URLS[$name]}"
    start_time="${AGENT_START_TIMES[$name]}"

    # Poll until healthy or timeout
    elapsed=0
    while [ $elapsed -lt $MAX_WAIT ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "200"; then
            ready_time=$(ms_since_start)
            startup_ms=$((ready_time - start_time))
            AGENT_STARTUP_TIMES[$name]=$startup_ms
            printf "  ✅ %-15s ready in %5d ms\n" "$name" "$startup_ms"
            break
        fi
        sleep $POLL_INTERVAL
        elapsed=$((elapsed + 1))
    done

    if [ -z "${AGENT_STARTUP_TIMES[$name]}" ]; then
        AGENT_STARTUP_TIMES[$name]=-1
        printf "  ❌ %-15s failed to start\n" "$name"
    fi

    # Write to JSON
    if [ "$first" = true ]; then
        first=false
    else
        echo "," >> logs/startup_times.json
    fi
    echo "  \"$name\": ${AGENT_STARTUP_TIMES[$name]}" >> logs/startup_times.json
done

echo "}" >> logs/startup_times.json

echo ""
echo "✅ All agents started!"
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
echo "Startup times saved to: $SCRIPT_DIR/logs/startup_times.json"
echo ""
echo "To test: uv run python test_agents.py"
echo "To stop: ./stop_all.sh"

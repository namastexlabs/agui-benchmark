# AG-UI Benchmark Project

## Overview
This project benchmarks the AG-UI (Agent-User Interaction) protocol across multiple AI agent frameworks. It tests protocol compliance, response times, and tool calling performance.

**Key Feature**: Multi-model testing - each framework is tested with Claude, OpenAI, and Gemini models for fair cross-framework and cross-model comparisons.

## Quick Start

```bash
# Install dependencies
uv sync
cd ts-agents && npm install && cd ..

# Start all agents
./start_all.sh

# Run benchmarks
uv run python test_agents.py

# Stop all agents
./stop_all.sh
```

## Project Structure

```
├── agno_agent/          # Agno framework (Python, native AG-UI, multi-model)
├── langgraph_agent/     # LangGraph framework (Python, native AG-UI, multi-model)
├── crewai_agent/        # CrewAI framework (Python, native AG-UI) *
├── pydantic_agent/      # PydanticAI framework (Python, native AG-UI, multi-model)
├── llamaindex_agent/    # LlamaIndex framework (Python, native AG-UI, multi-model)
├── ag2_agent/           # AG2/AutoGen framework (Python, AG-UI wrapped, OpenAI only)
├── google_adk_agent/    # Google ADK framework (Python, native AG-UI, Gemini only)
├── openai_raw/          # Direct OpenAI API (Python, AG-UI wrapped)
├── anthropic_raw/       # Direct Anthropic API (Python, AG-UI wrapped)
├── gemini_raw/          # Direct Gemini API (Python, AG-UI wrapped)
├── ts-agents/           # TypeScript agents
│   └── vercel_agent/    # Vercel AI SDK (TypeScript, AG-UI wrapped, multi-model)
├── test_agents.py       # Main benchmark script
├── start_all.sh         # Start all agents
├── stop_all.sh          # Stop all agents
└── pyproject.toml       # Python dependencies
```

* CrewAI has known issues with `ag-ui-crewai` package

## Multi-Model Endpoints

### Multi-Model Frameworks (support Claude, OpenAI, Gemini)

| Framework | Port | Claude Endpoint | OpenAI Endpoint | Gemini Endpoint |
|-----------|------|-----------------|-----------------|-----------------|
| Agno | 7771 | `/agui/anthropic` | `/agui/openai` | `/agui/gemini` |
| LangGraph | 7772 | `/agent/anthropic` | `/agent/openai` | `/agent/gemini` |
| PydanticAI | 7774 | `/anthropic` | `/openai` | `/gemini` |
| LlamaIndex | 7780 | `/agent/anthropic/run` | `/agent/openai/run` | `/agent/gemini/run` |
| Vercel AI SDK | 7779 | `/agent/anthropic` | `/agent/openai` | `/agent/gemini` |

### Single-Model Frameworks

| Port | Framework | Model | Endpoint |
|------|-----------|-------|----------|
| 7773 | CrewAI | Claude | `/agent` |
| 7781 | AG2 (AutoGen) | OpenAI | `/agent` |
| 7782 | Google ADK | Gemini | `/agent` |

### Raw LLM APIs (Baseline)

| Port | API | Model | Endpoint |
|------|-----|-------|----------|
| 7775 | OpenAI Raw | gpt-4o-mini | `/agent` |
| 7776 | Anthropic Raw | claude-haiku-4-5 | `/agent` |
| 7777 | Gemini Raw | gemini-2.0-flash | `/agent` |

## Models Tested

| Model Key | Model ID | Provider |
|-----------|----------|----------|
| claude | claude-haiku-4-5-20251001 | Anthropic |
| openai | gpt-4o-mini | OpenAI |
| gemini | gemini-2.0-flash | Google |

## Environment Variables

Create a `.env` file with your API keys:

```env
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
```

## Test Output

The benchmark produces comparisons:

1. **By Model**: Same model across different frameworks (fair framework comparison)
2. **By Framework**: Same framework with different models (fair model comparison)
3. **Overall Ranking**: All framework+model combinations sorted by performance

## AG-UI Protocol Events

The benchmark tests for these events:
- `RUN_STARTED` / `RUN_FINISHED` - Lifecycle events
- `TEXT_MESSAGE_START` / `TEXT_MESSAGE_CONTENT` / `TEXT_MESSAGE_END` - Streaming text
- `TOOL_CALL_START` / `TOOL_CALL_ARGS` / `TOOL_CALL_END` / `TOOL_CALL_RESULT` - Tool calls
- `MESSAGES_SNAPSHOT` / `STATE_SNAPSHOT` - State management (CrewAI pattern)

## Adding New Frameworks

1. Create a new directory for the agent
2. Implement AG-UI endpoints (POST) for each model you want to support
3. Add health endpoint (GET /health)
4. Add to `start_all.sh` and `stop_all.sh`
5. Add to `AGENTS` dict in `test_agents.py` (one entry per framework+model combination)

## Known Issues

- **CrewAI**: `ag-ui-crewai` package expects LiteLLM responses, not crew.kickoff()
- **Mastra**: Version conflicts between `@mastra/core` and `@ag-ui/mastra` (not included)
- **LangGraph**: Occasional failures on simple prompts (needs investigation)
- **AG2**: Uses custom AG-UI adapter (no official `ag-ui-ag2` package yet)
- **LlamaIndex**: AG-UI router adds `/run` to endpoints automatically
- **Google ADK**: Requires session creation before running

# AG-UI Benchmark Project

## Overview
This project benchmarks the AG-UI (Agent-User Interaction) protocol across multiple AI agent frameworks. It tests protocol compliance, response times, and tool calling performance.

## Quick Start

```bash
# Install dependencies
uv sync

# Start all agents
./start_all.sh

# Run benchmarks
uv run python test_agents.py

# Stop all agents
./stop_all.sh
```

## Project Structure

```
├── agno_agent/          # Agno framework (Python, native AG-UI)
├── langgraph_agent/     # LangGraph framework (Python, native AG-UI)
├── crewai_agent/        # CrewAI framework (Python, native AG-UI) *
├── pydantic_agent/      # PydanticAI framework (Python, native AG-UI)
├── llamaindex_agent/    # LlamaIndex framework (Python, native AG-UI)
├── ag2_agent/           # AG2/AutoGen framework (Python, AG-UI wrapped)
├── google_adk_agent/    # Google ADK framework (Python, native AG-UI)
├── openai_raw/          # Direct OpenAI API (Python, AG-UI wrapped)
├── anthropic_raw/       # Direct Anthropic API (Python, AG-UI wrapped)
├── gemini_raw/          # Direct Gemini API (Python, AG-UI wrapped)
├── ts-agents/           # TypeScript agents
│   └── vercel_agent/    # Vercel AI SDK (TypeScript, AG-UI wrapped)
├── test_agents.py       # Main benchmark script
├── start_all.sh         # Start all agents
├── stop_all.sh          # Stop all agents
└── pyproject.toml       # Python dependencies
```

* CrewAI has known issues with `ag-ui-crewai` package

## Ports

| Port | Framework | Type |
|------|-----------|------|
| 7771 | Agno | Native AG-UI |
| 7772 | LangGraph | Native AG-UI |
| 7773 | CrewAI | Native AG-UI |
| 7774 | PydanticAI | Native AG-UI |
| 7775 | OpenAI Raw | Wrapped |
| 7776 | Anthropic Raw | Wrapped |
| 7777 | Gemini Raw | Wrapped |
| 7779 | Vercel AI SDK | Wrapped (TS) |
| 7780 | LlamaIndex | Native AG-UI |
| 7781 | AG2 (AutoGen) | Wrapped |
| 7782 | Google ADK | Native AG-UI |

## Environment Variables

Create a `.env` file with your API keys:

```env
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
```

## Adding New Frameworks

1. Create a new directory for the agent
2. Implement the AG-UI endpoint (POST /agent)
3. Add health endpoint (GET /health)
4. Add to `start_all.sh` and `stop_all.sh`
5. Add to `AGENTS` dict in `test_agents.py`

## AG-UI Protocol Events

The benchmark tests for these events:
- `RUN_STARTED` / `RUN_FINISHED` - Lifecycle events
- `TEXT_MESSAGE_START` / `TEXT_MESSAGE_CONTENT` / `TEXT_MESSAGE_END` - Streaming text
- `TOOL_CALL_START` / `TOOL_CALL_ARGS` / `TOOL_CALL_END` / `TOOL_CALL_RESULT` - Tool calls
- `MESSAGES_SNAPSHOT` / `STATE_SNAPSHOT` - State management (CrewAI pattern)

## Known Issues

- **CrewAI**: `ag-ui-crewai` package expects LiteLLM responses, not crew.kickoff()
- **Mastra**: Version conflicts between `@mastra/core` and `@ag-ui/mastra` (not included)
- **LangGraph**: Occasional failures on simple prompts (needs investigation)
- **AG2**: Uses custom AG-UI adapter (no official `ag-ui-ag2` package yet)
- **LlamaIndex**: Requires OpenAI API key (uses `llama-index-protocols-ag-ui`)
- **Google ADK**: Requires Gemini API key

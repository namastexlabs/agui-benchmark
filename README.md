# AG-UI Benchmark

> Comprehensive benchmark suite for the AG-UI (Agent-User Interaction) protocol across multiple AI agent frameworks.

## What is AG-UI?

[AG-UI](https://docs.ag-ui.com/) is an open, lightweight, event-based protocol for agent-user interaction created by CopilotKit. It enables framework-agnostic communication between AI agents and user interfaces through Server-Sent Events (SSE).

## Why This Benchmark?

Different agent frameworks claim various performance characteristics, but real-world numbers are rarely published. This benchmark provides:

- **Protocol Compliance Testing** - Verify AG-UI event support
- **Response Time Benchmarks** - Measure latency across frameworks
- **Tool Calling Performance** - Compare function calling efficiency
- **Framework Overhead Analysis** - Quantify the cost of abstraction

## Benchmark Results

### Simple Response (No Tools)

| Rank | Framework | Avg Time | Model |
|------|-----------|----------|-------|
| 1 | Gemini Raw | 640ms | Gemini 2.5 Flash |
| 2 | Anthropic Raw | 667ms | Claude Haiku 4.5 |
| 3 | Vercel AI SDK | 797ms | Claude Haiku 4.5 |
| 4 | PydanticAI | 908ms | Claude Haiku 4.5 |
| 5 | LangGraph | 1,237ms | Claude Haiku 4.5 |
| 6 | Agno | 1,494ms | Claude Haiku 4.5 |
| 7 | OpenAI Raw | 2,148ms | GPT-5.2 |

### Tool Calling Performance

| Rank | Framework | Avg Time | Tools Used |
|------|-----------|----------|------------|
| 1 | OpenAI Raw | 1,467ms | 6/6 |
| 2 | LangGraph | 1,611ms | 3/6 |
| 3 | PydanticAI | 1,644ms | 6/6 |
| 4 | Gemini Raw | 2,064ms | 6/6 |
| 5 | Anthropic Raw | 2,395ms | 6/6 |
| 6 | Vercel AI SDK | 2,414ms | 6/6 |
| 7 | Agno | 2,905ms | 6/6 |

### Key Insights

- **PydanticAI** offers the best balance of speed and features
- **GPT-5.2** is slow for chat but fast for function calling
- **Gemini 2.5 Flash** is genuinely fast for simple responses
- **Raw API wrappers** often outperform native framework integrations
- **Agno** claims "fastest to instantiate" but has ~800ms overhead vs raw API

### Framework Overhead (vs Raw API)

| Framework | Overhead | Percentage |
|-----------|----------|------------|
| Vercel AI SDK | +130ms | +19% |
| PydanticAI | +241ms | +36% |
| LangGraph | +570ms | +85% |
| Agno | +827ms | +124% |

## Supported Frameworks

### Native AG-UI Support

| Framework | Language | Package | Status |
|-----------|----------|---------|--------|
| Agno | Python | Built-in `AGUI()` | Working |
| LangGraph | Python | `ag-ui-langgraph` | Working |
| PydanticAI | Python | Built-in `AGUIAdapter` | Working |
| CrewAI | Python | `ag-ui-crewai` | Issues* |

### AG-UI Wrapped (Manual Implementation)

| Framework | Language | Status |
|-----------|----------|--------|
| OpenAI API | Python | Working |
| Anthropic API | Python | Working |
| Gemini API | Python | Working |
| Vercel AI SDK | TypeScript | Working |

*CrewAI's `ag-ui-crewai` package expects LiteLLM responses, not `crew.kickoff()`

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for TypeScript agents)
- [uv](https://github.com/astral-sh/uv) package manager
- API keys for OpenAI, Anthropic, and Google

### Installation

```bash
# Clone the repository
git clone https://github.com/namastexlabs/agui-benchmark.git
cd agui-benchmark

# Install Python dependencies
uv sync

# Install TypeScript dependencies
cd ts-agents && npm install --legacy-peer-deps && cd ..

# Create .env file with your API keys
cat > .env << EOF
ANTHROPIC_API_KEY=your-anthropic-key
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
EOF
```

### Running Benchmarks

```bash
# Start all agents
./start_all.sh

# Wait for agents to initialize
sleep 10

# Run the benchmark
uv run python test_agents.py

# Stop all agents
./stop_all.sh
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        test_agents.py                            │
│                     (Benchmark Runner)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP POST /agent
                              │ Accept: text/event-stream
                              ▼
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   :7771     │   :7772     │   :7774     │   :7775-79  │
│   Agno      │  LangGraph  │  PydanticAI │   Raw APIs  │
│  (Native)   │  (Native)   │  (Native)   │  (Wrapped)  │
└─────────────┴─────────────┴─────────────┴─────────────┘
                              │
                              │ AG-UI SSE Events
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  RUN_STARTED → TEXT_MESSAGE_* → TOOL_CALL_* → RUN_FINISHED      │
└─────────────────────────────────────────────────────────────────┘
```

## AG-UI Protocol Events

| Event | Description |
|-------|-------------|
| `RUN_STARTED` | Agent run begins |
| `RUN_FINISHED` | Agent run completes |
| `TEXT_MESSAGE_START` | Begin streaming text |
| `TEXT_MESSAGE_CONTENT` | Text chunk (delta) |
| `TEXT_MESSAGE_END` | End streaming text |
| `TOOL_CALL_START` | Tool invocation begins |
| `TOOL_CALL_ARGS` | Tool arguments (streaming) |
| `TOOL_CALL_END` | Tool invocation ends |
| `TOOL_CALL_RESULT` | Tool execution result |
| `STATE_SNAPSHOT` | Full state snapshot |
| `MESSAGES_SNAPSHOT` | Messages snapshot |

## Adding New Frameworks

1. Create a directory for your agent (e.g., `my_agent/`)
2. Implement the AG-UI endpoint:
   - POST `/agent` - Accept AG-UI requests, return SSE stream
   - GET `/health` - Return health status
3. Add to `start_all.sh` and `stop_all.sh`
4. Add to `AGENTS` dict in `test_agents.py`

### AG-UI Request Format

```json
{
  "thread_id": "string",
  "run_id": "string",
  "messages": [{"id": "string", "role": "user", "content": "string"}],
  "state": {},
  "tools": [],
  "context": [],
  "forwardedProps": {}
}
```

### AG-UI Response Format (SSE)

```
data: {"type": "RUN_STARTED", "thread_id": "...", "run_id": "..."}

data: {"type": "TEXT_MESSAGE_START", "message_id": "...", "role": "assistant"}

data: {"type": "TEXT_MESSAGE_CONTENT", "message_id": "...", "delta": "Hello"}

data: {"type": "TEXT_MESSAGE_END", "message_id": "..."}

data: {"type": "RUN_FINISHED", "thread_id": "...", "run_id": "..."}
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new frameworks
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Related Projects

- [AG-UI Protocol](https://docs.ag-ui.com/) - Official documentation
- [CopilotKit](https://github.com/CopilotKit/CopilotKit) - AG-UI creators
- [PydanticAI](https://github.com/pydantic/pydantic-ai) - Fast Python agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - LangChain's graph framework
- [Agno](https://github.com/agno-agi/agno) - Multi-agent orchestration

## Acknowledgments

- CopilotKit team for creating the AG-UI protocol
- All framework maintainers for their AG-UI integrations
- [Namastex Labs](https://github.com/namastexlabs) for sponsoring this benchmark

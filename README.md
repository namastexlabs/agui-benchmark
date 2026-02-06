# AG-UI Protocol Research Benchmark

> Comprehensive benchmark suite for the AG-UI (Agent-User Interaction) protocol across multiple AI agent frameworks. This is a research guide documenting protocol compliance, performance, and capabilities.

## What is AG-UI?

[AG-UI](https://docs.ag-ui.com/) is an open, lightweight, event-based protocol for agent-user interaction created by CopilotKit. It enables framework-agnostic communication between AI agents and user interfaces through Server-Sent Events (SSE).

## Research Goals

This benchmark provides rigorous testing and documentation of:

- **Protocol Compliance** - Which frameworks support which AG-UI events
- **Framework Capabilities** - What features each framework implements
- **Performance Characteristics** - Response times, throughput, tool calling
- **HITL Implementation** - How human-in-the-loop workflows work via the protocol

## Documentation Structure

### 📖 Core Reference
- **[AGUI Spec Reference](docs/research/AGUI-SPEC-REFERENCE.md)** - Complete specification of all 26 AG-UI protocol events
- **[Framework Capabilities](docs/research/FRAMEWORK-CAPABILITIES.md)** - Deep analysis of what each framework supports

### 🔬 Research Results
- **[HITL Validation Results](docs/research/HITL-VALIDATION-RESULTS.md)** - Testing human-in-the-loop implementation across frameworks
- **[Event Coverage Matrix](docs/reports/EVENT-COVERAGE-MATRIX.md)** - Which frameworks emit which events
- **[Framework Comparison](docs/reports/FRAMEWORK-COMPARISON-MATRIX.md)** - Performance and feature comparison
- **[Event Type Analysis](docs/reports/EVENT-TYPE-ANALYSIS.md)** - Event adoption statistics
- **[Benchmark Summary](docs/reports/BENCHMARK-SUMMARY.md)** - Overall statistics and rankings

### 📚 Guides
- **[Report Generation](docs/guides/REPORT-GENERATION-GUIDE.md)** - How to run benchmarks and auto-generate reports

## Frameworks Tested

This benchmark covers **26 agent implementations** across multiple frameworks:

**Multi-Model Frameworks** (Anthropic, OpenAI, Google):
- Agno, LangGraph, PydanticAI, LlamaIndex, Vercel AI SDK

**Single-Model Frameworks**:
- CrewAI (Anthropic), AG2 (OpenAI), Google ADK (Google)

**Raw LLM APIs** (baseline):
- Anthropic, OpenAI, Google Gemini

For detailed framework analysis, see [Framework Capabilities](docs/research/FRAMEWORK-CAPABILITIES.md).

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

## Key Findings

### HITL Implementation
We validated that human-in-the-loop workflows can be fully implemented using the AG-UI protocol's existing `TOOL_CALL_*` events, without requiring special HITL-specific events. See [HITL Validation Results](docs/research/HITL-VALIDATION-RESULTS.md).

### Protocol Coverage
The AG-UI specification defines **26 events** across 5 categories:
- **Lifecycle**: RUN_STARTED, RUN_FINISHED, RUN_ERROR
- **Text Messages**: TEXT_MESSAGE_START/CONTENT/END, THINKING_START/END, THINKING_TEXT_MESSAGE_*
- **Tool Calls**: TOOL_CALL_START/ARGS/END/RESULT
- **State**: STATE_SNAPSHOT, STATE_DELTA, MESSAGES_SNAPSHOT, ACTIVITY_SNAPSHOT, ACTIVITY_DELTA
- **Custom**: STEP_STARTED, STEP_FINISHED, RAW, CUSTOM

See [AGUI Spec Reference](docs/research/AGUI-SPEC-REFERENCE.md) for complete details.

## Benchmark Architecture

```
test_agents.py (Benchmark Runner)
    │
    ├─ Starts 26 agent implementations on various ports
    │
    └─ Runs 9 test scenarios per agent:
       • Simple prompt (no tools)
       • Tool calling (6 tools available)
       • Streaming performance
       • Error handling
       • State management
       └─ Collects AG-UI events, timing, tool calls
          Saves JSON results → generate_reports.py
                                     ↓
                          Auto-generates 4 markdown reports
```

## Related Resources

- **[AG-UI Protocol](https://docs.ag-ui.com/)** - Official specification
- **[CopilotKit](https://github.com/CopilotKit/CopilotKit)** - AG-UI creators
- Framework repositories:
  - [PydanticAI](https://github.com/pydantic/pydantic-ai)
  - [LangGraph](https://github.com/langchain-ai/langgraph)
  - [Agno](https://github.com/agno-agi/agno)
  - [LlamaIndex](https://github.com/run-llama/llama_index)
  - [Vercel AI SDK](https://github.com/vercel/ai)
  - [CrewAI](https://github.com/joaomdmoura/crewAI)
  - [AG2](https://github.com/ag2ai/ag2)

## License

MIT License - see [LICENSE](LICENSE) for details.

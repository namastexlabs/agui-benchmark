# AG-UI Benchmark Research Documentation

This directory contains the research findings, reference materials, and reports from the AG-UI Protocol Benchmark.

## 📖 Structure

### `/research/` - Reference Materials
Core research documentation on the AG-UI protocol and framework capabilities.

- **AGUI-SPEC-REFERENCE.md** - Complete specification of all 26 AG-UI protocol events
  - Event categories and descriptions
  - Framework support matrix
  - Adoption statistics

- **FRAMEWORK-CAPABILITIES.md** - Detailed analysis of what each framework supports
  - Feature comparison matrix
  - Streaming support analysis
  - Tool calling capabilities
  - Native vs wrapped AG-UI implementations

- **HITL-VALIDATION-RESULTS.md** - Human-in-the-loop implementation study
  - Validation methodology
  - Cross-framework HITL testing
  - Event flow analysis
  - Success/failure patterns

### `/reports/` - Auto-Generated Research Reports
Reports automatically generated from benchmark runs using `generate_reports.py`.

- **EVENT-COVERAGE-MATRIX.md** - 26 events × N frameworks matrix
  - Coverage statistics (high/medium/low adoption)
  - Event-by-event framework support

- **FRAMEWORK-COMPARISON-MATRIX.md** - Framework capabilities comparison
  - Performance metrics
  - Success rates
  - Feature support grid

- **EVENT-TYPE-ANALYSIS.md** - Event adoption breakdown
  - Coverage by event category
  - Adoption percentages

- **BENCHMARK-SUMMARY.md** - Overall statistics
  - Test count and success rates
  - Performance rankings
  - Coverage summary

### `/guides/` - How-To Guides
Procedural documentation for running benchmarks and generating reports.

- **REPORT-GENERATION-GUIDE.md** - Complete workflow for benchmarking
  - How to run the full benchmark
  - How to generate reports
  - Report interpretation guide

## 🔄 Workflow

```
1. Run benchmark → 2. Generate reports → 3. Review findings
   (609 tests)      (auto-generated)      (4 matrices + analysis)
   ↓                ↓                      ↓
test_agents.py     generate_reports.py   docs/reports/
JSON results       Parse & analyze        Markdown files
```

## 📊 Key Metrics Tracked

### Protocol Compliance
- Which AG-UI events are emitted by each framework
- Event adoption rates (% of frameworks supporting each event)
- Coverage by event category

### Performance
- Response time (median, min, max)
- Throughput (characters per second for streaming)
- Tool call latency
- Success rates

### Capabilities
- Native vs wrapped AG-UI implementation
- Streaming support
- Tool calling efficiency
- State management
- Multi-model support

## 🔍 Research Highlights

### HITL Implementation
The research validates that human-in-the-loop workflows can be fully implemented using existing AG-UI protocol events, specifically the `TOOL_CALL_*` family. No special HITL-specific events are needed.

### Protocol Coverage
Out of 26 specified AG-UI events:
- **Adopted**: Core lifecycle, text messaging, tool calling events
- **Emerging**: State/activity snapshots (some frameworks)
- **Unused**: THINKING events (specified but not adopted by frameworks)

### Framework Patterns
- **Multi-model support**: Agno, LangGraph, PydanticAI, LlamaIndex, Vercel
- **Single-model**: CrewAI, AG2, Google ADK
- **Raw API**: Direct Anthropic, OpenAI, Gemini implementations

## 📝 How to Use This Documentation

1. **New to AG-UI?** Start with [AGUI-SPEC-REFERENCE.md](research/AGUI-SPEC-REFERENCE.md)
2. **Comparing frameworks?** See [FRAMEWORK-CAPABILITIES.md](research/FRAMEWORK-CAPABILITIES.md)
3. **Want HITL details?** Read [HITL-VALIDATION-RESULTS.md](research/HITL-VALIDATION-RESULTS.md)
4. **Looking for current metrics?** Check the [reports/](reports/) directory
5. **Need to run a fresh benchmark?** Follow [REPORT-GENERATION-GUIDE.md](guides/REPORT-GENERATION-GUIDE.md)

# AG-UI Benchmark Runs

This directory contains detailed logs of each benchmark run, including full request/response data for replay and analysis.

## Directory Structure

```
benchmark-runs/
└── 20260205-223045/              # Timestamp of run
    ├── run-metadata.json         # Run configuration and metadata
    ├── summary.json              # Final results and rankings
    │
    ├── agno-anthropic/           # Per-agent results
    │   ├── run1-simple/          # Test run 1, "simple" prompt
    │   │   ├── request.json      # Input payload sent to agent
    │   │   ├── response.jsonl    # Streaming events (JSON Lines)
    │   │   └── metadata.json     # Test results, timing, metrics
    │   ├── run1-tool_time/       # Test run 1, "tool_time" prompt
    │   ├── run1-tool_calc/       # Test run 1, "tool_calc" prompt
    │   ├── run2-simple/          # Test run 2, "simple" prompt
    │   └── ...
    │
    ├── langgraph-anthropic/
    │   └── ...
    └── ... (all other agents)
```

## File Formats

### `request.json`
Complete input payload sent to the agent endpoint:
```json
{
  "thread_id": "test-thread-agno-anthropic",
  "run_id": "test-run-agno-anthropic-simple",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "Say hello..."
    }
  ],
  "state": {},
  "tools": [],
  "context": [],
  "forwardedProps": {}
}
```

### `response.jsonl`
Streaming AG-UI events in JSON Lines format (one event per line):
```jsonl
{"type":"RUN_STARTED","timestamp":1234567890}
{"type":"TEXT_MESSAGE_START","messageId":"msg-1"}
{"type":"TEXT_MESSAGE_CONTENT","delta":"Hello"}
{"type":"TEXT_MESSAGE_CONTENT","delta":" world"}
{"type":"TEXT_MESSAGE_END","messageId":"msg-1"}
{"type":"RUN_FINISHED","timestamp":1234567891}
```

Each line is a complete JSON object representing one SSE event (the "delta" in streaming).

### `metadata.json`
Test results and metrics:
```json
{
  "agent": "agno-anthropic",
  "run_number": 1,
  "prompt_type": "simple",
  "success": true,
  "timing": {
    "total_time_ms": 1234.56,
    "time_to_first_event_ms": 45.23,
    "time_to_first_content_ms": 67.89
  },
  "tools": {
    "tool_calls": 0
  },
  "response": {
    "chars": 42,
    "final_text": "Hello world"
  },
  "events": {
    "total_events": 6,
    "event_types": ["RUN_STARTED", "TEXT_MESSAGE_START", ...]
  }
}
```

### `summary.json`
Overall benchmark results, rankings, and comparisons across all agents.

## Replaying Tests

Use the `replay_test.py` utility to replay any saved test:

```bash
# Replay a specific test
python replay_test.py benchmark-runs/20260205-223045/agno-anthropic/run1-simple

# Replay and compare all runs for an agent
python replay_test.py benchmark-runs/20260205-223045/agno-anthropic

# Analyze a full benchmark run
python replay_test.py benchmark-runs/20260205-223045
```

## Use Cases

1. **Debugging**: Examine exact request/response for failed tests
2. **Comparison**: Compare streaming behavior across frameworks
3. **Replay**: Re-run tests without calling live APIs
4. **Analysis**: Build custom analytics on streaming patterns
5. **Documentation**: Show real examples of AG-UI events
6. **Testing**: Validate client implementations against real data

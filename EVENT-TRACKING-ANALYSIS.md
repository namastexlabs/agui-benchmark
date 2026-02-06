# 📊 AG-UI Event Tracking Analysis

## Current State: What We Track

### ✅ Currently Captured Metrics

**Timing Metrics:**
- `total_time_ms` - Total request duration
- `time_to_first_event_ms` - Time until first event received
- `time_to_first_content_ms` - Time until first TEXT_MESSAGE_CONTENT
- `time_to_complete_ms` - Time until RUN_FINISHED
- `tool_call_time_ms` - Total time spent in tool calls

**Response Metrics:**
- `chars` - Total character count in response
- `tokens_approx` - Approximate token count (chars / 4)
- `final_text` - Complete assembled response text

**Token Metrics:**
- `input_tokens` - Input tokens (when available)
- `output_tokens` - Output tokens (when available)
- `total_tokens` - Sum of input + output

**Tool Metrics:**
- `tool_calls` - Number of tool calls made

**Event Metrics:**
- `total_events` - Total number of events received
- `event_types` - List of unique event types seen

**Files Generated:**
- `request.json` - Original request payload
- `response.jsonl` - All streaming events (JSONL format)
- `metadata.json` - Test metrics and summary
- `summary.json` - Benchmark-wide statistics

---

## 📈 AG-UI Events We Receive

Based on benchmark run 20260206-014545 (609 tests across 26 agents):

| Event Type | Count | Purpose |
|------------|-------|---------|
| TEXT_MESSAGE_CONTENT | 12,117 | Streaming text deltas |
| RAW | 3,970 | Framework-specific raw events (LangGraph) |
| TEXT_MESSAGE_CHUNK | 2,257 | Alternative text streaming format |
| RUN_STARTED | 609 | Agent run initialization |
| RUN_FINISHED | 603 | Agent run completion |
| TEXT_MESSAGE_START | 533 | Message stream start |
| TEXT_MESSAGE_END | 533 | Message stream end |
| TOOL_CALL_ARGS | 403 | Streaming tool call arguments |
| STATE_SNAPSHOT | 393 | Agent state checkpoints (LangGraph) |
| STEP_STARTED | 302 | Agent step/node start (LangGraph) |
| STEP_FINISHED | 301 | Agent step/node completion |
| MESSAGES_SNAPSHOT | 243 | Message history snapshot (CrewAI) |
| TOOL_CALL_START | 223 | Tool call initiated |
| TOOL_CALL_END | 223 | Tool call completed |
| TOOL_CALL_RESULT | 220 | Tool call result/output |
| TOOL_CALL_CHUNK | 36 | Streaming tool output (rare) |
| USAGE_METADATA | 24 | Token usage info (anthropic-raw) |
| RUN_ERROR | 18 | Error during execution |

---

## ❌ What We're NOT Tracking (But Should)

### 1. **Per-Event Timestamps** 🚨 CRITICAL GAP
**Problem:** Events in response.jsonl have NO timestamps
```json
{"type": "TEXT_MESSAGE_START"}  // ❌ No timestamp!
```

**Impact:**
- Can't measure time between events
- Can't identify slow steps in agent pipeline
- Can't profile streaming performance
- Can't detect event ordering issues

**Solution:** Add timestamp to every event when writing to JSONL
```json
{"type": "TEXT_MESSAGE_START", "timestamp": 1234567890.123, "offset_ms": 150.5}
```

---

### 2. **Event-Level Detailed Metrics**

**Missing Details:**
- **TOOL_CALL_START → TOOL_CALL_END:** Duration per tool call
- **STEP_STARTED → STEP_FINISHED:** Duration per step/node
- **TEXT_MESSAGE_START → TEXT_MESSAGE_END:** Time to stream complete message
- **RUN_STARTED → first TOOL_CALL_START:** Time to decision
- **TOOL_CALL_END → TOOL_CALL_RESULT:** Tool execution time

**Current:** We only track `tool_call_time_ms` as aggregate
**Need:** Per-tool-call breakdown with timing

---

### 3. **HITL (Human-in-the-Loop) Events** 🤔 NOT FOUND

**Expected AG-UI Events:**
```json
{"type": "HITL_PROMPT", "promptId": "...", "question": "..."}
{"type": "HITL_RESPONSE", "promptId": "...", "answer": "..."}
```

**Observation:** ZERO HITL events in 609 tests across all agents
**Reason:** Our test prompts don't trigger HITL scenarios

**Test Cases That Should Trigger HITL:**
- `hitl_approval` - Currently doesn't actually trigger HITL in most frameworks
- None of the agents are configured to prompt for human input

**Action Needed:**
1. Verify which frameworks support AG-UI HITL events
2. Create test scenarios that genuinely trigger HITL
3. Add HITL metrics (prompt count, response time, approval rate)

---

### 4. **Artifact Events** 📦 LIMITED COVERAGE

**Expected AG-UI Events:**
```json
{"type": "ARTIFACT_START", "artifactId": "...", "artifactType": "code"}
{"type": "ARTIFACT_CONTENT", "artifactId": "...", "delta": "..."}
{"type": "ARTIFACT_END", "artifactId": "..."}
```

**Observation:** Not seen in benchmark (agents may not be creating artifacts)

**Action Needed:**
- Add test prompts that request code generation, diagrams, etc.
- Track artifact creation rate, size, types

---

### 5. **Streaming Performance Metrics**

**Missing:**
- Throughput (chars/sec, tokens/sec)
- Latency distribution (p50, p95, p99)
- Stalls/pauses in streaming (gaps > 500ms between events)
- Time to interactive (first visible content)

**Current:** We only have aggregate times, not streaming quality

---

### 6. **Tool Call Deep Dive**

**What We Track:**
```json
{
  "tool_calls": 2,
  "tool_call_time_ms": 1500
}
```

**What We Should Track:**
```json
{
  "tool_calls": [
    {
      "name": "get_current_time",
      "args": {},
      "start_ms": 100,
      "args_complete_ms": 120,
      "end_ms": 150,
      "result_ms": 180,
      "duration_ms": 80,
      "execution_time_ms": 30,
      "success": true,
      "result": "2026-02-06 01:45:46"
    },
    {
      "name": "calculator",
      "args": {"expression": "2+2"},
      "start_ms": 200,
      "duration_ms": 50,
      "execution_time_ms": 20,
      "success": true,
      "result": "4"
    }
  ],
  "total_tool_time_ms": 130,
  "total_execution_time_ms": 50
}
```

---

### 7. **State/Memory Tracking**

**Current:** We see STATE_SNAPSHOT events but don't analyze them

**Should Track:**
- State size (bytes)
- State changes per step
- Memory accumulation over multi-turn conversations
- Message history growth

---

### 8. **Error Analytics**

**Current:** We track success/failure and error message

**Should Track:**
```json
{
  "errors": [
    {
      "type": "RUN_ERROR",
      "timestamp_ms": 1500,
      "code": "TOOL_EXECUTION_ERROR",
      "message": "Calculator failed",
      "recoverable": true,
      "retry_count": 0
    }
  ],
  "error_rate": 0.05,
  "error_recovery_time_ms": 500
}
```

---

### 9. **Multi-Turn Conversation Metrics**

**Test:** `multi_turn_memory`

**Missing Metrics:**
- Turn-by-turn timing
- Context retention accuracy
- Memory recall success rate
- Latency increase per turn

---

### 10. **Framework-Specific Events**

**LangGraph:**
- `RAW` events contain rich data we're not parsing
- Step-level profiling available
- Graph execution path tracking

**CrewAI:**
- `MESSAGES_SNAPSHOT` pattern differs from standard AG-UI
- Not extracting agent-to-agent communication

**Need:** Framework-specific metric extraction

---

## 🎯 Priority Gaps to Fix

### P0: Critical (Blocking Better Analysis)

1. **Add timestamps to every event** - Can't do time-based analysis without this
   - Add `timestamp` (Unix timestamp with milliseconds)
   - Add `offset_ms` (milliseconds since RUN_STARTED)

2. **Per-tool-call timing breakdown** - Essential for tool performance analysis
   - Track each tool individually
   - Measure execution time vs overhead

### P1: High Priority (Major Insights)

3. **Streaming performance metrics**
   - Throughput (tokens/sec)
   - Latency percentiles
   - Streaming quality (gaps/stalls)

4. **Event sequence analysis**
   - Time between events
   - Event order validation
   - Pipeline bottlenecks

### P2: Important (Completeness)

5. **HITL testing and metrics** - Need proper test cases first
6. **Artifact tracking** - Need test cases that generate artifacts
7. **State/memory analytics** - Parse STATE_SNAPSHOT events
8. **Error recovery metrics** - Track retry behavior

### P3: Nice to Have

9. **Multi-turn analytics** - Per-turn breakdown
10. **Framework-specific deep dives** - Parse RAW events

---

## 📋 Implementation Plan

### Phase 1: Core Event Tracking (1-2 hours)

**Add timestamps and enhanced event logging:**

```python
# In test_agents.py, event processing loop:
import time

start_time = time.time()
event_log = []

async for event in ...:
    current_time = time.time()
    timestamp_ms = current_time * 1000
    offset_ms = (current_time - start_time) * 1000

    # Add timing to event before saving
    event_with_timing = {
        **event,
        "_timestamp": timestamp_ms,
        "_offset_ms": offset_ms
    }

    event_log.append(event_with_timing)
    # Write to JSONL with timing
```

**Enhanced tool call tracking:**
```python
@dataclass
class ToolCallMetrics:
    name: str
    start_ms: float
    args_complete_ms: float = 0
    end_ms: float = 0
    result_ms: float = 0
    success: bool = False
    result: str = ""

    @property
    def duration_ms(self):
        return self.result_ms - self.start_ms

    @property
    def execution_time_ms(self):
        return self.result_ms - self.end_ms

# Track list of ToolCallMetrics
metrics.tool_calls_detail: List[ToolCallMetrics] = []
```

---

### Phase 2: Streaming Analytics (2-3 hours)

**Calculate streaming metrics from timestamped events:**

```python
def calculate_streaming_metrics(events):
    text_events = [e for e in events if e['type'] == 'TEXT_MESSAGE_CONTENT']

    if len(text_events) < 2:
        return {}

    # Calculate gaps between text chunks
    gaps = []
    for i in range(1, len(text_events)):
        gap_ms = text_events[i]['_offset_ms'] - text_events[i-1]['_offset_ms']
        gaps.append(gap_ms)

    # Identify stalls (gaps > 500ms)
    stalls = [g for g in gaps if g > 500]

    # Calculate throughput
    total_chars = sum(len(e.get('delta', '')) for e in text_events)
    duration_s = (text_events[-1]['_offset_ms'] - text_events[0]['_offset_ms']) / 1000
    throughput_cps = total_chars / duration_s if duration_s > 0 else 0

    return {
        "streaming": {
            "throughput_chars_per_sec": throughput_cps,
            "avg_gap_ms": statistics.mean(gaps),
            "p95_gap_ms": statistics.quantiles(gaps, n=20)[18] if len(gaps) > 20 else max(gaps),
            "stalls": len(stalls),
            "stall_time_ms": sum(stalls)
        }
    }
```

---

### Phase 3: Enhanced Reports (1-2 hours)

**Add new analysis sections:**

1. **Streaming Quality Report**
   ```
   📊 STREAMING PERFORMANCE
   Agent                Throughput    Avg Gap    P95 Gap    Stalls
   ----------------------------------------------------------------
   agno-cerebras        1200 c/s      8ms        15ms       0
   langgraph-anthropic  450 c/s       22ms       89ms       2
   ```

2. **Tool Performance Report**
   ```
   🔧 TOOL PERFORMANCE
   Tool                 Calls    Avg Exec    P95        Success Rate
   -------------------------------------------------------------------
   get_current_time     156      12ms        18ms       100%
   calculator           145      8ms         15ms       98.6%
   ```

3. **Event Pipeline Report**
   ```
   ⚡ EVENT PIPELINE TIMING
   Agent                Decision    Execution    Streaming    Total
   -------------------------------------------------------------------
   agno-cerebras        50ms        80ms         120ms        250ms
   (RUN_START→TOOL)    (TOOL→END)  (TEXT stream)
   ```

---

## 🧪 Test Case Improvements

### Add HITL Tests
```python
PROMPTS = {
    "hitl_real": "Generate a delete_database() function. IMPORTANT: Ask for my approval before proceeding.",
    "hitl_dangerous": "I want to delete all my production data. Please ask for confirmation first.",
}
```

### Add Artifact Tests
```python
PROMPTS = {
    "artifact_code": "Write a Python function to calculate fibonacci numbers. Return it as a code artifact.",
    "artifact_diagram": "Create a mermaid diagram showing the authentication flow.",
}
```

---

## 📊 Expected Improvements

**Current State:**
- Basic timing (4 metrics)
- Aggregate tool stats (2 metrics)
- Event counts (2 metrics)
- **~8 data points per test**

**After Phase 1:**
- Timestamped events
- Per-tool breakdown (6+ metrics per tool)
- Per-event timing
- **~30 data points per test**

**After Phase 2:**
- Streaming analytics (8 metrics)
- Pipeline profiling (10+ metrics)
- Percentile analysis
- **~50 data points per test**

**After Phase 3:**
- Comprehensive reports
- Framework comparisons
- Performance recommendations
- **Publication-ready analysis**

---

## 🚀 Quick Win: Phase 1 Implementation

Most impactful change with least effort: **Add timestamps**

```bash
# Before:
{"type": "TOOL_CALL_START", "toolCallId": "123", "toolCallName": "calculator"}

# After:
{"type": "TOOL_CALL_START", "toolCallId": "123", "toolCallName": "calculator", "_timestamp": 1707180346150.5, "_offset_ms": 150.5}
```

This single change unlocks:
- Time between events
- Event sequence validation
- Pipeline bottleneck identification
- Streaming performance analysis
- Tool execution timing

**ROI: 30 minutes of implementation → 10x better insights**

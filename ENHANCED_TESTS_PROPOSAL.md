# AG-UI Comprehensive Test Suite Proposal

## Current State (What We Test Now)

✅ **Basic Streaming**: `TEXT_MESSAGE_CONTENT` deltas
✅ **Tool Calling**: Single tool, sequential
✅ **Lifecycle Events**: `RUN_STARTED`, `RUN_FINISHED`

## Proposed Enhancements

### **1. Extended Test Prompts**

```python
TEST_PROMPTS = {
    # === CURRENT (Keep) ===
    "simple": "Say hello and introduce yourself briefly in 2-3 sentences.",
    "tool_time": "What is the current time? Use the time tool to check.",
    "tool_calc": "Calculate 42 * 17 using the calculator tool and tell me the result.",

    # === NEW: Thinking/Reasoning ===
    "thinking": "Think step-by-step: how would you solve the equation 2x + 5 = 13? Show your reasoning.",
    "planning": "Plan a simple breakfast menu for 2 people. List your thought process.",

    # === NEW: Multi-turn Conversation ===
    "memory": [
        {"content": "My favorite programming language is Python."},
        {"content": "What's my favorite programming language?"}
    ],
    "context": [
        {"content": "I work as a software engineer at Anthropic."},
        {"content": "Where do I work?"}
    ],

    # === NEW: Complex Tool Use ===
    "multi_tool": "What's the current time, and then calculate 42 * 17?",
    "parallel_tools": "Check the time in UTC and calculate 100 + 200 simultaneously.",
    "nested_tools": "Get the current time, then calculate how many hours until midnight.",

    # === NEW: Artifacts (if supported) ===
    "code_artifact": "Create a Python function to calculate factorial of a number.",
    "markdown_artifact": "Write a simple README.md for a todo app.",

    # === NEW: State Management ===
    "state_update": "Remember that my user_id is 12345. Confirm you've saved it.",
    "state_retrieve": "What's my user_id?",

    # === NEW: Error Handling ===
    "missing_tool": "Use the 'nonexistent_tool' to do something.",
    "invalid_input": "Calculate the time of 'banana' (intentionally nonsensical).",

    # === NEW: Edge Cases ===
    "empty_response": "Respond with nothing. Just silence.",
    "very_long": "Write a 500-word essay about AI.",
    "rapid_fire": "Answer: 1+1, 2+2, 3+3, 4+4, 5+5",

    # === NEW: Human-in-the-Loop (HITL) ===
    "hitl_approval": "I need to delete important data. Ask for my approval first.",
    "hitl_input": "Ask me what my favorite color is, then tell me about it.",
}
```

---

## **2. AG-UI Event Coverage Matrix**

### **Tier 1: Essential Events (Current)**
| Event | Tested? | Test Type |
|-------|---------|-----------|
| `RUN_STARTED` | ✅ | All tests |
| `RUN_FINISHED` | ✅ | All tests |
| `TEXT_MESSAGE_START` | ✅ | simple, tool_* |
| `TEXT_MESSAGE_CONTENT` | ✅ | simple, tool_* |
| `TEXT_MESSAGE_END` | ✅ | simple, tool_* |
| `TOOL_CALL_START` | ✅ | tool_time, tool_calc |
| `TOOL_CALL_ARGS` | ✅ | tool_time, tool_calc |
| `TOOL_CALL_END` | ✅ | tool_time, tool_calc |
| `TOOL_CALL_RESULT` | ✅ | tool_time, tool_calc |

### **Tier 2: Advanced Events (Missing)**
| Event | Tested? | Proposed Test |
|-------|---------|---------------|
| `THINKING_START` | ❌ | thinking, planning |
| `THINKING_CONTENT` | ❌ | thinking, planning |
| `THINKING_END` | ❌ | thinking, planning |
| `ARTIFACT_START` | ❌ | code_artifact, markdown_artifact |
| `ARTIFACT_CONTENT` | ❌ | code_artifact, markdown_artifact |
| `ARTIFACT_END` | ❌ | code_artifact, markdown_artifact |
| `STATE_SNAPSHOT` | ⚠️ | Partial (CrewAI only) |
| `MESSAGES_SNAPSHOT` | ⚠️ | Partial (CrewAI only) |
| `HUMAN_INPUT_REQUESTED` | ❌ | hitl_approval, hitl_input |
| `HUMAN_INPUT_RECEIVED` | ❌ | hitl_approval, hitl_input |
| `ERROR` | ❌ | missing_tool, invalid_input |

### **Tier 3: Extended Events (Framework-specific)**
| Event | Purpose | Frameworks |
|-------|---------|-----------|
| `PROGRESS_UPDATE` | Long-running tasks | CrewAI, AG2 |
| `AGENT_SWITCH` | Multi-agent handoff | CrewAI, AG2 |
| `RATE_LIMIT` | API throttling | All |
| `COST_UPDATE` | Token usage tracking | All |

---

## **3. Human-in-the-Loop (HITL) Testing Strategy**

### **Option A: Mock HITL (Automated)**
Simulate user responses with pre-configured answers:

```python
HITL_RESPONSES = {
    "hitl_approval": {
        "trigger": "HUMAN_INPUT_REQUESTED",
        "response": {"approved": True, "message": "Yes, proceed"},
        "timeout_ms": 1000  # Auto-respond after 1s
    },
    "hitl_input": {
        "trigger": "HUMAN_INPUT_REQUESTED",
        "response": {"input": "My favorite color is blue"},
        "timeout_ms": 500
    }
}
```

### **Option B: Record-Replay HITL**
1. Record a real HITL session manually
2. Save the request/response sequence
3. Replay it in tests with pre-recorded answers

### **Option C: Emulated HITL Server**
Create a mock user that responds programmatically:

```python
class MockUser:
    def on_approval_request(self, message: str) -> bool:
        # Approve if message contains "data"
        return "data" in message.lower()

    def on_input_request(self, question: str) -> str:
        # Answer based on question keywords
        if "color" in question:
            return "blue"
        if "name" in question:
            return "Alice"
        return "I don't know"
```

---

## **4. Framework Capability Matrix**

Not all frameworks support all features. Track what each supports:

| Framework | Tools | Thinking | Artifacts | HITL | Multi-turn | State |
|-----------|-------|----------|-----------|------|------------|-------|
| Agno | ✅ | ? | ? | ? | ✅ | ✅ |
| LangGraph | ✅ | ? | ? | ? | ✅ | ✅ |
| PydanticAI | ✅ | ? | ? | ? | ✅ | ✅ |
| LlamaIndex | ✅ | ? | ? | ? | ✅ | ✅ |
| CrewAI | ✅ | ✅ | ? | ✅ | ✅ | ✅ |
| AG2 | ✅ | ✅ | ? | ✅ | ✅ | ✅ |
| Vercel AI | ✅ | ✅ | ✅ | ? | ✅ | ✅ |
| Google ADK | ✅ | ✅ | ? | ? | ✅ | ✅ |

*(? = needs research)*

---

## **5. Implementation Plan**

### **Phase 1: Extended Basic Tests** (Quick wins)
- Add multi-turn conversation tests
- Add parallel tool calling tests
- Add error handling tests

### **Phase 2: Advanced Features** (Medium effort)
- Thinking/reasoning tests (if frameworks support)
- State management tests
- Artifact creation tests

### **Phase 3: HITL Emulation** (Complex)
- Design mock HITL system
- Implement automated response handlers
- Test HITL-capable frameworks (CrewAI, AG2)

### **Phase 4: Stress Testing** (Performance)
- Very long responses
- Rapid-fire tool calls
- Concurrent requests
- Token limit edge cases

---

## **6. Metrics to Track (Beyond Current)**

Current metrics:
- Total time, TTFB, TTFC
- Tool call count
- Response length

**Add:**
- Thinking time (time spent in reasoning)
- Artifact generation time
- HITL response latency
- State update frequency
- Error recovery success rate
- Multi-turn context retention accuracy
- Parallel tool concurrency level
- Token efficiency (response quality per token)

---

## **7. Expected Outcomes**

After implementing these enhancements:

✅ **Complete AG-UI Coverage**: Test all event types
✅ **Framework Differentiation**: See which frameworks support advanced features
✅ **Real-world Patterns**: Test actual use cases (multi-turn, HITL, artifacts)
✅ **Better Benchmarking**: Compare frameworks on more dimensions
✅ **Documentation**: Show comprehensive AG-UI examples
✅ **Debugging**: Capture edge cases and failures

---

## **Example: Enhanced Test Result**

```
🧪 Extended Test Results

THINKING TESTS:
  ✅ agno-anthropic: thinking events detected (3 steps, 245ms)
  ❌ langgraph-anthropic: no THINKING events (uses TEXT_MESSAGE only)
  ✅ vercel-openai: thinking via tool_use pattern

ARTIFACT TESTS:
  ✅ vercel-anthropic: ARTIFACT_START/CONTENT/END detected
  ❌ agno-anthropic: artifacts rendered as text

HITL TESTS:
  ✅ crewai: HUMAN_INPUT_REQUESTED after 1.2s
  ⚠️ ag2: timeout waiting for HITL event
  ❌ pydantic-ai: HITL not supported

MULTI-TURN TESTS:
  ✅ All frameworks: context retained (9/9)
  ⚠️ openai-raw: context forgotten after 3 turns

PARALLEL TOOLS:
  ✅ vercel-openai: 2 tools called concurrently
  ❌ most frameworks: sequential execution only
```

---

## **Next Steps**

1. Research which frameworks support which advanced features
2. Implement Phase 1 tests (multi-turn, errors)
3. Design HITL mock system
4. Extend TestMetrics dataclass for new metrics
5. Update reporting to show feature compatibility matrix

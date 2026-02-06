# 🎯 AG-UI Protocol Event Reference

**Source:** `ag_ui.core.events` v0.1.10
**Total Events:** 26
**Last Updated:** 2026-02-06

---

## 📋 Complete Event List

### Core Lifecycle (3 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `RUN_STARTED` | Run initiation | ✅ 99.7% coverage |
| `RUN_FINISHED` | Run completion | ✅ 98.7% coverage |
| `RUN_ERROR` | Run error | ✅ 3.0% coverage (errors only) |

---

### Text Streaming (4 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `TEXT_MESSAGE_START` | Message start | ✅ 81.3% coverage |
| `TEXT_MESSAGE_CONTENT` | Streaming text delta | ✅ 75.9% coverage |
| `TEXT_MESSAGE_END` | Message end | ✅ 81.3% coverage |
| `TEXT_MESSAGE_CHUNK` | Alternative chunk format | ✅ 11.3% coverage (LlamaIndex) |

---

### Thinking/Reasoning (5 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `THINKING_START` | Thinking step start | ❌ 0% - Not emitted |
| `THINKING_END` | Thinking step end | ❌ 0% - Not emitted |
| `THINKING_TEXT_MESSAGE_START` | Thinking text start | ❌ 0% - Not emitted |
| `THINKING_TEXT_MESSAGE_CONTENT` | Thinking text delta | ❌ 0% - Not emitted |
| `THINKING_TEXT_MESSAGE_END` | Thinking text end | ❌ 0% - Not emitted |

**Use Cases:**
- Claude extended thinking
- OpenAI o1/o3 reasoning
- Multi-step agent planning
- Exposing reasoning process

---

### Tool Calling (5 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `TOOL_CALL_START` | Tool call initiation | ✅ 29.7% coverage |
| `TOOL_CALL_ARGS` | Tool arguments (streaming) | ✅ 27.1% coverage |
| `TOOL_CALL_END` | Tool call end | ✅ 29.7% coverage |
| `TOOL_CALL_CHUNK` | Alternative chunk format | ✅ 4.4% coverage (LlamaIndex) |
| `TOOL_CALL_RESULT` | Tool execution result | ✅ 29.9% coverage |

---

### State Management (5 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `STATE_SNAPSHOT` | Complete state | ✅ 29.1% coverage (LangGraph, CrewAI, LlamaIndex) |
| `STATE_DELTA` | State patch (JSON Patch RFC 6902) | ❌ 0% - Not used |
| `MESSAGES_SNAPSHOT` | Message history | ✅ 29.1% coverage (CrewAI, LlamaIndex) |
| `ACTIVITY_SNAPSHOT` | Activity message (rich content) | ❌ 0% - Not used |
| `ACTIVITY_DELTA` | Activity patch | ❌ 0% - Not used |

**Notes:**
- `STATE_DELTA` could improve efficiency for large states
- `ACTIVITY_SNAPSHOT` designed for rich content (artifacts, diagrams)

---

### Steps/Nodes (2 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `STEP_STARTED` | Agent step start | ✅ 16.1% coverage (LangGraph, CrewAI) |
| `STEP_FINISHED` | Agent step end | ✅ 17.2% coverage (LangGraph, CrewAI) |

---

### Framework-Specific (2 events)
| Event | Purpose | Status in Benchmark |
|-------|---------|-------------------|
| `RAW` | Framework raw event | ✅ 13.8% coverage (LangGraph only) |
| `CUSTOM` | Custom event type | ❌ 0% - Not used |

**Note:** `CUSTOM` allows frameworks to add proprietary events while maintaining AG-UI compatibility.

---

## 📊 Coverage Summary

### By Category

| Category | Events in Spec | Captured | Coverage |
|----------|---------------|----------|----------|
| Core Lifecycle | 3 | 3 | 100% ✅ |
| Text Streaming | 4 | 4 | 100% ✅ |
| Thinking | 5 | 0 | 0% ❌ |
| Tool Calling | 5 | 5 | 100% ✅ |
| State Management | 5 | 2 | 40% ⚠️ |
| Steps | 2 | 2 | 100% ✅ |
| Framework | 2 | 1 | 50% ⚠️ |
| **TOTAL** | **26** | **18** | **69.2%** |

### By Adoption

**Universal (95%+ of frameworks):**
- RUN_STARTED, RUN_FINISHED
- TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END

**Common (25%+ of frameworks):**
- TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_CALL_RESULT
- STATE_SNAPSHOT, MESSAGES_SNAPSHOT

**Rare (5-25% of frameworks):**
- STEP_STARTED, STEP_FINISHED
- RAW
- TEXT_MESSAGE_CHUNK, TOOL_CALL_CHUNK

**Never Used (0%):**
- THINKING_* (all 5 events)
- ACTIVITY_* (2 events)
- STATE_DELTA
- CUSTOM

---

## ⚠️ Events NOT in Spec

These events are commonly expected but NOT defined in AG-UI protocol:

### HITL (Human-in-the-Loop)
- ❌ No HITL_PROMPT
- ❌ No HITL_RESPONSE
- ❌ No HITL_REQUEST
- ❌ No HITL_RESULT

**Workaround:** Use CUSTOM events or propose spec addition

### USAGE_METADATA
- ❌ Not in spec
- ✅ anthropic-raw added as custom event
- 💡 Should be standardized for production use

**Includes:**
- Token counts (input/output)
- Costs
- Cache statistics
- Model information

---

## 🎯 Event Patterns

### Standard Streaming Pattern
```
RUN_STARTED
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT (delta 1)
TEXT_MESSAGE_CONTENT (delta 2)
...
TEXT_MESSAGE_END
RUN_FINISHED
```
**Used by:** Most frameworks (18/26 agents)

---

### Tool Calling Pattern
```
RUN_STARTED
TOOL_CALL_START
TOOL_CALL_ARGS (args streaming)
TOOL_CALL_END
TOOL_CALL_RESULT
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT
TEXT_MESSAGE_END
RUN_FINISHED
```
**Used by:** 10/26 agents

---

### State Management Pattern
```
RUN_STARTED
STATE_SNAPSHOT (initial state)
STEP_STARTED
... (work happens)
STEP_FINISHED
STATE_SNAPSHOT (updated state)
MESSAGES_SNAPSHOT (updated messages)
RUN_FINISHED
```
**Used by:** LangGraph, CrewAI, LlamaIndex

---

### Thinking Pattern (NOT IMPLEMENTED YET)
```
RUN_STARTED
THINKING_START
THINKING_TEXT_MESSAGE_START
THINKING_TEXT_MESSAGE_CONTENT (reasoning delta)
THINKING_TEXT_MESSAGE_CONTENT (reasoning delta)
...
THINKING_TEXT_MESSAGE_END
THINKING_END
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT (final response)
TEXT_MESSAGE_END
RUN_FINISHED
```
**Used by:** ZERO frameworks (but spec defines it!)

---

## 🔗 Framework Support Matrix

### Full Event Support (10+ event types)
- **LangGraph** - 13 events (best observability)
- **Anthropic Raw** - 10 events (includes USAGE_METADATA)

### Good Support (9 event types)
- **Agno** (all models)
- **PydanticAI** (all models)
- **Vercel AI SDK** (all models)
- **OpenAI Raw**
- **Gemini Raw**

### Moderate Support (6-8 events)
- **LlamaIndex** - 8 events (alternative CHUNK pattern)
- **CrewAI** - 7 events (MESSAGES_SNAPSHOT pattern)
- **AG2** - 6 events
- **Google ADK** - 6 events

### Basic Support (5 events)
- **Cerebras** - 5 events (core + text only)

---

## 💡 Implementation Notes

### For Framework Developers

**Minimum Viable Implementation:**
```python
# Core lifecycle (required)
emit(RUN_STARTED)
# ... do work ...
emit(RUN_FINISHED)
```

**Standard Streaming:**
```python
emit(RUN_STARTED)
emit(TEXT_MESSAGE_START)
for chunk in stream:
    emit(TEXT_MESSAGE_CONTENT, content=chunk)
emit(TEXT_MESSAGE_END)
emit(RUN_FINISHED)
```

**With Tools:**
```python
emit(RUN_STARTED)
emit(TOOL_CALL_START, toolCallId=id, toolCallName=name)
emit(TOOL_CALL_ARGS, toolCallId=id, args=args)
emit(TOOL_CALL_END, toolCallId=id)
result = execute_tool()
emit(TOOL_CALL_RESULT, toolCallId=id, result=result)
emit(TEXT_MESSAGE_START)
# ... stream response ...
emit(TEXT_MESSAGE_END)
emit(RUN_FINISHED)
```

**With Thinking (proposed):**
```python
emit(RUN_STARTED)
emit(THINKING_START)
emit(THINKING_TEXT_MESSAGE_START)
for reasoning_chunk in thinking_stream:
    emit(THINKING_TEXT_MESSAGE_CONTENT, content=reasoning_chunk)
emit(THINKING_TEXT_MESSAGE_END)
emit(THINKING_END)
# ... then emit regular text response ...
emit(RUN_FINISHED)
```

---

## 📚 References

- **Spec Location:** `.venv/lib/python3.12/site-packages/ag_ui/core/events.py`
- **Version:** v0.1.10
- **Benchmark Data:** `benchmark-runs/20260206-015725/`
- **Related Docs:**
  - `AGUI-SPEC-COMPLIANCE.md` - Full compliance analysis
  - `EVENT-COVERAGE-REPORT.md` - Detailed coverage report
  - `FRAMEWORK-CAPABILITIES.md` - Framework comparison

---

**Last Updated:** 2026-02-06
**Verified Against:** ag_ui.core.events v0.1.10

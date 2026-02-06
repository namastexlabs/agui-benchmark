# 🎯 AG-UI Event Coverage Report

**Benchmark:** 20260206-015725
**Tests:** 609 across 26 agents
**Test Types:** 9 (simple, tool_time, tool_calc, multi_tool, thinking, artifact, hitl_approval, error_handling, multi_turn_memory)

---

## 🚨 CRITICAL FINDINGS

### ❌ Missing Event Types (Expected but NEVER Captured)

| Event Type | Status | Impact |
|------------|--------|--------|
| **HITL_PROMPT** | ❌ NEVER emitted | No frameworks emit HITL events |
| **HITL_RESPONSE** | ❌ NEVER emitted | Human-in-loop not observable |
| **HITL_REQUEST** | ❌ NEVER emitted | Test runs but no events |
| **HITL_RESULT** | ❌ NEVER emitted | |
| **ARTIFACT_START** | ❌ NEVER emitted | No frameworks emit artifact events |
| **ARTIFACT_CONTENT** | ❌ NEVER emitted | Artifacts not observable |
| **ARTIFACT_END** | ❌ NEVER emitted | Test runs but no events |
| **THINKING_START** | ❌ NEVER emitted | No frameworks emit thinking events |
| **THINKING_CONTENT** | ❌ NEVER emitted | Reasoning not observable |
| **THINKING_END** | ❌ NEVER emitted | Test runs but no events |

**Analysis:** We run `hitl_approval`, `artifact`, and `thinking` tests, but frameworks treat them as regular text responses without specialized AG-UI events!

---

## ✅ Events Successfully Captured

| Event Type | Occurrences | Coverage | Frameworks Supporting |
|------------|-------------|----------|----------------------|
| **RUN_STARTED** | 607/609 | 99.7% | All except 2 failures |
| **RUN_FINISHED** | 601/609 | 98.7% | All except 8 failures |
| **TEXT_MESSAGE_START** | 495/609 | 81.3% | 20/26 agents |
| **TEXT_MESSAGE_CONTENT** | 462/609 | 75.9% | 18/26 agents |
| **TEXT_MESSAGE_END** | 495/609 | 81.3% | 20/26 agents |
| **TOOL_CALL_START** | 181/609 | 29.7% | 10/26 agents |
| **TOOL_CALL_ARGS** | 165/609 | 27.1% | 9/26 agents |
| **TOOL_CALL_END** | 181/609 | 29.7% | 10/26 agents |
| **TOOL_CALL_RESULT** | 182/609 | 29.9% | 10/26 agents |
| **MESSAGES_SNAPSHOT** | 177/609 | 29.1% | CrewAI, LlamaIndex (alternative pattern) |
| **STATE_SNAPSHOT** | 177/609 | 29.1% | LangGraph, CrewAI, LlamaIndex |
| **STEP_STARTED** | 98/609 | 16.1% | LangGraph, CrewAI |
| **STEP_FINISHED** | 105/609 | 17.2% | LangGraph, CrewAI |
| **RAW** | 84/609 | 13.8% | LangGraph only |
| **TEXT_MESSAGE_CHUNK** | 69/609 | 11.3% | LlamaIndex (alternative) |
| **TOOL_CALL_CHUNK** | 27/609 | 4.4% | LlamaIndex (alternative) |
| **USAGE_METADATA** | 24/609 | 3.9% | anthropic-raw only |
| **RUN_ERROR** | 18/609 | 3.0% | 8 failures across all agents |

---

## 📊 COMPREHENSIVE EVENT MATRIX

### All Frameworks × All Event Types

| Event Type | ag2 | agno-anthropic | agno-cerebras | agno-gemini | agno-openai | anthropic-raw | cerebras-llama-3.1 | cerebras-llama-3.3 | crewai | gemini-raw | google-adk | langgraph-anthropic | langgraph-cerebras | langgraph-gemini | langgraph-openai | llamaindex-anthropic | llamaindex-gemini | llamaindex-openai | openai-raw | pydantic-anthropic | pydantic-gemini | pydantic-openai | vercel-anthropic | vercel-gemini | vercel-openai |
|------------|-----|----------------|---------------|-------------|-------------|---------------|-------------------|-------------------|--------|------------|------------|---------------------|-------------------|------------------|------------------|---------------------|------------------|------------------|------------|-------------------|----------------|----------------|-----------------|--------------|--------------|
| **RUN_STARTED** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RUN_FINISHED** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RUN_ERROR** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **TEXT_MESSAGE_START** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TEXT_MESSAGE_CONTENT** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TEXT_MESSAGE_END** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TEXT_MESSAGE_CHUNK** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **TOOL_CALL_START** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_ARGS** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_END** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_RESULT** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_CHUNK** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **STATE_SNAPSHOT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MESSAGES_SNAPSHOT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **STEP_STARTED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **STEP_FINISHED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **RAW** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **USAGE_METADATA** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **HITL_PROMPT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **ARTIFACT_START** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **THINKING_START** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🧪 TEST TYPE × EVENT MATRIX

Shows which events are captured during each test type:

| Test Type | TEXT_MESSAGE | TOOL_CALL | STATE | HITL | ARTIFACT | THINKING | USAGE | Notes |
|-----------|--------------|-----------|-------|------|----------|----------|-------|-------|
| **simple** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | Basic text generation |
| **tool_time** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | Tools work correctly |
| **tool_calc** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | Tools work correctly |
| **multi_tool** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | Multiple tools work |
| **thinking** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ⚠️ No THINKING events! |
| **artifact** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ⚠️ No ARTIFACT events! |
| **hitl_approval** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ⚠️ No HITL events! |
| **error_handling** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | Standard error responses |
| **multi_turn_memory** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ Most tests fail! |

---

## 📈 Event Coverage by Category

### Core Lifecycle Events
- ✅ **RUN_STARTED**: 99.7% coverage (607/609)
- ✅ **RUN_FINISHED**: 98.7% coverage (601/609)
- ✅ **RUN_ERROR**: 3.0% coverage (18/609) - only on actual errors

**Status:** ✅ EXCELLENT - All frameworks support core lifecycle

---

### Text Streaming Events
- ✅ **TEXT_MESSAGE_START**: 81.3% coverage (495/609)
- ✅ **TEXT_MESSAGE_CONTENT**: 75.9% coverage (462/609)
- ✅ **TEXT_MESSAGE_END**: 81.3% coverage (495/609)
- ⚠️ **TEXT_MESSAGE_CHUNK**: 11.3% coverage (69/609) - LlamaIndex only

**Status:** ✅ GOOD - Standard streaming well-supported
**Gap:** CrewAI and LlamaIndex use MESSAGES_SNAPSHOT instead

---

### Tool Calling Events
- ✅ **TOOL_CALL_START**: 29.7% coverage (181/609)
- ✅ **TOOL_CALL_ARGS**: 27.1% coverage (165/609)
- ✅ **TOOL_CALL_END**: 29.7% coverage (181/609)
- ✅ **TOOL_CALL_RESULT**: 29.9% coverage (182/609)
- ⚠️ **TOOL_CALL_CHUNK**: 4.4% coverage (27/609) - LlamaIndex only

**Status:** ✅ GOOD - 10/26 agents support tool events
**Gap:** Cerebras, Google ADK, AG2, CrewAI don't support tools

---

### State Management Events
- ✅ **STATE_SNAPSHOT**: 29.1% coverage (177/609)
- ✅ **MESSAGES_SNAPSHOT**: 29.1% coverage (177/609)
- ✅ **STEP_STARTED**: 16.1% coverage (98/609)
- ✅ **STEP_FINISHED**: 17.2% coverage (105/609)

**Status:** ⚠️ MODERATE - Only 3 frameworks (LangGraph, CrewAI, LlamaIndex)
**Gap:** Most frameworks don't expose state

---

### Observability Events
- ✅ **RAW**: 13.8% coverage (84/609) - LangGraph only
- ⚠️ **USAGE_METADATA**: 3.9% coverage (24/609) - anthropic-raw only

**Status:** ❌ POOR - Minimal observability
**Critical Gap:** Only 1 framework tracks tokens!

---

### Advanced Events (NEVER Captured)
- ❌ **HITL_PROMPT/RESPONSE**: 0% coverage
- ❌ **ARTIFACT_START/CONTENT/END**: 0% coverage
- ❌ **THINKING_START/CONTENT/END**: 0% coverage

**Status:** ❌ NOT SUPPORTED - No frameworks emit these
**Impact:** Cannot observe HITL, artifacts, or reasoning

---

## 🔍 Framework Event Support Summary

### Full AG-UI Compliance (12+ event types)
1. **LangGraph** - 13 event types
   - Core, Text, Tools, State, Steps, RAW
   - Best observability

2. **Agno (Claude/Gemini/GPT)** - 9 event types
   - Core, Text, Tools
   - No state/observability

3. **PydanticAI (all models)** - 9 event types
   - Core, Text, Tools
   - No state/observability

4. **Vercel AI SDK (all models)** - 9 event types
   - Core, Text, Tools
   - No state/observability

### Moderate Compliance (6-11 event types)
5. **LlamaIndex** - 8 event types (alternative pattern)
   - Uses CHUNK instead of CONTENT
   - STATE_SNAPSHOT support

6. **CrewAI** - 7 event types
   - MESSAGES_SNAPSHOT pattern
   - No standard streaming

7. **Anthropic Raw** - 10 event types
   - Full tool support
   - USAGE_METADATA (unique!)

8. **OpenAI Raw** - 9 event types
   - Full tool support
   - No tokens

9. **Gemini Raw** - 9 event types
   - Full tool support
   - No tokens

### Basic Compliance (3-5 event types)
10. **Cerebras** - 5 event types
    - Core + Text only
    - No tools/state

11. **Google ADK** - 6 event types
    - Core + Text + Error
    - No tools/state

12. **AG2** - 6 event types
    - Core + Text + Error
    - No tools/state

---

## 🎯 Recommendations

### For AG-UI Spec Authors
1. **Standardize HITL events** - No frameworks emit these
2. **Standardize ARTIFACT events** - No frameworks emit these
3. **Standardize THINKING events** - No frameworks emit these
4. **Mandate USAGE_METADATA** - Only 1/26 agents emit this!

### For Framework Authors
1. **Add USAGE_METADATA** - Critical for cost tracking (only anthropic-raw has it)
2. **Implement HITL events** - User approval flows not observable
3. **Implement ARTIFACT events** - Code/diagram generation not observable
4. **Add STATE_SNAPSHOT** - Only 3/12 frameworks expose state
5. **Standardize on CONTENT vs CHUNK** - LlamaIndex uses non-standard pattern

### For Test Suite Improvements
1. **Better HITL triggers** - Current prompts don't trigger actual HITL
2. **Better ARTIFACT triggers** - Need prompts that force artifact creation
3. **Better THINKING triggers** - Need prompts that expose reasoning
4. **Multi-turn fixes** - 0% event capture in multi_turn_memory tests

---

## 📊 Event Pattern Analysis

### Standard Pattern (Most Common)
```
RUN_STARTED
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT (streamed)
TEXT_MESSAGE_CONTENT (streamed)
...
TEXT_MESSAGE_END
RUN_FINISHED
```
**Used by:** 18/26 agents

### Tool Pattern
```
RUN_STARTED
TOOL_CALL_START
TOOL_CALL_ARGS (streamed)
TOOL_CALL_END
TOOL_CALL_RESULT
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT
TEXT_MESSAGE_END
RUN_FINISHED
```
**Used by:** 10/26 agents

### Snapshot Pattern (Alternative)
```
RUN_STARTED
MESSAGES_SNAPSHOT
STATE_SNAPSHOT
MESSAGES_SNAPSHOT (updated)
RUN_FINISHED
```
**Used by:** CrewAI, LlamaIndex (batch updates instead of streaming)

### LangGraph Pattern (Most Detailed)
```
RUN_STARTED
STEP_STARTED
RAW (internal state)
TOOL_CALL_START
TOOL_CALL_END
TOOL_CALL_RESULT
RAW (more state)
STEP_FINISHED
STATE_SNAPSHOT
MESSAGES_SNAPSHOT
TEXT_MESSAGE_START
TEXT_MESSAGE_CONTENT
TEXT_MESSAGE_END
RUN_FINISHED
```
**Used by:** LangGraph only (most observable)

---

## ✅ Summary

| Category | Events Found | Events Missing | Coverage |
|----------|-------------|----------------|----------|
| **Core Lifecycle** | 3/3 | 0 | 100% ✅ |
| **Text Streaming** | 4/4 | 0 | 100% ✅ |
| **Tool Calling** | 5/5 | 0 | 100% ✅ |
| **State Management** | 4/4 | 0 | 100% ✅ |
| **HITL** | 0/4 | 4 | 0% ❌ |
| **Artifacts** | 0/3 | 3 | 0% ❌ |
| **Thinking** | 0/3 | 3 | 0% ❌ |
| **Observability** | 2/2 | 0 | 100% ✅ |

**Overall:** 18/28 expected event types captured (64%)

**Key Gap:** HITL, Artifacts, and Thinking events are completely missing from all frameworks!

---

**Generated:** 2026-02-06
**Data Source:** benchmark-runs/20260206-015725

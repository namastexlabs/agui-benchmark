# 🎯 AG-UI Event Coverage Report

**Benchmark:** 20260206-015725
**Tests:** 609 across 26 agents
**Test Types:** 9 (simple, tool_time, tool_calc, multi_tool, thinking, artifact, hitl_approval, error_handling, multi_turn_memory)
**AG-UI Spec Version:** v0.1.10 (26 event types defined)
**Scope:** Analysis focuses ONLY on the 26 events defined in AG-UI spec

---

## 🚨 CRITICAL FINDINGS

### ❌ Events Defined in Spec But NEVER Captured (8 events)

| Event Type | Status | Purpose |
|------------|--------|---------|
| **THINKING_START** | ❌ 0% adoption | For Claude extended thinking, o1 reasoning |
| **THINKING_END** | ❌ 0% adoption | Thinking step boundaries |
| **THINKING_TEXT_MESSAGE_START** | ❌ 0% adoption | Expose reasoning process |
| **THINKING_TEXT_MESSAGE_CONTENT** | ❌ 0% adoption | Stream reasoning deltas |
| **THINKING_TEXT_MESSAGE_END** | ❌ 0% adoption | End of reasoning stream |
| **STATE_DELTA** | ❌ 0% adoption | JSON Patch format for incremental state updates |
| **ACTIVITY_SNAPSHOT** | ❌ 0% adoption | Rich content (diagrams, code, media) |
| **ACTIVITY_DELTA** | ❌ 0% adoption | Incremental activity updates |
| **CUSTOM** | ❌ 0% adoption | Framework-specific extensions |

**Analysis:** AG-UI spec defines 26 events. We capture **18/26 (69.2%)**. The 8 unused events represent advanced capabilities that no frameworks have implemented yet.

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

### All Frameworks × All AG-UI Spec Events (26 Total)

| Event Type | ag2 | agno-anthropic | agno-cerebras | agno-gemini | agno-openai | anthropic-raw | cerebras-llama-3.1 | cerebras-llama-3.3 | crewai | gemini-raw | google-adk | langgraph-anthropic | langgraph-cerebras | langgraph-gemini | langgraph-openai | llamaindex-anthropic | llamaindex-gemini | llamaindex-openai | openai-raw | pydantic-anthropic | pydantic-gemini | pydantic-openai | vercel-anthropic | vercel-gemini | vercel-openai |
|------------|-----|----------------|---------------|-------------|-------------|---------------|-------------------|-------------------|--------|------------|------------|---------------------|-------------------|------------------|------------------|---------------------|------------------|------------------|------------|-------------------|----------------|----------------|-----------------|--------------|--------------|
| **RUN_STARTED** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RUN_FINISHED** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RUN_ERROR** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **TEXT_MESSAGE_START** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TEXT_MESSAGE_CONTENT** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TEXT_MESSAGE_END** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TEXT_MESSAGE_CHUNK** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **THINKING_START** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **THINKING_END** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **THINKING_TEXT_MESSAGE_START** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **THINKING_TEXT_MESSAGE_CONTENT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **THINKING_TEXT_MESSAGE_END** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **TOOL_CALL_START** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_ARGS** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_END** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **TOOL_CALL_CHUNK** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **TOOL_CALL_RESULT** | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **STATE_SNAPSHOT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **STATE_DELTA** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **MESSAGES_SNAPSHOT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **ACTIVITY_SNAPSHOT** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **ACTIVITY_DELTA** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **STEP_STARTED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **STEP_FINISHED** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **RAW** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **CUSTOM** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **[USAGE_METADATA]** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Note:** [USAGE_METADATA] is NOT in AG-UI spec but anthropic-raw added as custom event. HITL/ARTIFACT events don't exist in spec.

---

## 🧪 TEST TYPE × EVENT MATRIX

Shows which AG-UI spec events are captured during each test type:

| Test Type | TEXT_MESSAGE | TOOL_CALL | STATE | THINKING | ACTIVITY | Notes |
|-----------|--------------|-----------|-------|----------|----------|-------|
| **simple** | ✅ | ❌ | ✅ | ❌ | ❌ | Basic text generation |
| **tool_time** | ✅ | ✅ | ✅ | ❌ | ❌ | Tools work correctly |
| **tool_calc** | ✅ | ✅ | ✅ | ❌ | ❌ | Tools work correctly |
| **multi_tool** | ✅ | ✅ | ✅ | ❌ | ❌ | Multiple tools work |
| **thinking** | ✅ | ✅ | ✅ | ❌ | ❌ | No THINKING_* events emitted |
| **artifact** | ✅ | ✅ | ✅ | ❌ | ❌ | No ACTIVITY_* events emitted |
| **hitl_approval** | ✅ | ✅ | ✅ | ❌ | ❌ | Requires request_approval tool (Agno tested ✅) |
| **error_handling** | ✅ | ✅ | ✅ | ❌ | ❌ | RUN_ERROR properly emitted |
| **multi_turn_memory** | ❌ | ❌ | ❌ | ❌ | ❌ | Most tests fail |

**Finding:** All tests use standard events (TEXT_MESSAGE, TOOL_CALL, STATE). Advanced spec events (THINKING, ACTIVITY) are never emitted by any framework.

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

### Thinking Events (In Spec, Never Captured)
- ❌ **THINKING_START/END**: 0% coverage
- ❌ **THINKING_TEXT_MESSAGE_START/CONTENT/END**: 0% coverage

**Status:** ❌ NOT USED - Defined in spec but no frameworks emit
**Impact:** Cannot observe Claude extended thinking, o1 reasoning, multi-step planning

### Activity Events (In Spec, Never Captured)
- ❌ **ACTIVITY_SNAPSHOT**: 0% coverage
- ❌ **ACTIVITY_DELTA**: 0% coverage

**Status:** ❌ NOT USED - Designed for rich content but no frameworks use
**Impact:** Could be used for artifacts, diagrams, rich media

### State Delta (In Spec, Never Captured)
- ❌ **STATE_DELTA**: 0% coverage

**Status:** ❌ NOT USED - Frameworks only use STATE_SNAPSHOT (full state)
**Impact:** Inefficient for large state objects

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

## 🎯 Recommendations for Framework Authors

### High Priority - Core Spec Events (0% adoption)

1. **Implement THINKING Events** (5 events)
   - THINKING_START, THINKING_END for step boundaries
   - THINKING_TEXT_MESSAGE_START/CONTENT/END for reasoning streams
   - **Use case:** Claude extended thinking, o1 reasoning, multi-step planning
   - **Impact:** Makes reasoning process observable

2. **Use ACTIVITY Events** (2 events)
   - ACTIVITY_SNAPSHOT for rich content (code artifacts, diagrams, media)
   - ACTIVITY_DELTA for incremental updates
   - **Use case:** Code generation, visualizations, structured outputs
   - **Impact:** Standardizes artifact/rich content patterns

3. **Implement STATE_DELTA** (1 event)
   - JSON Patch format (RFC 6902) for incremental state updates
   - **Use case:** Large state objects, frequent updates
   - **Impact:** More efficient than full STATE_SNAPSHOT

4. **Use CUSTOM Events** (1 event)
   - Framework-specific extensions while maintaining AG-UI compatibility
   - **Use case:** Proprietary features, experimental capabilities
   - **Impact:** Enables innovation without breaking protocol

### Medium Priority - Improve Existing

5. **Add STATE_SNAPSHOT** - Only 3/12 frameworks expose state
6. **Standardize on START/CONTENT/END** - Some use CHUNK pattern instead

---

## 🎯 For Benchmark Improvements

1. **Add THINKING triggers** - Need prompts that engage extended thinking/reasoning
2. **Add ACTIVITY triggers** - Need prompts that generate rich content/artifacts
3. **Fix multi_turn_memory** - 0% event capture, most tests fail
4. **Test STATE_DELTA** - Need frameworks that implement incremental updates

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

| Category | In Spec | Captured | Missing | Coverage |
|----------|---------|----------|---------|----------|
| **Core Lifecycle** | 3 | 3 | 0 | 100% ✅ |
| **Text Streaming** | 4 | 4 | 0 | 100% ✅ |
| **Thinking** | 5 | 0 | 5 | 0% ❌ |
| **Tool Calling** | 5 | 5 | 0 | 100% ✅ |
| **State Management** | 5 | 2 | 3 | 40% ⚠️ |
| **Steps** | 2 | 2 | 0 | 100% ✅ |
| **Framework** | 2 | 1 | 1 | 50% ⚠️ |

**Overall:** 18/26 AG-UI event types captured (69.2%)

**Key Gaps:**
- ❌ THINKING events (5) - In spec but 0% adoption
- ❌ ACTIVITY events (2) - In spec but 0% adoption
- ❌ STATE_DELTA (1) - In spec but 0% adoption

**Not in Spec (and don't need to be):**
- ℹ️ **HITL** - Can be implemented via TOOL_CALL events + approval tools (see HITL-IMPLEMENTATION-ANALYSIS.md)
- ℹ️ **ARTIFACTS** - Can use ACTIVITY_SNAPSHOT events or CUSTOM events

---

**Generated:** 2026-02-06
**Data Source:** benchmark-runs/20260206-015725

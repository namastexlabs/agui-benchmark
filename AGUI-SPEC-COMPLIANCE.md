# 🎯 AG-UI Specification Compliance Report

**Analysis Based On:** Official AG-UI Protocol Spec (ag_ui.core.events v0.1.10)

---

## ✅ ACTUAL AG-UI EVENT TYPES (From Spec)

### Core Lifecycle (3 events)
1. **RUN_STARTED** - Run initiation
2. **RUN_FINISHED** - Run completion
3. **RUN_ERROR** - Run error

### Text Streaming (4 events)
4. **TEXT_MESSAGE_START** - Message start
5. **TEXT_MESSAGE_CONTENT** - Streaming delta
6. **TEXT_MESSAGE_END** - Message end
7. **TEXT_MESSAGE_CHUNK** - Alternative chunk format

### Thinking/Reasoning (5 events)
8. **THINKING_START** - Thinking step start
9. **THINKING_END** - Thinking step end
10. **THINKING_TEXT_MESSAGE_START** - Thinking text start
11. **THINKING_TEXT_MESSAGE_CONTENT** - Thinking text delta
12. **THINKING_TEXT_MESSAGE_END** - Thinking text end

### Tool Calling (5 events)
13. **TOOL_CALL_START** - Tool call initiation
14. **TOOL_CALL_ARGS** - Tool arguments (streaming)
15. **TOOL_CALL_END** - Tool call end
16. **TOOL_CALL_CHUNK** - Alternative chunk format
17. **TOOL_CALL_RESULT** - Tool execution result

### State Management (5 events)
18. **STATE_SNAPSHOT** - Complete state
19. **STATE_DELTA** - State patch (JSON Patch RFC 6902)
20. **MESSAGES_SNAPSHOT** - Message history
21. **ACTIVITY_SNAPSHOT** - Activity message
22. **ACTIVITY_DELTA** - Activity patch

### Steps/Nodes (2 events)
23. **STEP_STARTED** - Agent step start
24. **STEP_FINISHED** - Agent step end

### Framework-Specific (2 events)
25. **RAW** - Framework raw event
26. **CUSTOM** - Custom event type

**TOTAL:** 26 event types defined in AG-UI spec

---

## ❌ EVENTS I INCORRECTLY EXPECTED (NOT IN SPEC!)

### HITL (Human-in-the-Loop) - ❌ NOT DEFINED
- ~~HITL_PROMPT~~ - DOESN'T EXIST
- ~~HITL_RESPONSE~~ - DOESN'T EXIST
- ~~HITL_REQUEST~~ - DOESN'T EXIST
- ~~HITL_RESULT~~ - DOESN'T EXIST

**Reality:** AG-UI spec has NO HITL events! HITL would need to use CUSTOM events or be added to spec.

### Artifacts - ❌ NOT DEFINED
- ~~ARTIFACT_START~~ - DOESN'T EXIST
- ~~ARTIFACT_CONTENT~~ - DOESN'T EXIST
- ~~ARTIFACT_END~~ - DOESN'T EXIST

**Reality:** AG-UI spec has NO ARTIFACT events! Could use ACTIVITY_SNAPSHOT or CUSTOM.

### Incorrect Thinking Events - ❌ WRONG FORMAT
- ~~THINKING_START~~ ✅ EXISTS (but different from what I expected)
- ~~THINKING_CONTENT~~ ❌ WRONG (should be THINKING_TEXT_MESSAGE_CONTENT)
- ~~THINKING_END~~ ✅ EXISTS (but different from what I expected)

**Reality:** THINKING events exist but have a different structure!

---

## 📊 ACTUAL COVERAGE: 18/26 Events (69.2%)

### ✅ Events We Successfully Capture

| Event Type | Captured? | Usage | Notes |
|------------|-----------|-------|-------|
| **RUN_STARTED** | ✅ | 607/609 tests | 99.7% |
| **RUN_FINISHED** | ✅ | 601/609 tests | 98.7% |
| **RUN_ERROR** | ✅ | 18/609 tests | 3.0% (only on errors) |
| **TEXT_MESSAGE_START** | ✅ | 495/609 tests | 81.3% |
| **TEXT_MESSAGE_CONTENT** | ✅ | 462/609 tests | 75.9% |
| **TEXT_MESSAGE_END** | ✅ | 495/609 tests | 81.3% |
| **TEXT_MESSAGE_CHUNK** | ✅ | 69/609 tests | 11.3% (LlamaIndex) |
| **TOOL_CALL_START** | ✅ | 181/609 tests | 29.7% |
| **TOOL_CALL_ARGS** | ✅ | 165/609 tests | 27.1% |
| **TOOL_CALL_END** | ✅ | 181/609 tests | 29.7% |
| **TOOL_CALL_CHUNK** | ✅ | 27/609 tests | 4.4% (LlamaIndex) |
| **TOOL_CALL_RESULT** | ✅ | 182/609 tests | 29.9% |
| **STATE_SNAPSHOT** | ✅ | 177/609 tests | 29.1% (LangGraph, CrewAI, LlamaIndex) |
| **MESSAGES_SNAPSHOT** | ✅ | 177/609 tests | 29.1% (CrewAI, LlamaIndex) |
| **STEP_STARTED** | ✅ | 98/609 tests | 16.1% (LangGraph, CrewAI) |
| **STEP_FINISHED** | ✅ | 105/609 tests | 17.2% (LangGraph, CrewAI) |
| **RAW** | ✅ | 84/609 tests | 13.8% (LangGraph only) |
| **CUSTOM** | ⚠️ | 0/609 tests | Not used by any framework |

**Coverage: 18/26 = 69.2%**

---

### ❌ Events NOT Captured (8 missing)

| Event Type | Status | Reason |
|------------|--------|--------|
| **THINKING_START** | ❌ NEVER | No frameworks emit |
| **THINKING_END** | ❌ NEVER | No frameworks emit |
| **THINKING_TEXT_MESSAGE_START** | ❌ NEVER | No frameworks emit |
| **THINKING_TEXT_MESSAGE_CONTENT** | ❌ NEVER | No frameworks emit |
| **THINKING_TEXT_MESSAGE_END** | ❌ NEVER | No frameworks emit |
| **STATE_DELTA** | ❌ NEVER | No frameworks use delta updates |
| **ACTIVITY_SNAPSHOT** | ❌ NEVER | No frameworks emit |
| **ACTIVITY_DELTA** | ❌ NEVER | No frameworks emit |

**Missing: 8/26 = 30.8%**

---

## 🔍 Key Findings

### 1. NO HITL Events in Spec
**My Error:** I assumed HITL_PROMPT/RESPONSE/etc. existed in AG-UI spec.

**Reality:** AG-UI spec has NO standardized HITL events!

**Options for HITL:**
- Use CUSTOM events
- Propose HITL events as AG-UI spec addition
- Frameworks handle HITL outside AG-UI protocol

### 2. NO ARTIFACT Events in Spec
**My Error:** I assumed ARTIFACT_START/CONTENT/END existed.

**Reality:** AG-UI spec has NO standardized artifact events!

**Options for Artifacts:**
- Use ACTIVITY_SNAPSHOT (designed for rich content)
- Use CUSTOM events
- Propose ARTIFACT events as spec addition

### 3. THINKING Events Exist But Unused
**Spec Defines:**
- THINKING_START / THINKING_END (step boundaries)
- THINKING_TEXT_MESSAGE_* (reasoning text streaming)

**Reality:** ZERO frameworks emit thinking events!

**Impact:** Claude's extended thinking, o1/o3 reasoning, etc. NOT observable

### 4. ACTIVITY Events Unused
**Spec Defines:**
- ACTIVITY_SNAPSHOT (rich content snapshots)
- ACTIVITY_DELTA (activity patches)

**Reality:** NO frameworks use these events

**Could Be Used For:**
- Artifacts
- Rich media
- Visualizations
- Code blocks

### 5. STATE_DELTA Unused
**Spec Defines:** JSON Patch (RFC 6902) for incremental state updates

**Reality:** Frameworks only use STATE_SNAPSHOT (full state)

**Impact:** Inefficient for large states (send full state every time)

---

## 📈 Framework Compliance Scores

### Full Compliance (14+ events)
- None! Best is LangGraph with 13/26

### High Compliance (10-13 events)
1. **LangGraph** - 13/26 (50%) - Missing thinking, activity, delta events

### Moderate Compliance (6-9 events)
2. **Agno (Claude/GPT/Gemini)** - 9/26 (35%)
3. **PydanticAI** - 9/26 (35%)
4. **Vercel AI SDK** - 9/26 (35%)
5. **Anthropic Raw** - 10/26 (38%) - Has USAGE_METADATA (custom?)
6. **OpenAI Raw** - 9/26 (35%)
7. **Gemini Raw** - 9/26 (35%)
8. **LlamaIndex** - 8/26 (31%)
9. **CrewAI** - 7/26 (27%)

### Low Compliance (3-5 events)
10. **Cerebras** - 5/26 (19%)
11. **Google ADK** - 6/26 (23%)
12. **AG2** - 6/26 (23%)

**Average Compliance:** ~30-35% of AG-UI spec

---

## 🎯 What's Really Missing

### Missing From ALL Frameworks:
1. **THINKING events** (5 event types) - 0% usage
   - Would expose Claude extended thinking, o1 reasoning, etc.

2. **ACTIVITY events** (2 event types) - 0% usage
   - Could represent artifacts, rich media, visualizations

3. **STATE_DELTA** - 0% usage
   - Only full state snapshots used (inefficient)

4. **CUSTOM** - 0% usage
   - Frameworks could use for extensions but don't

### Rarely Used:
5. **USAGE_METADATA** - NOT in spec! (Only anthropic-raw custom addition)
   - Critical for cost tracking
   - Should be added to AG-UI spec?

---

## 💡 Recommendations

### For AG-UI Spec Maintainers:

1. **Add HITL Events**
   ```
   HITL_PROMPT - User approval requested
   HITL_RESPONSE - User provided approval
   ```

2. **Add ARTIFACT Events (or clarify ACTIVITY usage)**
   ```
   Option A: Standardize ARTIFACT_* events
   Option B: Document ACTIVITY_SNAPSHOT for artifacts
   ```

3. **Add USAGE_METADATA Event**
   ```
   USAGE_METADATA - Token/cost tracking
   Currently missing but critical for production!
   ```

4. **Promote THINKING Events**
   - Document use cases (Claude thinking, o1 reasoning)
   - Provide implementation examples
   - Currently defined but 0% adoption

5. **Document ACTIVITY Pattern**
   - When to use ACTIVITY vs CUSTOM
   - Examples for rich content
   - Currently defined but 0% adoption

### For Framework Developers:

1. **Implement THINKING Events**
   - Claude extended thinking
   - o1/o3 reasoning
   - Multi-step planning

2. **Use ACTIVITY_SNAPSHOT for Artifacts**
   - Code generation
   - Diagrams/charts
   - Rich media

3. **Consider STATE_DELTA**
   - More efficient than full snapshots
   - Better for large states

4. **Add Usage Tracking**
   - Use CUSTOM for now
   - Propose USAGE_METADATA standard

---

## 📊 Corrected Coverage Summary

| Category | In Spec | Captured | Missing | Coverage |
|----------|---------|----------|---------|----------|
| **Core Lifecycle** | 3 | 3 | 0 | 100% ✅ |
| **Text Streaming** | 4 | 4 | 0 | 100% ✅ |
| **Tool Calling** | 5 | 5 | 0 | 100% ✅ |
| **State Management** | 5 | 2 | 3 | 40% ⚠️ |
| **Steps** | 2 | 2 | 0 | 100% ✅ |
| **Thinking** | 5 | 0 | 5 | 0% ❌ |
| **Framework** | 2 | 1 | 1 | 50% ⚠️ |

**Overall:** 18/26 event types captured (69.2%)

---

## ✅ Corrections to Previous Analysis

### What I Got Wrong:

1. **HITL Events** - I made these up! Not in AG-UI spec.
2. **ARTIFACT Events** - I made these up! Not in AG-UI spec.
3. **THINKING Event Names** - Spec has different structure than I expected.
4. **USAGE_METADATA** - Not in spec! Custom addition by anthropic-raw.

### What I Got Right:

1. ✅ Core events (RUN_*, TEXT_MESSAGE_*, TOOL_CALL_*)
2. ✅ State events (STATE_SNAPSHOT, MESSAGES_SNAPSHOT)
3. ✅ Step events (STEP_STARTED, STEP_FINISHED)
4. ✅ Framework events (RAW)

---

**Conclusion:** AG-UI spec is comprehensive (26 events) but only 69% utilized. Major gaps:
- ❌ NO frameworks emit THINKING events (0/26)
- ❌ NO frameworks use ACTIVITY events (0/26)
- ❌ NO frameworks use STATE_DELTA (0/26)
- ⚠️  NO standardized usage/cost tracking in spec
- ⚠️  NO HITL or ARTIFACT events defined (need spec addition?)

**Generated:** 2026-02-06
**Based On:** ag_ui.core.events v0.1.10

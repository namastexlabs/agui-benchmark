# 🎯 Token Tracking Implementation Guide

## Problem Statement

Currently only **3/26 agents** (11.5%) report token usage:
- ✅ LangGraph (anthropic, openai, gemini)
- ❌ All other frameworks

**Root cause:** AG-UI wrappers receive usage data from underlying APIs but don't emit it as AG-UI events.

---

## Solution: Add USAGE_METADATA Events

### Proposed AG-UI Event

```json
{
  "type": "USAGE_METADATA",
  "input_tokens": 677,
  "output_tokens": 70,
  "total_tokens": 747,
  "model": "claude-haiku-4-5-20251001"
}
```

**When to emit:** At end of streaming, before `RUN_FINISHED`

---

## Framework-Specific Implementations

### 1. Anthropic Raw API ✅ **Usage Available**

**Current code** (`anthropic_raw/main.py` line 188):
```python
final_message = stream.get_final_message()
# final_message.usage exists but not emitted!
```

**Fix:**
```python
final_message = stream.get_final_message()

# EMIT USAGE_METADATA
if hasattr(final_message, 'usage') and final_message.usage:
    yield encode_sse("USAGE_METADATA", {
        "input_tokens": final_message.usage.input_tokens,
        "output_tokens": final_message.usage.output_tokens,
        "total_tokens": final_message.usage.input_tokens + final_message.usage.output_tokens,
        "model": "claude-haiku-4-5-20251001"
    })
```

---

### 2. OpenAI Raw API ✅ **Usage Available**

**Current streaming:**
```python
for chunk in stream:
    # ...stream deltas...
```

**Anthropic provides usage in final message, OpenAI provides it in the last chunk:**

**Fix:**
```python
final_chunk = None
for chunk in stream:
    # ...stream deltas...
    final_chunk = chunk

# EMIT USAGE_METADATA from final chunk
if final_chunk and hasattr(final_chunk, 'usage') and final_chunk.usage:
    yield encode_sse("USAGE_METADATA", {
        "input_tokens": final_chunk.usage.prompt_tokens,
        "output_tokens": final_chunk.usage.completion_tokens,
        "total_tokens": final_chunk.usage.total_tokens,
        "model": "gpt-5-mini"
    })
```

---

### 3. Gemini Raw API ✅ **Usage Available**

**Gemini provides usage_metadata in response:**

**Fix:**
```python
# After streaming completes
if hasattr(response, 'usage_metadata') and response.usage_metadata:
    yield encode_sse("USAGE_METADATA", {
        "input_tokens": response.usage_metadata.prompt_token_count,
        "output_tokens": response.usage_metadata.candidates_token_count,
        "total_tokens": response.usage_metadata.total_token_count,
        "model": "gemini-2.5-flash"
    })
```

---

### 4. Cerebras Raw API ✅ **Usage Available**

**Cerebras uses OpenAI-compatible API, same pattern as OpenAI:**

**Fix:**
```python
# Extract from last chunk (OpenAI format)
if final_chunk and 'usage' in chunk:
    usage = chunk['usage']
    yield encode_sse("USAGE_METADATA", {
        "input_tokens": usage.get('prompt_tokens', 0),
        "output_tokens": usage.get('completion_tokens', 0),
        "total_tokens": usage.get('total_tokens', 0),
        "model": model  # llama-3.3-70b, etc.
    })
```

---

### 5. Agno Framework ✅ **Usage Available**

**Agno uses OpenAI/Anthropic/Gemini clients internally.**

**Current:** Uses AGUI() interface which doesn't expose usage.

**Options:**

#### Option A: Enhance AGUI Interface (Requires upstream PR)
```python
# Request feature in agno library
from agno.os.interfaces.agui import AGUI

# AGUI should emit usage from underlying model response
```

#### Option B: Custom Wrapper
```python
# Create custom streaming wrapper
async def stream_with_usage(agent, request):
    response = await agent.run(request)

    # Stream events
    async for event in response.stream():
        yield event

    # EMIT USAGE_METADATA
    if hasattr(response, 'usage'):
        yield {
            "type": "USAGE_METADATA",
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
```

---

### 6. LangGraph Framework ✅ **ALREADY WORKING**

**LangGraph includes usage in RAW events:**

```json
{
  "type": "RAW",
  "event": {
    "data": {
      "chunk": {
        "usage_metadata": {
          "input_tokens": 677,
          "output_tokens": 70
        }
      }
    }
  }
}
```

**No changes needed** - our extraction logic already handles this.

---

### 7. PydanticAI Framework ✅ **Usage Available**

**PydanticAI provides `result.usage()`:**

**Current wrapper** (needs investigation):
```python
# pydantic_agent/main.py
result = await agent.run(...)
```

**Fix:**
```python
result = await agent.run(...)

# After streaming
usage = result.usage()
if usage:
    yield encode_sse("USAGE_METADATA", {
        "input_tokens": usage.request_tokens,
        "output_tokens": usage.response_tokens,
        "total_tokens": usage.total_tokens,
        "model": result.data.model  # Get actual model used
    })
```

---

### 8. LlamaIndex Framework ✅ **Usage Available**

**LlamaIndex ReActAgent provides token counts:**

**Current wrapper** (needs investigation):
```python
# llamaindex_agent/main.py
response = await agent.astream_chat(...)
```

**Fix:**
```python
response = await agent.astream_chat(...)

# After streaming
if hasattr(response, 'token_counts'):
    yield encode_sse("USAGE_METADATA", {
        "input_tokens": response.token_counts.prompt_tokens,
        "output_tokens": response.token_counts.completion_tokens,
        "total_tokens": response.token_counts.total_tokens,
        "model": agent.llm.metadata.model_name
    })
```

---

### 9. Vercel AI SDK (TypeScript) ✅ **Usage Available**

**Vercel AI SDK returns usage in result:**

**Current wrapper** (`ts-agents/vercel_agent/index.ts`):
```typescript
const result = await streamText({
  model: anthropic('claude-3-haiku-20240307'),
  messages: request.messages,
});
```

**Fix:**
```typescript
const result = await streamText({ ... });

// Stream text chunks
for await (const chunk of result.textStream) {
  // ...emit TEXT_MESSAGE_CONTENT...
}

// EMIT USAGE_METADATA
const usage = await result.usage;
if (usage) {
  yield JSON.stringify({
    type: "USAGE_METADATA",
    input_tokens: usage.promptTokens,
    output_tokens: usage.completionTokens,
    total_tokens: usage.totalTokens,
    model: modelName
  });
}
```

---

### 10. CrewAI Framework ⚠️ **Special Case**

**CrewAI uses MESSAGES_SNAPSHOT pattern, not TEXT_MESSAGE_CONTENT.**

**Investigation needed:** Check if crew.kickoff() returns usage.

---

### 11. AG2 (AutoGen) Framework ⚠️ **Investigation Needed**

**AG2 uses custom AG-UI adapter.**

**Check:** Does agent.run() return usage metadata?

---

### 12. Google ADK Framework ✅ **Usage Available**

**Google ADK uses Gemini API which provides usage:**

**Same as Gemini Raw API fix.**

---

## Implementation Priority

### Phase 1: Raw APIs (Quick Win) ⭐ **HIGHEST PRIORITY**
- [ ] anthropic_raw/main.py
- [ ] openai_raw/main.py
- [ ] gemini_raw/main.py
- [ ] cerebras_raw/server.py

**Impact:** 4 agents (15.4% → 27.9%)
**Effort:** 30 minutes (straightforward, we have direct access)

### Phase 2: Native Frameworks (Medium Effort)
- [ ] pydantic_agent/main.py
- [ ] llamaindex_agent/main.py
- [ ] vercel_agent/index.ts
- [ ] google_adk_agent/main.py

**Impact:** 10 agents (27.9% → 66.4%)
**Effort:** 2-3 hours (need to check wrapper implementations)

### Phase 3: Complex Frameworks (Higher Effort)
- [ ] agno_agent/main.py (requires custom wrapper or upstream PR)
- [ ] crewai_agent/main.py (special MESSAGES_SNAPSHOT pattern)
- [ ] ag2_agent/main.py (custom adapter)

**Impact:** 12 agents (66.4% → 100%)
**Effort:** 4-6 hours (may require framework modifications)

---

## Testing Plan

### 1. Add Test Assertion

Update `test_agents.py`:
```python
# After benchmark completes
agents_with_tokens = [
    name for name, metrics in all_metrics.items()
    if any(m.input_tokens > 0 for m in metrics)
]

print(f"\n📊 Token tracking coverage: {len(agents_with_tokens)}/26 ({len(agents_with_tokens)/26*100:.1f}%)")
print(f"   Agents with token data: {', '.join(sorted(agents_with_tokens))}")
```

### 2. Validation Checklist

For each updated wrapper, verify:
- ✅ USAGE_METADATA event emitted before RUN_FINISHED
- ✅ input_tokens > 0 (not zero)
- ✅ output_tokens > 0 (not zero)
- ✅ total_tokens = input_tokens + output_tokens
- ✅ metadata.json contains token data
- ✅ Cost calculation works in print_cost_breakdown()

### 3. Quick Test Command

```bash
# Test single agent
curl -X POST http://localhost:7776/agent \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"id":"1","role":"user","content":"Hi"}],
    "thread_id":"test",
    "run_id":"test",
    "state":{}, "tools":[], "context":[], "forwardedProps":{}
  }' | grep -A5 "USAGE_METADATA"
```

---

## Expected Results After Full Implementation

### Token Tracking Coverage

| Phase | Agents | Coverage | Cost Calculation |
|-------|--------|----------|------------------|
| **Before** | 3/26 | 11.5% | Partial |
| **Phase 1** | 7/26 | 26.9% | Improved |
| **Phase 2** | 17/26 | 65.4% | Good |
| **Phase 3** | 26/26 | 100% | Complete |

### Cost Breakdown (After Full Implementation)

```
💰 COST BY MODEL
claude-haiku: ~150,000 in / ~15,000 out → ~$0.18
gemini-flash: ~40,000 in / ~7,000 out → ~$0.005
gpt-5-mini: ~50,000 in / ~60,000 out → ~0.04
cerebras-llama: ~20,000 in / ~5,000 out → ~$0.015

💵 TOTAL: ~$0.24 (24 cents for 702 tests)
📈 Per 1,000 tests: ~$0.34
```

---

## Upstream Contributions

Consider submitting PRs to add usage metadata to AG-UI outputs:

1. **ag-ui-langgraph** ✅ Already includes (via RAW events)
2. **agno** - Add usage to AGUI() interface
3. **ag-ui-crewai** - Add usage to MESSAGES_SNAPSHOT
4. **ag-ui-pydantic** - Add usage metadata event (if package exists)

---

## Alternative: Estimate from Response Length

If usage unavailable, use approximation:

```python
# Fallback estimation
if metrics.input_tokens == 0:
    # Rough approximation: ~4 chars per token
    metrics.input_tokens = len(prompt) // 4
    metrics.output_tokens = len(final_text) // 4
    metrics.total_tokens = metrics.input_tokens + metrics.output_tokens
```

**Accuracy:** ±20-30% (better than nothing for cost estimates)

---

## Next Steps

1. ✅ Document token tracking approach (this file)
2. ⏳ **Implement Phase 1** (Raw APIs) - Quick win, 30 minutes
3. ⏳ Run benchmark to verify 27.9% coverage
4. ⏳ Implement Phase 2 (Native frameworks) - 2-3 hours
5. ⏳ Run benchmark to verify 66.4% coverage
6. ⏳ Implement Phase 3 (Complex frameworks) - 4-6 hours
7. ⏳ Run final benchmark to verify 100% coverage
8. ⏳ Update BENCHMARK-ANALYSIS.md with complete cost data

---

**Priority:** HIGH
**Effort:** 7-10 hours total for 100% coverage
**Value:** Essential for production cost tracking and optimization

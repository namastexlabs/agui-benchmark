# 🧠 Cerebras OpenAI-Compatible Integration Guide

Cerebras provides an **OpenAI-compatible API**, which means ANY framework that supports OpenAI can use Cerebras by simply changing the `base_url`.

## 📡 Cerebras API Details

**Base URL:** `https://api.cerebras.ai/v1`
**API Key:** Set `CEREBRAS_API_KEY` in `.env`
**Models:**
- `llama-3.3-70b` (latest, recommended)
- `llama-3.1-70b`
- `llama-3.1-8b`

## ✅ Integration Pattern (All Frameworks)

### Key Concept
```python
# Instead of standard OpenAI:
ChatOpenAI(model="gpt-4")

# Use Cerebras with custom base_url:
ChatOpenAI(
    model="llama-3.3-70b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1"
)
```

---

## 🔧 Framework-Specific Integration

### 1. Agno

```python
from agno.models.openai import OpenAIChat

cerebras_agent = Agent(
    model=OpenAIChat(
        id="llama-3.3-70b",
        api_key=os.getenv("CEREBRAS_API_KEY"),
        base_url="https://api.cerebras.ai/v1"
    ),
    tools=[...],
    instructions="..."
)

# Add to AgentOS
agent_os = AgentOS(
    agents=[..., cerebras_agent],
    interfaces=[
        AGUI(agent=cerebras_agent, prefix="/agui/cerebras")
    ]
)
```

**Result:** `POST http://localhost:7771/agui/cerebras`

---

### 2. LangGraph

```python
from langchain_openai import ChatOpenAI

llm_cerebras = ChatOpenAI(
    model="llama-3.3-70b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1"
)

graph_cerebras = create_graph(llm_cerebras)
agent_cerebras = LangGraphAgent(
    name="langgraph-cerebras",
    graph=graph_cerebras,
    description="LangGraph agent with Cerebras"
)

add_langgraph_fastapi_endpoint(app, agent_cerebras, "/agent/cerebras")
```

**Result:** `POST http://localhost:7772/agent/cerebras`

---

### 3. PydanticAI

```python
from pydantic_ai.models.openai import OpenAIModel

cerebras_model = OpenAIModel(
    "llama-3.3-70b",
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

# Use in agent
agent_cerebras = Agent(
    model=cerebras_model,
    tools=[...],
    system_prompt="..."
)
```

**Result:** Cerebras via PydanticAI agent

---

### 4. LlamaIndex

```python
from llama_index.llms.openai import OpenAI

llm_cerebras = OpenAI(
    model="llama-3.3-70b",
    api_key=os.getenv("CEREBRAS_API_KEY"),
    api_base="https://api.cerebras.ai/v1"  # Note: api_base not base_url
)

# Use in ReActAgent
agent = ReActAgent.from_tools(
    tools=[...],
    llm=llm_cerebras,
    verbose=True
)
```

**Result:** Cerebras via LlamaIndex ReActAgent

---

### 5. Vercel AI SDK (TypeScript)

```typescript
import { createOpenAI } from '@ai-sdk/openai'

const cerebras = createOpenAI({
  name: 'cerebras',
  apiKey: process.env.CEREBRAS_API_KEY,
  baseURL: 'https://api.cerebras.ai/v1'
})

// Use in streamText
const result = await streamText({
  model: cerebras('llama-3.3-70b'),
  messages: [...]
})
```

**Result:** `POST http://localhost:7779/agent/cerebras`

---

## 🧪 Test Configuration

Add to `test_agents.py`:

```python
"langgraph-cerebras": {
    "url": "http://localhost:7772/agent/cerebras",
    "port": 7772,
    "health": "http://localhost:7772/health",
    "type": "native",
    "language": "Python",
    "framework": "langgraph",
    "model": "cerebras",
    "model_id": "llama-3.3-70b",
},
"pydantic-cerebras": {
    "url": "http://localhost:7774/cerebras",
    "port": 7774,
    "health": "http://localhost:7774/health",
    "type": "native",
    "language": "Python",
    "framework": "pydantic-ai",
    "model": "cerebras",
    "model_id": "llama-3.3-70b",
},
"llamaindex-cerebras": {
    "url": "http://localhost:7780/agent/cerebras/run",
    "port": 7780,
    "health": "http://localhost:7780/health",
    "type": "native",
    "language": "Python",
    "framework": "llamaindex",
    "model": "cerebras",
    "model_id": "llama-3.3-70b",
},
"vercel-cerebras": {
    "url": "http://localhost:7779/agent/cerebras",
    "port": 7779,
    "health": "http://localhost:7779/health",
    "type": "wrapped",
    "language": "TypeScript",
    "framework": "vercel-ai-sdk",
    "model": "cerebras",
    "model_id": "llama-3.3-70b",
},
```

---

## 🚀 Quick Start

1. **Add CEREBRAS_API_KEY to .env:**
   ```bash
   echo "CEREBRAS_API_KEY=csk-ycjmxtfh88ywpxxwx5cnfp5kfy4xj49hxxn66k8yxdv2v2j3" >> .env
   ```

2. **Restart agents:**
   ```bash
   ./stop_all.sh
   ./start_all.sh
   ```

3. **Test Cerebras endpoint:**
   ```bash
   curl -X POST http://localhost:7771/agui/cerebras \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [{"id": "1", "role": "user", "content": "Say hi"}],
       "thread_id": "test",
       "run_id": "test"
     }'
   ```

4. **Run benchmark:**
   ```bash
   uv run python test_agents.py
   ```

---

## 📊 Expected Performance

Based on initial tests:
- **Raw Cerebras API:** 3.9-4.7s median
- **Framework-wrapped (expected):** 2-3s median (optimized)

Frameworks should improve Cerebras performance through:
- Connection pooling
- HTTP/2 multiplexing
- Async I/O optimization
- Better error handling

---

## ⚠️ Known Issues

1. **llama-3.1-70b** produces empty responses (Cerebras API issue)
2. **llama-3.3-70b** and **llama-3.1-8b** work correctly
3. Cerebras doesn't support function calling (tool use) yet

---

## 🎯 Benchmark Focus

After adding Cerebras to all frameworks, we can compare:

| Framework | Expected Median | vs Raw API |
|-----------|----------------|------------|
| agno-cerebras | 2.5s (est) | 1.6x faster |
| langgraph-cerebras | 2.8s (est) | 1.4x faster |
| pydantic-cerebras | 2.3s (est) | 1.7x faster |
| llamaindex-cerebras | 2.2s (est) | 1.8x faster |
| vercel-cerebras | 2.9s (est) | 1.4x faster |
| cerebras-raw | 3.9s (actual) | baseline |

This will prove if framework optimizations benefit Cerebras like they do for Claude/OpenAI/Gemini (3-5x speedup).

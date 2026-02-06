#!/usr/bin/env python3
"""
AG-UI Multi-Framework Test Script with Multi-Model Comparison

Tests all agent frameworks for AG-UI protocol compliance and compares performance.
Each multi-model framework is tested with Claude, OpenAI, and Gemini.

Run with: python test_agents.py
"""

import httpx
import asyncio
import json
import sys
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


# Number of runs per test for statistical significance
NUM_RUNS = 3

# Create benchmark-runs directory
BENCHMARK_RUNS_DIR = Path(__file__).parent / "benchmark-runs"
BENCHMARK_RUNS_DIR.mkdir(exist_ok=True)

# Model identifiers for grouping
MODELS = {
    "claude": "claude-haiku-4-5-20251001",
    "openai": "gpt-5-mini",
    "gemini": "gemini-2.5-flash",
    "cerebras": "llama-3.3-70b",  # Cerebras: fastest LLM inference
}

# Model pricing (per 1M tokens) as of 2026-02
# Prices in USD
MODEL_PRICING = {
    "claude-haiku-4-5-20251001": {
        "input": 0.80,    # $0.80 per 1M input tokens
        "output": 4.00,   # $4.00 per 1M output tokens
    },
    "gpt-5-mini": {
        "input": 0.150,   # $0.15 per 1M input tokens
        "output": 0.600,  # $0.60 per 1M output tokens
    },
    "gemini-2.5-flash": {
        "input": 0.075,   # $0.075 per 1M input tokens (up to 128K context)
        "output": 0.30,   # $0.30 per 1M output tokens
    },
    "llama-3.3-70b": {
        "input": 0.60,    # $0.60 per 1M input tokens
        "output": 0.60,   # $0.60 per 1M output tokens
    },
    "llama-3.1-70b": {
        "input": 0.60,
        "output": 0.60,
    },
    "llama-3.1-8b": {
        "input": 0.10,
        "output": 0.10,
    },
}

# Agent configurations organized by framework and model
# Multi-model frameworks have separate entries per model for fair comparison
AGENTS = {
    # === AGNO (Multi-model) ===
    # Note: AGUI interface adds /agui suffix to the prefix
    "agno-anthropic": {
        "url": "http://localhost:7771/agui/anthropic/agui",
        "port": 7771,
        "health": "http://localhost:7771/health",
        "type": "native",
        "language": "Python",
        "framework": "agno",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },
    "agno-openai": {
        "url": "http://localhost:7771/agui/openai/agui",
        "port": 7771,
        "health": "http://localhost:7771/health",
        "type": "native",
        "language": "Python",
        "framework": "agno",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },
    "agno-gemini": {
        "url": "http://localhost:7771/agui/gemini/agui",
        "port": 7771,
        "health": "http://localhost:7771/health",
        "type": "native",
        "language": "Python",
        "framework": "agno",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },
    "agno-cerebras": {
        "url": "http://localhost:7771/agui/cerebras",
        "port": 7771,
        "health": "http://localhost:7771/health",
        "type": "native",
        "language": "Python",
        "framework": "agno",
        "model": "cerebras",
        "model_id": "llama-3.3-70b",
    },

    # === LANGGRAPH (Multi-model) ===
    "langgraph-anthropic": {
        "url": "http://localhost:7772/agent/anthropic",
        "port": 7772,
        "health": "http://localhost:7772/health",
        "type": "native",
        "language": "Python",
        "framework": "langgraph",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },
    "langgraph-openai": {
        "url": "http://localhost:7772/agent/openai",
        "port": 7772,
        "health": "http://localhost:7772/health",
        "type": "native",
        "language": "Python",
        "framework": "langgraph",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },
    "langgraph-gemini": {
        "url": "http://localhost:7772/agent/gemini",
        "port": 7772,
        "health": "http://localhost:7772/health",
        "type": "native",
        "language": "Python",
        "framework": "langgraph",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },
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

    # === PYDANTIC-AI (Multi-model) ===
    "pydantic-anthropic": {
        "url": "http://localhost:7774/anthropic",
        "port": 7774,
        "health": "http://localhost:7774/health",
        "type": "native",
        "language": "Python",
        "framework": "pydantic-ai",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },
    "pydantic-openai": {
        "url": "http://localhost:7774/openai",
        "port": 7774,
        "health": "http://localhost:7774/health",
        "type": "native",
        "language": "Python",
        "framework": "pydantic-ai",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },
    "pydantic-gemini": {
        "url": "http://localhost:7774/gemini",
        "port": 7774,
        "health": "http://localhost:7774/health",
        "type": "native",
        "language": "Python",
        "framework": "pydantic-ai",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },

    # === LLAMAINDEX (Multi-model) ===
    "llamaindex-anthropic": {
        "url": "http://localhost:7780/agent/anthropic/run",
        "port": 7780,
        "health": "http://localhost:7780/health",
        "type": "native",
        "language": "Python",
        "framework": "llamaindex",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },
    "llamaindex-openai": {
        "url": "http://localhost:7780/agent/openai/run",
        "port": 7780,
        "health": "http://localhost:7780/health",
        "type": "native",
        "language": "Python",
        "framework": "llamaindex",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },
    "llamaindex-gemini": {
        "url": "http://localhost:7780/agent/gemini/run",
        "port": 7780,
        "health": "http://localhost:7780/health",
        "type": "native",
        "language": "Python",
        "framework": "llamaindex",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },

    # === VERCEL-AI-SDK (Multi-model, TypeScript) ===
    "vercel-anthropic": {
        "url": "http://localhost:7779/agent/anthropic",
        "port": 7779,
        "health": "http://localhost:7779/health",
        "type": "wrapped",
        "language": "TypeScript",
        "framework": "vercel-ai-sdk",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },
    "vercel-openai": {
        "url": "http://localhost:7779/agent/openai",
        "port": 7779,
        "health": "http://localhost:7779/health",
        "type": "wrapped",
        "language": "TypeScript",
        "framework": "vercel-ai-sdk",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },
    "vercel-gemini": {
        "url": "http://localhost:7779/agent/gemini",
        "port": 7779,
        "health": "http://localhost:7779/health",
        "type": "wrapped",
        "language": "TypeScript",
        "framework": "vercel-ai-sdk",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },

    # === SINGLE-MODEL FRAMEWORKS ===

    # CrewAI (Claude only - has known issues)
    "crewai": {
        "url": "http://localhost:7773/agent",
        "port": 7773,
        "health": "http://localhost:7773/health",
        "type": "native",
        "language": "Python",
        "framework": "crewai",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },

    # AG2/AutoGen (OpenAI only)
    "ag2": {
        "url": "http://localhost:7781/agent",
        "port": 7781,
        "health": "http://localhost:7781/health",
        "type": "wrapped",
        "language": "Python",
        "framework": "ag2",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },

    # Google ADK (Gemini only)
    "google-adk": {
        "url": "http://localhost:7782/agent",
        "port": 7782,
        "health": "http://localhost:7782/health",
        "type": "native",
        "language": "Python",
        "framework": "google-adk",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },

    # === RAW LLM APIs (baseline comparisons) ===
    "openai-raw": {
        "url": "http://localhost:7775/agent",
        "port": 7775,
        "health": "http://localhost:7775/health",
        "type": "raw",
        "language": "Python",
        "framework": "openai-raw",
        "model": "openai",
        "model_id": "gpt-5-mini",
    },
    "anthropic-raw": {
        "url": "http://localhost:7776/agent",
        "port": 7776,
        "health": "http://localhost:7776/health",
        "type": "raw",
        "language": "Python",
        "framework": "anthropic-raw",
        "model": "claude",
        "model_id": "claude-haiku-4-5-20251001",
    },
    "gemini-raw": {
        "url": "http://localhost:7777/agent",
        "port": 7777,
        "health": "http://localhost:7777/health",
        "type": "raw",
        "language": "Python",
        "framework": "gemini-raw",
        "model": "gemini",
        "model_id": "gemini-2.5-flash",
    },

    # === CEREBRAS (Ultra-fast inference) ===
    # Testing multiple Cerebras models for speed comparison
    "cerebras-llama-3.3-70b": {
        "url": "http://localhost:7778/agent",
        "port": 7778,
        "health": "http://localhost:7778/health",
        "type": "raw",
        "language": "Python",
        "framework": "cerebras-raw",
        "model": "cerebras",
        "model_id": "llama-3.3-70b",
        "model_override": "llama-3.3-70b",  # Send in request
    },
    "cerebras-llama-3.1-70b": {
        "url": "http://localhost:7778/agent",
        "port": 7778,
        "health": "http://localhost:7778/health",
        "type": "raw",
        "language": "Python",
        "framework": "cerebras-raw",
        "model": "cerebras",
        "model_id": "llama-3.1-70b",
        "model_override": "llama-3.1-70b",
    },
    "cerebras-llama-3.1-8b": {
        "url": "http://localhost:7778/agent",
        "port": 7778,
        "health": "http://localhost:7778/health",
        "type": "raw",
        "language": "Python",
        "framework": "cerebras-raw",
        "model": "cerebras",
        "model_id": "llama-3.1-8b",
        "model_override": "llama-3.1-8b",
    },
}


# Unified test prompts - objective tasks that don't bias toward any framework
# Each test validates specific AG-UI features
TEST_PROMPTS = {
    # === BASIC TESTS ===
    "simple": {
        "type": "single",
        "prompt": "Say hello and introduce yourself briefly in 2-3 sentences.",
        "validates": ["TEXT_MESSAGE_CONTENT", "RUN_STARTED", "RUN_FINISHED"],
    },

    # === TOOL CALLING TESTS ===
    "tool_time": {
        "type": "single",
        "prompt": "What is the current time? Use the time tool to check.",
        "validates": ["TOOL_CALL_START", "TOOL_CALL_ARGS", "TOOL_CALL_END", "TOOL_CALL_RESULT"],
    },
    "tool_calc": {
        "type": "single",
        "prompt": "Calculate 42 * 17 using the calculator tool and tell me the result.",
        "validates": ["TOOL_CALL_START", "TOOL_CALL_ARGS", "TOOL_CALL_END", "TOOL_CALL_RESULT"],
    },

    # === MULTI-TURN CONVERSATION ===
    "multi_turn_memory": {
        "type": "multi",
        "messages": [
            {"role": "user", "content": "My favorite programming language is Python. Remember this."},
            {"role": "user", "content": "What is my favorite programming language?"},
        ],
        "validates": ["context_retention", "MESSAGES_SNAPSHOT", "STATE_SNAPSHOT"],
    },

    # === THINKING/REASONING ===
    "thinking": {
        "type": "single",
        "prompt": "Think step-by-step: If x + 5 = 12, what is x? Show your reasoning process.",
        "validates": ["THINKING_START", "THINKING_CONTENT", "THINKING_END"],
    },

    # === ARTIFACT GENERATION ===
    "artifact": {
        "type": "single",
        "prompt": "Create a simple Python function that adds two numbers. Return it as code.",
        "validates": ["ARTIFACT_START", "ARTIFACT_CONTENT", "ARTIFACT_END"],
    },

    # === HUMAN-IN-THE-LOOP (HITL) ===
    "hitl_approval": {
        "type": "hitl",
        "prompt": "I need to delete important data. You must ask for my approval before proceeding.",
        "hitl_response": {"approved": True, "message": "Yes, you may proceed"},
        "validates": ["HUMAN_INPUT_REQUESTED", "HUMAN_INPUT_RECEIVED"],
    },

    # === ERROR HANDLING ===
    "error_handling": {
        "type": "single",
        "prompt": "Use the 'nonexistent_tool' to do something.",
        "validates": ["ERROR"],
        "expect_error": True,
    },

    # === COMPLEX MULTI-TOOL ===
    "multi_tool": {
        "type": "single",
        "prompt": "First get the current time, then calculate 10 + 20.",
        "validates": ["TOOL_CALL_START", "TOOL_CALL_END"],
        "expect_tools": 2,
    },
}

# Legacy compatibility - extract simple prompt strings
SIMPLE_TEST_PROMPTS = {
    "simple": "Say hello and introduce yourself briefly in 2-3 sentences.",
    "tool_time": "What is the current time? Use the time tool to check.",
    "tool_calc": "Calculate 42 * 17 using the calculator tool and tell me the result.",
}


@dataclass
class TestMetrics:
    """Metrics collected during a test run."""
    name: str
    prompt_type: str
    prompt: str
    success: bool = False
    error: str = None

    # Timing metrics (in milliseconds)
    total_time_ms: float = 0
    time_to_first_event_ms: float = 0
    time_to_first_content_ms: float = 0
    time_to_complete_ms: float = 0

    # Tool metrics
    tool_calls: int = 0
    tool_call_time_ms: float = 0

    # Response metrics
    response_chars: int = 0
    response_tokens_approx: int = 0

    # Token usage (for cost calculation)
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Event counts
    total_events: int = 0
    event_types: set = field(default_factory=set)

    # The actual response
    final_response: str = ""

    # === NEW: Feature detection ===
    has_thinking: bool = False
    has_artifacts: bool = False
    has_hitl: bool = False
    has_state_snapshot: bool = False
    has_error_events: bool = False
    thinking_time_ms: float = 0
    hitl_response_time_ms: float = 0

    # Multi-turn tracking
    is_multi_turn: bool = False
    turn_count: int = 1
    context_retained: bool = False


class HITLMockHandler:
    """Handles Human-in-the-Loop emulation for testing."""

    def __init__(self, test_config: dict):
        self.config = test_config
        self.response_delay_ms = 500  # Simulate human response time

    def should_respond(self, event: dict) -> bool:
        """Check if we should respond to this HITL event."""
        return event.get("type") == "HUMAN_INPUT_REQUESTED"

    def get_response(self, event: dict) -> dict:
        """Generate appropriate HITL response based on the request."""
        if "hitl_response" in self.config:
            return self.config["hitl_response"]

        # Default responses based on question content
        question = event.get("question", "").lower()
        if "approval" in question or "approve" in question:
            return {"approved": True, "message": "Yes, proceed"}
        elif "color" in question:
            return {"input": "blue"}
        elif "name" in question:
            return {"input": "Alice"}
        else:
            return {"input": "I don't know"}


def parse_sse_events(text: str) -> List[Dict[str, Any]]:
    """Parse SSE formatted text into list of events."""
    events = []
    for line in text.split("\n"):
        if line.startswith("data: "):
            try:
                data = json.loads(line[6:])
                events.append(data)
            except json.JSONDecodeError:
                pass
    return events


async def check_health(client: httpx.AsyncClient, name: str, config: dict) -> bool:
    """Check if agent is healthy."""
    try:
        response = await client.get(config["health"], timeout=5.0)
        if response.status_code == 200:
            return True
        return False
    except Exception:
        return False


def save_test_data(run_dir: Path, agent_name: str, run_num: int,
                   prompt_type: str, request_body: dict,
                   events: List[Dict[str, Any]], metrics: TestMetrics):
    """Save test request, streaming response, and metadata to disk."""
    # Create agent directory
    agent_dir = run_dir / agent_name
    agent_dir.mkdir(exist_ok=True)

    # Create test directory
    test_dir = agent_dir / f"run{run_num}-{prompt_type}"
    test_dir.mkdir(exist_ok=True)

    # Save request payload
    with open(test_dir / "request.json", "w") as f:
        json.dump(request_body, f, indent=2)

    # Save streaming events as JSONL (JSON Lines - one event per line)
    with open(test_dir / "response.jsonl", "w") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    # Save test metadata
    metadata = {
        "agent": agent_name,
        "run_number": run_num,
        "prompt_type": prompt_type,
        "prompt": metrics.prompt,
        "success": metrics.success,
        "error": metrics.error,
        "timing": {
            "total_time_ms": metrics.total_time_ms,
            "time_to_first_event_ms": metrics.time_to_first_event_ms,
            "time_to_first_content_ms": metrics.time_to_first_content_ms,
            "time_to_complete_ms": metrics.time_to_complete_ms,
        },
        "tools": {
            "tool_calls": metrics.tool_calls,
            "tool_call_time_ms": metrics.tool_call_time_ms,
        },
        "response": {
            "chars": metrics.response_chars,
            "tokens_approx": metrics.response_tokens_approx,
            "final_text": metrics.final_response,
        },
        "tokens": {
            "input_tokens": metrics.input_tokens,
            "output_tokens": metrics.output_tokens,
            "total_tokens": metrics.total_tokens,
        },
        "events": {
            "total_events": metrics.total_events,
            "event_types": sorted(list(metrics.event_types)),
        }
    }

    with open(test_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


def calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD for the given token usage."""
    if model_id not in MODEL_PRICING:
        return 0.0

    pricing = MODEL_PRICING[model_id]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


async def test_agent(client: httpx.AsyncClient, name: str, config: dict,
                     prompt_type: str, prompt: str, run_dir: Path = None,
                     run_num: int = 1) -> TestMetrics:
    """Test an agent with a prompt and collect detailed metrics."""
    metrics = TestMetrics(name=name, prompt_type=prompt_type, prompt=prompt)

    request_body = {
        "thread_id": f"test-thread-{name}",
        "run_id": f"test-run-{name}-{prompt_type}",
        "messages": [{
            "id": "msg-1",
            "role": "user",
            "content": prompt
        }],
        "state": {},
        "tools": [],
        "context": [],
        "forwardedProps": {}
    }

    # Add model override if specified (for Cerebras multi-model testing)
    if "model_override" in config:
        request_body["model"] = config["model_override"]

    start_time = time.perf_counter()
    first_event_time = None
    first_content_time = None
    tool_start_time = None
    events = []  # Store all events for saving

    try:
        async with client.stream(
            "POST",
            config["url"],
            json=request_body,
            headers={"Accept": "text/event-stream"},
            timeout=120.0
        ) as response:
            full_text = ""
            async for chunk in response.aiter_text():
                current_time = time.perf_counter()
                full_text += chunk

                if first_event_time is None and chunk.strip():
                    first_event_time = current_time

            end_time = time.perf_counter()

            events = parse_sse_events(full_text)
            metrics.total_events = len(events)
            metrics.event_types = {e.get("type") for e in events if "type" in e}

            response_parts = []
            for event in events:
                event_type = event.get("type", "")

                if event_type == "TEXT_MESSAGE_CONTENT" and first_content_time is None:
                    first_content_time = time.perf_counter()

                if event_type == "TEXT_MESSAGE_CONTENT":
                    delta = event.get("delta", "")
                    response_parts.append(delta)

                # Extract token usage from various event types
                # Different frameworks report usage in different places
                if "usage_metadata" in event:
                    usage = event["usage_metadata"]
                    if isinstance(usage, dict):
                        metrics.input_tokens = max(metrics.input_tokens, usage.get("input_tokens", 0))
                        metrics.output_tokens = max(metrics.output_tokens, usage.get("output_tokens", 0))
                        metrics.total_tokens = max(metrics.total_tokens, usage.get("total_tokens", 0))

                # Check for usage in rawEvent (LangGraph pattern)
                if "rawEvent" in event:
                    raw = event["rawEvent"]
                    if isinstance(raw, dict) and "data" in raw:
                        data = raw["data"]
                        if isinstance(data, dict):
                            # LangGraph usage_metadata in chunk
                            if "chunk" in data:
                                chunk = data["chunk"]
                                if isinstance(chunk, dict) and "usage_metadata" in chunk:
                                    usage = chunk["usage_metadata"]
                                    if isinstance(usage, dict):
                                        metrics.input_tokens = max(metrics.input_tokens, usage.get("input_tokens", 0))
                                        metrics.output_tokens = max(metrics.output_tokens, usage.get("output_tokens", 0))
                                        metrics.total_tokens = max(metrics.total_tokens, usage.get("total_tokens", 0))
                            # LangGraph usage_metadata in output
                            if "output" in data:
                                output = data["output"]
                                if isinstance(output, dict) and "usage_metadata" in output:
                                    usage = output["usage_metadata"]
                                    if isinstance(usage, dict):
                                        metrics.input_tokens = max(metrics.input_tokens, usage.get("input_tokens", 0))
                                        metrics.output_tokens = max(metrics.output_tokens, usage.get("output_tokens", 0))
                                        metrics.total_tokens = max(metrics.total_tokens, usage.get("total_tokens", 0))

                elif event_type == "MESSAGES_SNAPSHOT":
                    messages = event.get("messages", [])
                    for msg in reversed(messages):
                        if isinstance(msg, dict) and msg.get("role") == "assistant":
                            content = msg.get("content", "")
                            if content and content not in response_parts:
                                response_parts.append(content)
                                if first_content_time is None:
                                    first_content_time = time.perf_counter()
                            break

                elif event_type == "TOOL_CALL_START":
                    metrics.tool_calls += 1
                    tool_start_time = time.perf_counter()

                elif event_type == "TOOL_CALL_RESULT" and tool_start_time:
                    metrics.tool_call_time_ms += (time.perf_counter() - tool_start_time) * 1000
                    tool_start_time = None

            metrics.final_response = "".join(response_parts)
            metrics.response_chars = len(metrics.final_response)
            metrics.response_tokens_approx = metrics.response_chars // 4

            metrics.total_time_ms = (end_time - start_time) * 1000
            if first_event_time:
                metrics.time_to_first_event_ms = (first_event_time - start_time) * 1000
            if first_content_time:
                metrics.time_to_first_content_ms = (first_content_time - start_time) * 1000
            metrics.time_to_complete_ms = metrics.total_time_ms

            metrics.success = True

    except Exception as e:
        metrics.error = str(e)
        metrics.total_time_ms = (time.perf_counter() - start_time) * 1000

    # Save test data if run_dir is provided
    if run_dir and run_num:
        save_test_data(run_dir, name, run_num, prompt_type, request_body, events, metrics)

    return metrics


def median(values: List[float]) -> float:
    """Calculate median of a list of values."""
    if not values:
        return 0.0
    return statistics.median(values)


def print_comparison_by_model(all_metrics: Dict[str, List[TestMetrics]]):
    """Print comparison tables grouped by model (same model, different frameworks)."""
    print("\n" + "=" * 120)
    print("COMPARISON BY MODEL (Same model, different frameworks)")
    print("=" * 120)

    for model_key, model_name in MODELS.items():
        print(f"\n{'─' * 100}")
        print(f"🔷 {model_key.upper()} MODEL ({model_name})")
        print(f"{'─' * 100}")

        # Get all agents using this model
        model_agents = {name: config for name, config in AGENTS.items()
                       if config.get("model") == model_key}

        if not model_agents:
            print("  No agents for this model")
            continue

        # Calculate stats for each agent
        agent_stats = []
        for name in model_agents:
            if name not in all_metrics:
                continue
            metrics_list = all_metrics[name]
            successful = [m for m in metrics_list if m.success]
            if not successful:
                continue

            config = AGENTS[name]
            agent_stats.append({
                "name": name,
                "framework": config.get("framework", name),
                "type": config.get("type", "unknown"),
                "median_time": median([m.total_time_ms for m in successful]),
                "ttfb": median([m.time_to_first_event_ms for m in successful]),
                "ttfc": median([m.time_to_first_content_ms for m in successful]),
                "tools": sum(m.tool_calls for m in successful),
                "chars": median([m.response_chars for m in successful]),
                "tests": len(successful),
            })

        if not agent_stats:
            print("  No successful tests for this model")
            continue

        # Sort by median time
        agent_stats.sort(key=lambda x: x["median_time"])

        print(f"\n  {'Framework':<20} {'Type':<10} {'Median':<10} {'TTFB':<10} {'TTFC':<10} {'Tests':<8}")
        print(f"  {'-' * 78}")

        for stat in agent_stats:
            print(f"  {stat['framework']:<20} {stat['type']:<10} {stat['median_time']:>6.0f}ms  {stat['ttfb']:>6.0f}ms  {stat['ttfc']:>6.0f}ms  {stat['tests']:>4}")

        # Winner for this model
        if agent_stats:
            winner = agent_stats[0]
            print(f"\n  🏆 Fastest {model_key}: {winner['framework']} ({winner['median_time']:.0f}ms)")


def print_comparison_by_framework(all_metrics: Dict[str, List[TestMetrics]]):
    """Print comparison tables grouped by framework (same framework, different models)."""
    print("\n" + "=" * 120)
    print("COMPARISON BY FRAMEWORK (Same framework, different models)")
    print("=" * 120)

    # Get unique frameworks
    frameworks = set(config.get("framework") for config in AGENTS.values())

    for framework in sorted(frameworks):
        # Get all agents for this framework
        framework_agents = {name: config for name, config in AGENTS.items()
                          if config.get("framework") == framework}

        # Skip single-model frameworks in this comparison
        if len(framework_agents) <= 1:
            continue

        print(f"\n{'─' * 100}")
        print(f"📦 {framework.upper()}")
        print(f"{'─' * 100}")

        agent_stats = []
        for name, config in framework_agents.items():
            if name not in all_metrics:
                continue
            metrics_list = all_metrics[name]
            successful = [m for m in metrics_list if m.success]
            if not successful:
                continue

            agent_stats.append({
                "name": name,
                "model": config.get("model", "unknown"),
                "model_id": config.get("model_id", "unknown"),
                "median_time": median([m.total_time_ms for m in successful]),
                "ttfb": median([m.time_to_first_event_ms for m in successful]),
                "chars": median([m.response_chars for m in successful]),
                "tests": len(successful),
            })

        if not agent_stats:
            print("  No successful tests")
            continue

        agent_stats.sort(key=lambda x: x["median_time"])

        print(f"\n  {'Model':<10} {'Model ID':<30} {'Median':<10} {'TTFB':<10} {'Resp Len':<10}")
        print(f"  {'-' * 80}")

        for stat in agent_stats:
            print(f"  {stat['model']:<10} {stat['model_id']:<30} {stat['median_time']:>6.0f}ms  {stat['ttfb']:>6.0f}ms  {stat['chars']:>6.0f}")


def print_overall_ranking(all_metrics: Dict[str, List[TestMetrics]]):
    """Print overall ranking across all agents."""
    print("\n" + "=" * 120)
    print("OVERALL RANKING (All framework+model combinations)")
    print("=" * 120)

    agent_stats = []
    for name, metrics_list in all_metrics.items():
        successful = [m for m in metrics_list if m.success]
        if not successful:
            continue

        config = AGENTS.get(name, {})
        agent_stats.append({
            "name": name,
            "framework": config.get("framework", name),
            "model": config.get("model", "unknown"),
            "model_id": config.get("model_id", "unknown"),
            "type": config.get("type", "unknown"),
            "median_time": median([m.total_time_ms for m in successful]),
            "ttfb": median([m.time_to_first_event_ms for m in successful]),
            "ttfc": median([m.time_to_first_content_ms for m in successful]),
            "tests": len(successful),
            "passed": len(successful),
            "total": len(metrics_list),
        })

    agent_stats.sort(key=lambda x: x["median_time"])

    print(f"\n{'Rank':<6} {'Agent':<25} {'Framework':<15} {'Model':<10} {'Median':<10} {'TTFB':<10} {'Tests':<8}")
    print("-" * 100)

    for i, stat in enumerate(agent_stats, 1):
        print(f"{i:<6} {stat['name']:<25} {stat['framework']:<15} {stat['model']:<10} {stat['median_time']:>6.0f}ms  {stat['ttfb']:>6.0f}ms  {stat['passed']}/{stat['total']}")


def print_test_breakdown(all_metrics: Dict[str, List[TestMetrics]]):
    """Print detailed breakdown by test type."""
    print("\n" + "-" * 120)
    print(f"DETAILED BREAKDOWN BY TEST TYPE (Median of {NUM_RUNS} runs)")
    print("-" * 120)

    for prompt_type in TEST_PROMPTS.keys():
        print(f"\n📊 {prompt_type.upper()} TEST")
        print(f"{'Agent':<25} {'Framework':<15} {'Model':<10} {'Median':<10} {'Tools':<8} {'Status':<8}")
        print("-" * 90)

        type_results = []
        for name, metrics_list in all_metrics.items():
            runs = [m for m in metrics_list if m.prompt_type == prompt_type]
            successful_runs = [m for m in runs if m.success]

            config = AGENTS.get(name, {})
            framework = config.get("framework", name)
            model = config.get("model", "unknown")

            if successful_runs:
                median_time = median([m.total_time_ms for m in successful_runs])
                total_tools = sum(m.tool_calls for m in successful_runs)
                type_results.append((name, framework, model, median_time, total_tools // len(successful_runs), True))
            elif runs:
                type_results.append((name, framework, model, float('inf'), 0, False))

        type_results.sort(key=lambda x: x[3])

        for name, framework, model, med_time, tools, success in type_results:
            status = "✅" if success else "❌"
            tool_str = str(tools) if tools > 0 else "-"
            time_str = f"{med_time:>6.0f}ms" if med_time != float('inf') else "   N/A"
            print(f"{name:<25} {framework:<15} {model:<10} {time_str}    {tool_str:<8} {status}")


def print_startup_times(startup_times: Optional[Dict[str, int]]):
    """Print startup time metrics."""
    print("\n" + "-" * 100)
    print("STARTUP TIMES (Cold Start)")
    print("-" * 100)

    if not startup_times:
        print("\n  No startup times available. Run ./start_all.sh to measure.")
        return

    valid_times = {k: v for k, v in startup_times.items() if v >= 0}
    failed = {k: v for k, v in startup_times.items() if v < 0}

    if valid_times:
        sorted_times = sorted(valid_times.items(), key=lambda x: x[1])
        print(f"\n{'Framework':<20} {'Startup Time':<15} {'Status':<10}")
        print("-" * 50)

        for name, ms in sorted_times:
            print(f"{name:<20} {ms:>8} ms      ✅")

        for name in failed:
            print(f"{name:<20} {'N/A':>8}         ❌ failed")

        times = list(valid_times.values())
        avg_time = sum(times) / len(times)
        fastest = min(sorted_times, key=lambda x: x[1])
        slowest = max(sorted_times, key=lambda x: x[1])

        print(f"\n  🚀 Fastest startup: {fastest[0]} ({fastest[1]} ms)")
        print(f"  🐢 Slowest startup: {slowest[0]} ({slowest[1]} ms)")
        print(f"  📊 Average startup: {avg_time:.0f} ms")


def load_startup_times() -> Optional[Dict[str, int]]:
    """Load startup times from JSON file."""
    startup_file = Path(__file__).parent / "logs" / "startup_times.json"
    if startup_file.exists():
        try:
            with open(startup_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None


def analyze_results(results: List[TestMetrics]) -> Dict[str, Any]:
    """Analyze test results for AG-UI compliance."""
    analysis = {
        "total_tests": len(results),
        "successful": 0,
        "failed": 0,
        "frameworks": {},
    }

    required_events = {"RUN_STARTED", "RUN_FINISHED"}
    message_events = {"TEXT_MESSAGE_START", "TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_END"}

    for result in results:
        name = result.name
        if name not in analysis["frameworks"]:
            analysis["frameworks"][name] = {
                "tests": 0,
                "passed": 0,
                "has_lifecycle": False,
                "has_messages": False,
                "has_tools": False,
                "event_types_seen": set(),
            }

        fw = analysis["frameworks"][name]
        fw["tests"] += 1
        fw["event_types_seen"].update(result.event_types)

        if result.success:
            analysis["successful"] += 1
            fw["passed"] += 1

            if required_events.issubset(result.event_types):
                fw["has_lifecycle"] = True

            if message_events.issubset(result.event_types):
                fw["has_messages"] = True
            elif "MESSAGES_SNAPSHOT" in result.event_types:
                fw["has_messages"] = True

            tool_events = {"TOOL_CALL_START", "TOOL_CALL_END"}
            if tool_events.issubset(result.event_types):
                fw["has_tools"] = True
        else:
            analysis["failed"] += 1

    return analysis


def print_cost_breakdown(all_metrics: Dict[str, List[TestMetrics]]):
    """Print cost breakdown by framework, model, and total."""
    print("\n" + "=" * 120)
    print("💰 COST BREAKDOWN (Token Usage & Pricing)")
    print("=" * 120)

    # Aggregate costs by framework -> model
    framework_costs = {}
    model_costs = {}
    total_cost = 0.0
    total_input_tokens = 0
    total_output_tokens = 0

    for name, metrics_list in all_metrics.items():
        config = AGENTS.get(name, {})
        framework = config.get("framework", "unknown")
        model_id = config.get("model_id", "unknown")

        for metrics in metrics_list:
            if not metrics.success or metrics.input_tokens == 0:
                continue

            cost = calculate_cost(model_id, metrics.input_tokens, metrics.output_tokens)

            # Aggregate by framework
            if framework not in framework_costs:
                framework_costs[framework] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "models": {}
                }
            framework_costs[framework]["cost"] += cost
            framework_costs[framework]["input_tokens"] += metrics.input_tokens
            framework_costs[framework]["output_tokens"] += metrics.output_tokens

            # Aggregate by framework -> model
            if model_id not in framework_costs[framework]["models"]:
                framework_costs[framework]["models"][model_id] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "tests": 0
                }
            framework_costs[framework]["models"][model_id]["cost"] += cost
            framework_costs[framework]["models"][model_id]["input_tokens"] += metrics.input_tokens
            framework_costs[framework]["models"][model_id]["output_tokens"] += metrics.output_tokens
            framework_costs[framework]["models"][model_id]["tests"] += 1

            # Aggregate by model
            if model_id not in model_costs:
                model_costs[model_id] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "tests": 0
                }
            model_costs[model_id]["cost"] += cost
            model_costs[model_id]["input_tokens"] += metrics.input_tokens
            model_costs[model_id]["output_tokens"] += metrics.output_tokens
            model_costs[model_id]["tests"] += 1

            total_cost += cost
            total_input_tokens += metrics.input_tokens
            total_output_tokens += metrics.output_tokens

    # Print by model
    print("\n📊 COST BY MODEL")
    print("-" * 100)
    print(f"{'Model':<30} {'Tests':<8} {'Input Tokens':<15} {'Output Tokens':<15} {'Total Cost':<12}")
    print("-" * 100)

    for model_id in sorted(model_costs.keys()):
        stats = model_costs[model_id]
        print(f"{model_id:<30} {stats['tests']:<8} {stats['input_tokens']:>14,} {stats['output_tokens']:>14,} ${stats['cost']:>10.6f}")

    # Print by framework
    print("\n📊 COST BY FRAMEWORK")
    print("-" * 100)

    for framework in sorted(framework_costs.keys()):
        stats = framework_costs[framework]
        print(f"\n🔷 {framework.upper()}")
        print(f"   Total: ${stats['cost']:.6f} ({stats['input_tokens']:,} in / {stats['output_tokens']:,} out)")

        for model_id in sorted(stats["models"].keys()):
            model_stats = stats["models"][model_id]
            print(f"     - {model_id}: ${model_stats['cost']:.6f} ({model_stats['tests']} tests)")

    # Print total
    print("\n" + "=" * 100)
    print(f"💵 TOTAL BENCHMARK COST: ${total_cost:.6f}")
    print(f"   Input Tokens:  {total_input_tokens:,}")
    print(f"   Output Tokens: {total_output_tokens:,}")
    print(f"   Total Tokens:  {total_input_tokens + total_output_tokens:,}")
    print("=" * 100)

    # Cost per 1000 tests estimate
    if total_cost > 0:
        num_successful = sum(len([m for m in metrics_list if m.success and m.input_tokens > 0])
                           for metrics_list in all_metrics.values())
        if num_successful > 0:
            cost_per_1k = (total_cost / num_successful) * 1000
            print(f"\n📈 Estimated cost per 1,000 similar tests: ${cost_per_1k:.2f}")


async def main():
    print("🧪 AG-UI Multi-Framework Multi-Model Test Suite")
    print("=" * 120)
    print(f"Testing {len(AGENTS)} agent configurations across {len(MODELS)} models")

    # Create timestamped run directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = BENCHMARK_RUNS_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Saving detailed logs to: {run_dir}")

    # Save run metadata
    run_metadata = {
        "timestamp": timestamp,
        "start_time": datetime.now().isoformat(),
        "num_runs": NUM_RUNS,
        "models": MODELS,
        "test_prompts": TEST_PROMPTS,
        "total_agents": len(AGENTS),
    }
    with open(run_dir / "run-metadata.json", "w") as f:
        json.dump(run_metadata, f, indent=2)

    async with httpx.AsyncClient() as client:
        # Step 1: Health checks (group by port to avoid duplicate checks)
        print("\n📡 Checking agent health...")
        checked_ports = {}
        healthy_agents = {}

        for name, config in AGENTS.items():
            port = config["port"]
            if port in checked_ports:
                # Already checked this port
                if checked_ports[port]:
                    healthy_agents[name] = config
                    print(f"  ✅ {name}: healthy (port {port})")
                else:
                    print(f"  ❌ {name}: unhealthy (port {port})")
            else:
                # Check health
                is_healthy = await check_health(client, name, config)
                checked_ports[port] = is_healthy
                if is_healthy:
                    healthy_agents[name] = config
                    print(f"  ✅ {name}: healthy")
                else:
                    print(f"  ❌ {name}: not reachable")

        if not healthy_agents:
            print("\n❌ No agents are running!")
            sys.exit(1)

        print(f"\n✅ {len(healthy_agents)}/{len(AGENTS)} agents healthy")

        # Step 2: Run tests
        total_tests = len(healthy_agents) * len(TEST_PROMPTS) * NUM_RUNS
        print(f"\n🧪 Running AG-UI protocol tests ({NUM_RUNS} runs each, {total_tests} total)...")

        all_metrics: Dict[str, List[TestMetrics]] = {name: [] for name in healthy_agents}

        for run in range(NUM_RUNS):
            print(f"\n  === Run {run + 1}/{NUM_RUNS} ===")

            # Build all tasks for parallel execution
            tasks = []
            task_info = []  # Track (name, prompt_type) for each task

            for name, config in healthy_agents.items():
                for prompt_type, test_config in TEST_PROMPTS.items():
                    # Extract actual prompt string from test config
                    if isinstance(test_config, dict) and "prompt" in test_config:
                        prompt = test_config["prompt"]
                    else:
                        prompt = test_config  # Fallback for simple string prompts

                    tasks.append(test_agent(client, name, config, prompt_type, prompt, run_dir, run + 1))
                    task_info.append((name, prompt_type))

            # Run all tests in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Organize results by agent and model for display
            agent_results: Dict[str, List[TestMetrics]] = {name: [] for name in healthy_agents}

            for i, result in enumerate(results):
                name, prompt_type = task_info[i]
                if isinstance(result, Exception):
                    # Extract prompt string from test config
                    test_config = TEST_PROMPTS[prompt_type]
                    prompt_str = test_config["prompt"] if isinstance(test_config, dict) and "prompt" in test_config else test_config
                    metrics = TestMetrics(name=name, prompt_type=prompt_type, prompt=prompt_str)
                    metrics.error = str(result)
                    agent_results[name].append(metrics)
                    all_metrics[name].append(metrics)
                else:
                    agent_results[name].append(result)
                    all_metrics[name].append(result)

            # Print results grouped by model
            for model_key in MODELS.keys():
                model_agents = [n for n in healthy_agents if healthy_agents[n].get("model") == model_key]
                if not model_agents:
                    continue

                print(f"\n  [{model_key.upper()}]")
                for name in model_agents:
                    agent_res = agent_results[name]
                    passed = sum(1 for r in agent_res if r.success)
                    times = [f"{r.total_time_ms:.0f}ms" for r in agent_res]
                    status = "✅" if passed == len(agent_res) else "⚠️"
                    print(f"    {status} {name}: {passed}/{len(agent_res)} ({', '.join(times)})")

        # Step 3: Analyze and report
        flat_results = [m for metrics_list in all_metrics.values() for m in metrics_list]
        analysis = analyze_results(flat_results)

        print("\n" + "=" * 120)
        print("AG-UI MULTI-FRAMEWORK MULTI-MODEL TEST REPORT")
        print("=" * 120)
        print(f"\nTotal Tests: {analysis['total_tests']}")
        print(f"Passed: {analysis['successful']}")
        print(f"Failed: {analysis['failed']}")

        # Print comparison reports
        print_comparison_by_model(all_metrics)
        print_comparison_by_framework(all_metrics)
        print_overall_ranking(all_metrics)
        print_test_breakdown(all_metrics)
        print_cost_breakdown(all_metrics)
        print_startup_times(load_startup_times())

        # Final verdict
        print("\n" + "=" * 120)
        print("VERDICT")
        print("=" * 120)

        # Best per model
        print("\n🏆 FASTEST BY MODEL:")
        for model_key in MODELS.keys():
            model_agents = {n: all_metrics[n] for n in all_metrics
                          if AGENTS.get(n, {}).get("model") == model_key}
            if model_agents:
                best = None
                best_time = float('inf')
                for name, metrics_list in model_agents.items():
                    successful = [m for m in metrics_list if m.success]
                    if successful:
                        med = median([m.total_time_ms for m in successful])
                        if med < best_time:
                            best_time = med
                            best = name
                if best:
                    framework = AGENTS.get(best, {}).get("framework", best)
                    print(f"  {model_key.upper()}: {framework} ({best_time:.0f}ms)")

        # Overall best
        all_times = {}
        for name, metrics_list in all_metrics.items():
            successful = [m for m in metrics_list if m.success]
            if successful:
                all_times[name] = median([m.total_time_ms for m in successful])

        if all_times:
            fastest = min(all_times.items(), key=lambda x: x[1])
            slowest = max(all_times.items(), key=lambda x: x[1])
            fastest_config = AGENTS.get(fastest[0], {})
            slowest_config = AGENTS.get(slowest[0], {})
            print(f"\n🥇 Overall Fastest: {fastest[0]} ({fastest[1]:.0f}ms) - {fastest_config.get('framework')} + {fastest_config.get('model')}")
            print(f"🐢 Overall Slowest: {slowest[0]} ({slowest[1]:.0f}ms) - {slowest_config.get('framework')} + {slowest_config.get('model')}")

        # Save summary to run directory
        summary = {
            "timestamp": timestamp,
            "end_time": datetime.now().isoformat(),
            "analysis": {
                "total_tests": analysis["total_tests"],
                "successful": analysis["successful"],
                "failed": analysis["failed"],
            },
            "fastest_by_model": {},
            "overall_fastest": {
                "name": fastest[0] if all_times else None,
                "time_ms": fastest[1] if all_times else None,
                "framework": fastest_config.get("framework") if all_times else None,
                "model": fastest_config.get("model") if all_times else None,
            },
            "overall_slowest": {
                "name": slowest[0] if all_times else None,
                "time_ms": slowest[1] if all_times else None,
                "framework": slowest_config.get("framework") if all_times else None,
                "model": slowest_config.get("model") if all_times else None,
            },
            "all_results": {}
        }

        # Add fastest by model
        for model_key in MODELS.keys():
            model_agents = {n: all_metrics[n] for n in all_metrics
                          if AGENTS.get(n, {}).get("model") == model_key}
            if model_agents:
                best = None
                best_time = float('inf')
                for name, metrics_list in model_agents.items():
                    successful = [m for m in metrics_list if m.success]
                    if successful:
                        med = median([m.total_time_ms for m in successful])
                        if med < best_time:
                            best_time = med
                            best = name
                if best:
                    framework = AGENTS.get(best, {}).get("framework", best)
                    summary["fastest_by_model"][model_key] = {
                        "name": best,
                        "framework": framework,
                        "time_ms": best_time
                    }

        # Add all agent results
        for name, metrics_list in all_metrics.items():
            successful = [m for m in metrics_list if m.success]
            if successful:
                config = AGENTS.get(name, {})
                summary["all_results"][name] = {
                    "framework": config.get("framework", name),
                    "model": config.get("model", "unknown"),
                    "model_id": config.get("model_id", "unknown"),
                    "type": config.get("type", "unknown"),
                    "median_time_ms": median([m.total_time_ms for m in successful]),
                    "median_ttfb_ms": median([m.time_to_first_event_ms for m in successful]),
                    "median_ttfc_ms": median([m.time_to_first_content_ms for m in successful]),
                    "tests_passed": len(successful),
                    "tests_total": len(metrics_list),
                }

        with open(run_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n📁 Full benchmark data saved to: {run_dir}")
        print(f"   - Individual test requests: */request.json")
        print(f"   - Streaming responses (JSONL): */response.jsonl")
        print(f"   - Test metadata: */metadata.json")
        print(f"   - Run summary: summary.json")


if __name__ == "__main__":
    asyncio.run(main())

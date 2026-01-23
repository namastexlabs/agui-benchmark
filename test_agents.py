#!/usr/bin/env python3
"""
AG-UI Multi-Framework Test Script with Performance Metrics

Tests all agent frameworks for AG-UI protocol compliance and compares performance.
Run with: python test_agents.py
"""

import httpx
import asyncio
import json
import sys
import time
from typing import Dict, List, Any
from dataclasses import dataclass, field


# Agent configurations
AGENTS = {
    # Python Agent Frameworks (Native AG-UI)
    "agno": {
        "url": "http://localhost:7771/agui",
        "port": 7771,
        "health": "http://localhost:7771/health",
        "type": "native",
        "language": "Python",
    },
    "langgraph": {
        "url": "http://localhost:7772/agent",
        "port": 7772,
        "health": "http://localhost:7772/health",
        "type": "native",
        "language": "Python",
    },
    "crewai": {
        "url": "http://localhost:7773/agent",
        "port": 7773,
        "health": "http://localhost:7773/health",
        "type": "native",
        "language": "Python",
    },
    "pydantic-ai": {
        "url": "http://localhost:7774/",
        "port": 7774,
        "health": "http://localhost:7774/health",
        "type": "native",
        "language": "Python",
    },
    "llamaindex": {
        "url": "http://localhost:7780/agent",
        "port": 7780,
        "health": "http://localhost:7780/health",
        "type": "native",
        "language": "Python",
    },
    "ag2": {
        "url": "http://localhost:7781/agent",
        "port": 7781,
        "health": "http://localhost:7781/health",
        "type": "wrapped",
        "language": "Python",
    },
    "google-adk": {
        "url": "http://localhost:7782/agent",
        "port": 7782,
        "health": "http://localhost:7782/health",
        "type": "native",
        "language": "Python",
    },
    # Raw LLM APIs (AG-UI Wrapped)
    "openai-raw": {
        "url": "http://localhost:7775/agent",
        "port": 7775,
        "health": "http://localhost:7775/health",
        "type": "wrapped",
        "language": "Python",
        "model": "GPT-5.2",
    },
    "anthropic-raw": {
        "url": "http://localhost:7776/agent",
        "port": 7776,
        "health": "http://localhost:7776/health",
        "type": "wrapped",
        "language": "Python",
        "model": "Claude Haiku 4.5",
    },
    "gemini-raw": {
        "url": "http://localhost:7777/agent",
        "port": 7777,
        "health": "http://localhost:7777/health",
        "type": "wrapped",
        "language": "Python",
        "model": "Gemini 2.5 Flash",
    },
    # TypeScript Agents (AG-UI Wrapped)
    "vercel-ai-sdk": {
        "url": "http://localhost:7779/agent",
        "port": 7779,
        "health": "http://localhost:7779/health",
        "type": "wrapped",
        "language": "TypeScript",
        "model": "Claude Haiku 4.5",
    },
}


# Test messages - categorized by type
TEST_PROMPTS = {
    "simple": "Hello! What framework are you running on?",
    "tool_time": "What time is it right now?",
    "tool_calc": "Calculate 42 * 17 for me",
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
    tool_call_time_ms: float = 0  # Time from TOOL_CALL_START to TOOL_CALL_RESULT

    # Response metrics
    response_chars: int = 0
    response_tokens_approx: int = 0  # Rough estimate: chars / 4

    # Event counts
    total_events: int = 0
    event_types: set = field(default_factory=set)

    # The actual response
    final_response: str = ""


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
            print(f"  ✅ {name}: healthy")
            return True
        print(f"  ❌ {name}: unhealthy (status {response.status_code})")
        return False
    except Exception as e:
        print(f"  ❌ {name}: not reachable ({e})")
        return False


async def test_agent(client: httpx.AsyncClient, name: str, config: dict,
                     prompt_type: str, prompt: str) -> TestMetrics:
    """Test an agent with a prompt and collect detailed metrics."""
    metrics = TestMetrics(name=name, prompt_type=prompt_type, prompt=prompt)

    # Full AG-UI request format
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

    start_time = time.perf_counter()
    first_event_time = None
    first_content_time = None
    tool_start_time = None

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

                # Track first event time
                if first_event_time is None and chunk.strip():
                    first_event_time = current_time

            end_time = time.perf_counter()

            events = parse_sse_events(full_text)
            metrics.total_events = len(events)
            metrics.event_types = {e.get("type") for e in events if "type" in e}

            # Process events for metrics
            response_parts = []
            for event in events:
                event_type = event.get("type", "")

                # Track time to first content
                if event_type == "TEXT_MESSAGE_CONTENT" and first_content_time is None:
                    first_content_time = time.perf_counter()

                # Collect response text
                if event_type == "TEXT_MESSAGE_CONTENT":
                    delta = event.get("delta", "")
                    response_parts.append(delta)

                # Handle MESSAGES_SNAPSHOT (CrewAI pattern)
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

                # Track tool calls
                elif event_type == "TOOL_CALL_START":
                    metrics.tool_calls += 1
                    tool_start_time = time.perf_counter()

                elif event_type == "TOOL_CALL_RESULT" and tool_start_time:
                    metrics.tool_call_time_ms += (time.perf_counter() - tool_start_time) * 1000
                    tool_start_time = None

            metrics.final_response = "".join(response_parts)
            metrics.response_chars = len(metrics.final_response)
            metrics.response_tokens_approx = metrics.response_chars // 4

            # Calculate timing metrics
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

    return metrics


def print_metrics_table(all_metrics: Dict[str, List[TestMetrics]]):
    """Print a comparison table of metrics across frameworks."""
    print("\n" + "=" * 100)
    print("PERFORMANCE COMPARISON")
    print("=" * 100)

    # Calculate averages per framework
    framework_stats = {}
    for name, metrics_list in all_metrics.items():
        successful = [m for m in metrics_list if m.success]
        if not successful:
            continue

        framework_stats[name] = {
            "total_time_avg": sum(m.total_time_ms for m in successful) / len(successful),
            "ttfb_avg": sum(m.time_to_first_event_ms for m in successful) / len(successful),
            "ttfc_avg": sum(m.time_to_first_content_ms for m in successful) / len(successful),
            "tool_time_avg": sum(m.tool_call_time_ms for m in successful if m.tool_calls > 0) / max(1, len([m for m in successful if m.tool_calls > 0])),
            "response_chars_avg": sum(m.response_chars for m in successful) / len(successful),
            "tool_calls": sum(m.tool_calls for m in successful),
            "tests": len(successful),
            "events_avg": sum(m.total_events for m in successful) / len(successful),
        }

    # Sort by average total time
    sorted_frameworks = sorted(framework_stats.items(), key=lambda x: x[1]["total_time_avg"])

    # Print header
    print(f"\n{'Framework':<15} {'Avg Time':<12} {'TTFB':<10} {'TTFC':<10} {'Tool Time':<12} {'Resp Chars':<12} {'Events':<8}")
    print("-" * 100)

    for name, stats in sorted_frameworks:
        print(f"{name:<15} {stats['total_time_avg']:>8.0f}ms  {stats['ttfb_avg']:>6.0f}ms  {stats['ttfc_avg']:>6.0f}ms  {stats['tool_time_avg']:>8.0f}ms   {stats['response_chars_avg']:>8.0f}     {stats['events_avg']:>5.0f}")

    print("\nLegend: TTFB = Time to First Byte, TTFC = Time to First Content")

    # Detailed per-test breakdown
    print("\n" + "-" * 100)
    print("DETAILED BREAKDOWN BY TEST TYPE")
    print("-" * 100)

    for prompt_type in TEST_PROMPTS.keys():
        print(f"\n📊 {prompt_type.upper()} TEST")
        print(f"{'Framework':<15} {'Time (ms)':<12} {'Tool Calls':<12} {'Response Len':<12} {'Status':<10}")
        print("-" * 60)

        type_results = []
        for name, metrics_list in all_metrics.items():
            for m in metrics_list:
                if m.prompt_type == prompt_type:
                    type_results.append((name, m))
                    break

        # Sort by time
        type_results.sort(key=lambda x: x[1].total_time_ms if x[1].success else float('inf'))

        for name, m in type_results:
            status = "✅" if m.success else "❌"
            tool_str = str(m.tool_calls) if m.tool_calls > 0 else "-"
            print(f"{name:<15} {m.total_time_ms:>8.0f}     {tool_str:<12} {m.response_chars:<12} {status}")


def print_framework_report(analysis: Dict[str, Any], all_metrics: Dict[str, List[TestMetrics]]):
    """Print detailed framework compliance report."""
    print("\n" + "-" * 100)
    print("FRAMEWORK COMPLIANCE & FEATURES")
    print("-" * 100)

    for name, fw in analysis["frameworks"].items():
        config = AGENTS.get(name, {})
        lang = config.get("language", "Unknown")
        agent_type = config.get("type", "unknown")
        model = config.get("model", "Claude Haiku 4.5")

        print(f"\n📦 {name.upper()} ({lang}, {agent_type})")
        print(f"   Model: {model}")
        print(f"   Tests: {fw['passed']}/{fw['tests']} passed")
        print(f"   Lifecycle: {'✅' if fw['has_lifecycle'] else '❌'}  Messages: {'✅' if fw['has_messages'] else '❌'}  Tools: {'✅' if fw['has_tools'] else '⚠️'}")

        # Get metrics for this framework
        if name in all_metrics:
            metrics_list = all_metrics[name]
            successful = [m for m in metrics_list if m.success]
            if successful:
                avg_time = sum(m.total_time_ms for m in successful) / len(successful)
                avg_chars = sum(m.response_chars for m in successful) / len(successful)
                print(f"   Avg Response Time: {avg_time:.0f}ms  Avg Response Length: {avg_chars:.0f} chars")


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


def print_sample_responses(all_metrics: Dict[str, List[TestMetrics]]):
    """Print sample responses from each framework."""
    print("\n" + "-" * 100)
    print("SAMPLE RESPONSES")
    print("-" * 100)

    for name, metrics_list in all_metrics.items():
        # Get the "simple" test response
        for m in metrics_list:
            if m.prompt_type == "simple" and m.success:
                response = m.final_response[:250] + "..." if len(m.final_response) > 250 else m.final_response
                response = response or "(empty response)"
                print(f"\n📦 {name.upper()}")
                print(f"   {response}")
                break


async def main():
    print("🧪 AG-UI Multi-Framework Test Suite with Performance Metrics")
    print("=" * 100)

    async with httpx.AsyncClient() as client:
        # Step 1: Health checks
        print("\n📡 Checking agent health...")
        healthy_agents = {}
        for name, config in AGENTS.items():
            if await check_health(client, name, config):
                healthy_agents[name] = config

        if not healthy_agents:
            print("\n❌ No agents are running!")
            sys.exit(1)

        print(f"\n✅ {len(healthy_agents)}/{len(AGENTS)} agents healthy")

        # Step 2: Run tests IN PARALLEL
        print("\n🧪 Running AG-UI protocol tests (parallel)...")

        tasks = []
        task_info = []
        for name, config in healthy_agents.items():
            for prompt_type, prompt in TEST_PROMPTS.items():
                tasks.append(test_agent(client, name, config, prompt_type, prompt))
                task_info.append((name, prompt_type))

        print(f"  Running {len(tasks)} tests in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Organize results by framework
        all_metrics: Dict[str, List[TestMetrics]] = {name: [] for name in healthy_agents}

        current_agent = None
        for i, result in enumerate(results):
            name, prompt_type = task_info[i]
            if name != current_agent:
                current_agent = name
                print(f"\n  {name}:")

            if isinstance(result, Exception):
                print(f"    ❌ {prompt_type}: error - {result}")
                metrics = TestMetrics(name=name, prompt_type=prompt_type, prompt=TEST_PROMPTS[prompt_type])
                metrics.error = str(result)
                all_metrics[name].append(metrics)
            else:
                status = "✅" if result.success else "❌"
                time_str = f"{result.total_time_ms:.0f}ms"
                tool_str = f" ({result.tool_calls} tools)" if result.tool_calls > 0 else ""
                print(f"    {status} {prompt_type}: {time_str}{tool_str}")
                all_metrics[name].append(result)

        # Step 3: Analyze and report
        flat_results = [m for metrics_list in all_metrics.values() for m in metrics_list]
        analysis = analyze_results(flat_results)

        # Print reports
        print("\n" + "=" * 100)
        print("AG-UI MULTI-FRAMEWORK TEST REPORT")
        print("=" * 100)
        print(f"\nTotal Tests: {analysis['total_tests']}")
        print(f"Passed: {analysis['successful']}")
        print(f"Failed: {analysis['failed']}")

        print_metrics_table(all_metrics)
        print_framework_report(analysis, all_metrics)
        print_sample_responses(all_metrics)

        # Final verdict
        print("\n" + "=" * 100)
        print("VERDICT")
        print("=" * 100)

        all_have_lifecycle = all(fw["has_lifecycle"] for fw in analysis["frameworks"].values())
        all_have_messages = all(fw["has_messages"] for fw in analysis["frameworks"].values())

        if all_have_lifecycle and all_have_messages:
            print("\n✅ ALL FRAMEWORKS SUPPORT AG-UI PROTOCOL")
            print("   Omni can be framework-agnostic via AG-UI!")
        else:
            print("\n⚠️  SOME FRAMEWORKS HAVE INCOMPLETE AG-UI SUPPORT")
            for name, fw in analysis["frameworks"].items():
                if not fw["has_lifecycle"] or not fw["has_messages"]:
                    print(f"   - {name}: missing events")

        # Performance winner
        framework_times = {}
        for name, metrics_list in all_metrics.items():
            successful = [m for m in metrics_list if m.success]
            if successful:
                framework_times[name] = sum(m.total_time_ms for m in successful) / len(successful)

        if framework_times:
            fastest = min(framework_times.items(), key=lambda x: x[1])
            slowest = max(framework_times.items(), key=lambda x: x[1])
            print(f"\n🏆 Fastest: {fastest[0]} ({fastest[1]:.0f}ms avg)")
            print(f"🐢 Slowest: {slowest[0]} ({slowest[1]:.0f}ms avg)")


if __name__ == "__main__":
    asyncio.run(main())

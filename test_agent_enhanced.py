"""
Enhanced test agent with multi-turn, HITL, and feature detection support.
"""

import httpx
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path


async def test_agent_enhanced(
    client: httpx.AsyncClient,
    name: str,
    config: dict,
    test_config: dict,
    run_dir: Path = None,
    run_num: int = 1
) -> Dict[str, Any]:
    """
    Enhanced agent test that handles:
    - Single-turn prompts
    - Multi-turn conversations
    - HITL emulation
    - Feature detection (thinking, artifacts, errors)
    """

    test_type = test_config.get("type", "single")
    prompt_type = test_config.get("name", "unknown")

    # Initialize metrics
    metrics = {
        "name": name,
        "prompt_type": prompt_type,
        "test_type": test_type,
        "success": False,
        "error": None,
        "timing": {},
        "features": {
            "has_thinking": False,
            "has_artifacts": False,
            "has_hitl": False,
            "has_state": False,
            "has_errors": False,
        },
        "tool_calls": 0,
        "events": [],
        "turns": [],
    }

    start_time = time.perf_counter()

    try:
        if test_type == "single":
            result = await _run_single_turn(client, name, config, test_config, metrics)
        elif test_type == "multi":
            result = await _run_multi_turn(client, name, config, test_config, metrics)
        elif test_type == "hitl":
            result = await _run_hitl_test(client, name, config, test_config, metrics)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

        metrics.update(result)
        metrics["success"] = True

    except Exception as e:
        metrics["error"] = str(e)
        metrics["success"] = False

    end_time = time.perf_counter()
    metrics["timing"]["total_ms"] = (end_time - start_time) * 1000

    # Analyze events for feature detection
    _detect_features(metrics)

    # Save data if run_dir provided
    if run_dir:
        _save_enhanced_test_data(run_dir, name, run_num, prompt_type, metrics)

    return metrics


async def _run_single_turn(client, name, config, test_config, metrics):
    """Run a single-turn test."""
    prompt = test_config.get("prompt", "")

    request_body = {
        "thread_id": f"test-thread-{name}",
        "run_id": f"test-run-{name}-{test_config.get('name')}",
        "messages": [{"id": "msg-1", "role": "user", "content": prompt}],
        "state": {},
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }

    events = await _stream_request(client, config, request_body)

    return {
        "request": request_body,
        "events": events,
        "turns": [{"request": request_body, "events": events}],
    }


async def _run_multi_turn(client, name, config, test_config, metrics):
    """Run a multi-turn conversation test."""
    messages_list = test_config.get("messages", [])
    all_turns = []
    all_events = []
    thread_id = f"test-thread-{name}-multi"

    for turn_num, msg_config in enumerate(messages_list, 1):
        # Build messages history
        messages = [
            {"id": f"msg-{i+1}", "role": m.get("role", "user"), "content": m.get("content", "")}
            for i, m in enumerate(messages_list[:turn_num])
        ]

        request_body = {
            "thread_id": thread_id,
            "run_id": f"test-run-{name}-turn{turn_num}",
            "messages": messages,
            "state": {},
            "tools": [],
            "context": [],
            "forwardedProps": {},
        }

        turn_start = time.perf_counter()
        events = await _stream_request(client, config, request_body)
        turn_time = (time.perf_counter() - turn_start) * 1000

        turn_data = {
            "turn": turn_num,
            "request": request_body,
            "events": events,
            "time_ms": turn_time,
        }

        all_turns.append(turn_data)
        all_events.extend(events)

        # Check if context was retained (for turn 2+)
        if turn_num > 1:
            # Look for context retention indicators in the response
            response_text = _extract_text_from_events(events)
            if _check_context_retention(messages_list, response_text, turn_num):
                metrics["features"]["context_retained"] = True

    return {
        "request": all_turns[0]["request"],  # First turn request
        "events": all_events,
        "turns": all_turns,
    }


async def _run_hitl_test(client, name, config, test_config, metrics):
    """Run a test with HITL emulation."""
    prompt = test_config.get("prompt", "")
    hitl_response = test_config.get("hitl_response", {"approved": True})

    request_body = {
        "thread_id": f"test-thread-{name}-hitl",
        "run_id": f"test-run-{name}-hitl",
        "messages": [{"id": "msg-1", "role": "user", "content": prompt}],
        "state": {},
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }

    # Stream and watch for HITL events
    events = []
    hitl_detected = False

    async with client.stream(
        "POST",
        config["url"],
        json=request_body,
        headers={"Accept": "text/event-stream"},
        timeout=120.0,
    ) as response:
        full_text = ""
        async for chunk in response.aiter_text():
            full_text += chunk

            # Parse events as they come
            chunk_events = _parse_sse_events(full_text)
            for event in chunk_events:
                if event not in events:
                    events.append(event)

                    # Check for HITL request
                    if event.get("type") == "HUMAN_INPUT_REQUESTED":
                        hitl_detected = True
                        # In a real implementation, we'd send the response back
                        # For now, just record that we detected it
                        metrics["features"]["has_hitl"] = True
                        metrics["hitl_response"] = hitl_response

    return {
        "request": request_body,
        "events": events,
        "turns": [{"request": request_body, "events": events}],
        "hitl_detected": hitl_detected,
    }


async def _stream_request(client, config, request_body):
    """Stream a request and return all events."""
    events = []

    async with client.stream(
        "POST",
        config["url"],
        json=request_body,
        headers={"Accept": "text/event-stream"},
        timeout=120.0,
    ) as response:
        full_text = ""
        async for chunk in response.aiter_text():
            full_text += chunk

        events = _parse_sse_events(full_text)

    return events


def _parse_sse_events(text: str) -> List[Dict[str, Any]]:
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


def _extract_text_from_events(events: List[Dict]) -> str:
    """Extract text content from events."""
    text_parts = []
    for event in events:
        if event.get("type") == "TEXT_MESSAGE_CONTENT":
            text_parts.append(event.get("delta", ""))
        elif event.get("type") == "MESSAGES_SNAPSHOT":
            # Extract from messages snapshot
            messages = event.get("messages", [])
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if content:
                        return content
    return "".join(text_parts)


def _check_context_retention(messages_list, response_text, turn_num):
    """Check if the agent retained context from previous turns."""
    # Simple heuristic: check if response references earlier information
    # This is test-specific and should be improved based on actual tests

    # For the "memory" test, check if Python is mentioned in turn 2
    if turn_num == 2 and "python" in response_text.lower():
        return True

    return False


def _detect_features(metrics):
    """Detect AG-UI features from events."""
    event_types = {e.get("type") for e in metrics["events"]}

    # Thinking/reasoning
    if "THINKING_START" in event_types or "THINKING_CONTENT" in event_types:
        metrics["features"]["has_thinking"] = True

    # Artifacts
    if "ARTIFACT_START" in event_types or "ARTIFACT_CONTENT" in event_types:
        metrics["features"]["has_artifacts"] = True

    # HITL
    if "HUMAN_INPUT_REQUESTED" in event_types:
        metrics["features"]["has_hitl"] = True

    # State/Messages snapshots
    if "STATE_SNAPSHOT" in event_types or "MESSAGES_SNAPSHOT" in event_types:
        metrics["features"]["has_state"] = True

    # Errors
    if "ERROR" in event_types:
        metrics["features"]["has_errors"] = True

    # Tool calls
    tool_starts = [e for e in metrics["events"] if e.get("type") == "TOOL_CALL_START"]
    metrics["tool_calls"] = len(tool_starts)


def _save_enhanced_test_data(run_dir: Path, agent_name: str, run_num: int,
                              prompt_type: str, metrics: Dict):
    """Save enhanced test data including multi-turn and features."""
    agent_dir = run_dir / agent_name
    agent_dir.mkdir(exist_ok=True)

    test_dir = agent_dir / f"run{run_num}-{prompt_type}"
    test_dir.mkdir(exist_ok=True)

    # Save all turns
    for i, turn in enumerate(metrics.get("turns", []), 1):
        turn_dir = test_dir if len(metrics["turns"]) == 1 else test_dir / f"turn{i}"
        if len(metrics["turns"]) > 1:
            turn_dir.mkdir(exist_ok=True)

        # Save request
        with open(turn_dir / "request.json", "w") as f:
            json.dump(turn.get("request", {}), f, indent=2)

        # Save events as JSONL
        with open(turn_dir / "response.jsonl", "w") as f:
            for event in turn.get("events", []):
                f.write(json.dumps(event) + "\n")

    # Save comprehensive metadata
    metadata = {
        "agent": agent_name,
        "run_number": run_num,
        "prompt_type": prompt_type,
        "test_type": metrics.get("test_type"),
        "success": metrics.get("success"),
        "error": metrics.get("error"),
        "timing": metrics.get("timing", {}),
        "features": metrics.get("features", {}),
        "tool_calls": metrics.get("tool_calls", 0),
        "turn_count": len(metrics.get("turns", [])),
        "total_events": len(metrics.get("events", [])),
        "event_types": sorted(list({e.get("type") for e in metrics.get("events", [])})),
    }

    with open(test_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

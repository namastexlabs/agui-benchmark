#!/usr/bin/env python3
"""
AG-UI Benchmark Replay Utility

Replay and analyze saved benchmark test data.

Usage:
    python replay_test.py <path-to-test-dir>
    python replay_test.py benchmark-runs/20260205-223045/agno-anthropic/run1-simple
    python replay_test.py benchmark-runs/20260205-223045/agno-anthropic
    python replay_test.py benchmark-runs/20260205-223045
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import time


def load_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file (one JSON object per line)."""
    events = []
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def replay_test(test_dir: Path, animate: bool = False):
    """Replay a single test from saved data."""
    print(f"\n{'=' * 80}")
    print(f"🔄 REPLAYING: {test_dir.name}")
    print(f"{'=' * 80}")

    # Load files
    request_file = test_dir / "request.json"
    response_file = test_dir / "response.jsonl"
    metadata_file = test_dir / "metadata.json"

    if not all([request_file.exists(), response_file.exists(), metadata_file.exists()]):
        print("❌ Missing required files (request.json, response.jsonl, metadata.json)")
        return

    with open(request_file) as f:
        request = json.load(f)

    events = load_jsonl(response_file)

    with open(metadata_file) as f:
        metadata = json.load(f)

    # Display test info
    print(f"\n📋 Test Info:")
    print(f"   Agent: {metadata['agent']}")
    print(f"   Run: #{metadata['run_number']}")
    print(f"   Type: {metadata['prompt_type']}")
    print(f"   Success: {'✅' if metadata['success'] else '❌'}")
    if metadata.get('error'):
        print(f"   Error: {metadata['error']}")

    print(f"\n📨 Request:")
    print(f"   Prompt: \"{metadata['prompt']}\"")
    print(f"   Thread ID: {request['thread_id']}")
    print(f"   Run ID: {request['run_id']}")

    print(f"\n⏱️  Timing:")
    timing = metadata['timing']
    print(f"   Total Time: {timing['total_time_ms']:.2f}ms")
    print(f"   Time to First Event: {timing['time_to_first_event_ms']:.2f}ms")
    print(f"   Time to First Content: {timing['time_to_first_content_ms']:.2f}ms")

    print(f"\n🔧 Tools:")
    tools = metadata['tools']
    print(f"   Tool Calls: {tools['tool_calls']}")
    if tools['tool_calls'] > 0:
        print(f"   Tool Time: {tools['tool_call_time_ms']:.2f}ms")

    print(f"\n📊 Response Stats:")
    response = metadata['response']
    print(f"   Characters: {response['chars']}")
    print(f"   Tokens (approx): {response['tokens_approx']}")

    print(f"\n📡 Events ({metadata['events']['total_events']} total):")
    print(f"   Types: {', '.join(metadata['events']['event_types'])}")

    # Replay events
    print(f"\n🎬 Streaming Events:")
    print(f"   {'-' * 76}")

    text_buffer = []
    for i, event in enumerate(events, 1):
        event_type = event.get('type', 'UNKNOWN')

        if animate:
            time.sleep(0.05)  # Simulate streaming delay

        if event_type == 'TEXT_MESSAGE_CONTENT':
            delta = event.get('delta', '')
            text_buffer.append(delta)
            print(f"   [{i:3d}] {event_type:<25} → \"{delta}\"")

        elif event_type == 'TOOL_CALL_START':
            print(f"   [{i:3d}] {event_type:<25} → {event.get('name', 'unknown')} (id: {event.get('id', 'N/A')})")

        elif event_type == 'TOOL_CALL_ARGS':
            print(f"   [{i:3d}] {event_type:<25} → {event.get('args', {})}")

        elif event_type == 'TOOL_CALL_RESULT':
            print(f"   [{i:3d}] {event_type:<25} → {str(event.get('result', {}))[:60]}...")

        elif event_type == 'MESSAGES_SNAPSHOT':
            messages = event.get('messages', [])
            print(f"   [{i:3d}] {event_type:<25} → {len(messages)} messages")

        else:
            print(f"   [{i:3d}] {event_type:<25}")

    print(f"   {'-' * 76}")

    # Show final response
    print(f"\n💬 Final Response:")
    final_text = response['final_text']
    if final_text:
        print(f"   \"{final_text}\"")
    else:
        print(f"   (no text response)")

    # Compare streamed vs final
    streamed_text = ''.join(text_buffer)
    if streamed_text and streamed_text != final_text:
        print(f"\n⚠️  Warning: Streamed text differs from final response")
        print(f"   Streamed: \"{streamed_text}\"")
        print(f"   Final: \"{final_text}\"")


def replay_agent_runs(agent_dir: Path):
    """Replay all runs for an agent."""
    test_dirs = sorted([d for d in agent_dir.iterdir() if d.is_dir()])

    print(f"\n{'=' * 80}")
    print(f"📦 Agent: {agent_dir.name}")
    print(f"{'=' * 80}")
    print(f"\nFound {len(test_dirs)} test runs\n")

    for test_dir in test_dirs:
        replay_test(test_dir, animate=False)


def analyze_run(run_dir: Path):
    """Analyze a complete benchmark run."""
    print(f"\n{'=' * 80}")
    print(f"📊 BENCHMARK RUN ANALYSIS")
    print(f"{'=' * 80}")

    # Load metadata
    metadata_file = run_dir / "run-metadata.json"
    summary_file = run_dir / "summary.json"

    if metadata_file.exists():
        with open(metadata_file) as f:
            metadata = json.load(f)
        print(f"\n⏰ Run Time: {metadata['timestamp']}")
        print(f"   Started: {metadata['start_time']}")
        print(f"   Runs per test: {metadata['num_runs']}")

    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)

        print(f"\n📈 Results:")
        analysis = summary['analysis']
        print(f"   Total Tests: {analysis['total_tests']}")
        print(f"   Successful: {analysis['successful']} ({analysis['successful']/analysis['total_tests']*100:.1f}%)")
        print(f"   Failed: {analysis['failed']}")

        print(f"\n🏆 Fastest by Model:")
        for model, data in summary.get('fastest_by_model', {}).items():
            print(f"   {model.upper()}: {data['framework']} ({data['time_ms']:.0f}ms)")

        fastest = summary.get('overall_fastest', {})
        if fastest.get('name'):
            print(f"\n🥇 Overall Fastest:")
            print(f"   {fastest['name']} ({fastest['time_ms']:.0f}ms)")
            print(f"   Framework: {fastest['framework']}")
            print(f"   Model: {fastest['model']}")

    # List all agent directories
    agent_dirs = sorted([d for d in run_dir.iterdir() if d.is_dir()])
    print(f"\n📁 Agent Data ({len(agent_dirs)} agents):")
    for agent_dir in agent_dirs:
        test_count = len([d for d in agent_dir.iterdir() if d.is_dir()])
        print(f"   {agent_dir.name:<30} {test_count} tests")


def main():
    if len(sys.argv) < 2:
        print("Usage: python replay_test.py <path-to-test-or-run-dir>")
        print("\nExamples:")
        print("  python replay_test.py benchmark-runs/20260205-223045/agno-anthropic/run1-simple")
        print("  python replay_test.py benchmark-runs/20260205-223045/agno-anthropic")
        print("  python replay_test.py benchmark-runs/20260205-223045")
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"❌ Path not found: {path}")
        sys.exit(1)

    # Determine what kind of path this is
    if (path / "request.json").exists():
        # Single test directory
        replay_test(path, animate=True)
    elif (path / "run-metadata.json").exists():
        # Full benchmark run directory
        analyze_run(path)
    elif path.is_dir():
        # Assume agent directory with multiple runs
        replay_agent_runs(path)
    else:
        print(f"❌ Unknown path type: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()

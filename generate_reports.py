#!/usr/bin/env python3
"""
Generate comprehensive markdown reports from benchmark results.

Reads JSON output from benchmark runs and generates:
- Event coverage matrix (26 events × agents)
- Framework capabilities matrix
- Tool call analysis
- Streaming performance analysis
- Success rate comparisons
- Model vs Framework comparisons
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from statistics import median, mean
from datetime import datetime


def load_benchmark_results(run_dir):
    """Load all benchmark results from a run directory."""
    results = {}

    for agent_dir in sorted(run_dir.glob("*")):
        if not agent_dir.is_dir():
            continue

        agent_name = agent_dir.name
        agent_results = {}

        for test_dir in sorted(agent_dir.glob("run*-*")):
            if not test_dir.is_dir():
                continue

            metadata_file = test_dir / "metadata.json"
            response_file = test_dir / "response.jsonl"

            if not metadata_file.exists():
                continue

            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)

                # Load events from response
                events = []
                event_types = set()
                if response_file.exists():
                    with open(response_file) as f:
                        for line in f:
                            if line.startswith("data: "):
                                try:
                                    event = json.loads(line[6:])
                                    events.append(event)
                                    event_types.add(event.get("type"))
                                except:
                                    pass

                test_name = test_dir.name
                agent_results[test_name] = {
                    "metadata": metadata,
                    "events": events,
                    "event_types": event_types,
                }
            except Exception as e:
                print(f"Error loading {test_dir}: {e}")
                continue

        if agent_results:
            results[agent_name] = agent_results

    return results


def generate_event_coverage_matrix(results, output_file):
    """Generate 26-event × agents matrix."""

    # All AG-UI spec events
    all_events = [
        "RUN_STARTED", "RUN_FINISHED", "RUN_ERROR",
        "TEXT_MESSAGE_START", "TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_END", "TEXT_MESSAGE_CHUNK",
        "THINKING_START", "THINKING_END",
        "THINKING_TEXT_MESSAGE_START", "THINKING_TEXT_MESSAGE_CONTENT", "THINKING_TEXT_MESSAGE_END",
        "TOOL_CALL_START", "TOOL_CALL_ARGS", "TOOL_CALL_END", "TOOL_CALL_CHUNK", "TOOL_CALL_RESULT",
        "STATE_SNAPSHOT", "STATE_DELTA", "MESSAGES_SNAPSHOT",
        "ACTIVITY_SNAPSHOT", "ACTIVITY_DELTA",
        "STEP_STARTED", "STEP_FINISHED",
        "RAW", "CUSTOM"
    ]

    # Collect event types per agent (across all tests)
    agent_events = {}
    for agent_name, tests in results.items():
        all_agent_events = set()
        for test_data in tests.values():
            all_agent_events.update(test_data["event_types"])
        agent_events[agent_name] = all_agent_events

    agents = sorted(agent_events.keys())

    # Generate matrix
    content = "# 🎯 AG-UI Event Coverage Matrix\n\n"
    content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += f"**Total Agents:** {len(agents)}\n"
    content += f"**AG-UI Spec Events:** {len(all_events)}\n\n"
    content += "## 📊 All Frameworks × All AG-UI Events\n\n"

    # Build table header
    content += "| Event Type | " + " | ".join(agents) + " |\n"
    content += "|" + "|".join(["-" * max(15, len(a)) for a in ["Event Type"] + agents]) + "|\n"

    # Build table rows
    for event in all_events:
        row = f"| **{event}** |"
        for agent in agents:
            has_event = event in agent_events.get(agent, set())
            row += " ✅ |" if has_event else " ❌ |"
        content += row + "\n"

    # Summary statistics
    content += "\n## 📈 Event Coverage Statistics\n\n"

    event_coverage = {}
    for event in all_events:
        count = sum(1 for agent in agents if event in agent_events.get(agent, set()))
        coverage = (count / len(agents)) * 100
        event_coverage[event] = (count, coverage)

    # Events by coverage percentage
    high_coverage = [e for e, (c, pct) in event_coverage.items() if pct >= 80]
    medium_coverage = [e for e, (c, pct) in event_coverage.items() if 20 <= pct < 80]
    low_coverage = [e for e, (c, pct) in event_coverage.items() if pct < 20]

    content += f"**High Coverage (≥80%):** {len(high_coverage)}\n"
    for event in sorted(high_coverage):
        count, pct = event_coverage[event]
        content += f"- {event}: {count}/{len(agents)} ({pct:.0f}%)\n"

    content += f"\n**Medium Coverage (20-80%):** {len(medium_coverage)}\n"
    for event in sorted(medium_coverage):
        count, pct = event_coverage[event]
        content += f"- {event}: {count}/{len(agents)} ({pct:.0f}%)\n"

    content += f"\n**Low Coverage (<20%):** {len(low_coverage)}\n"
    for event in sorted(low_coverage):
        count, pct = event_coverage[event]
        content += f"- {event}: {count}/{len(agents)} ({pct:.0f}%)\n"

    with open(output_file, "w") as f:
        f.write(content)

    print(f"✅ Generated: {output_file}")


def generate_framework_comparison(results, output_file):
    """Generate framework capabilities comparison matrix."""

    content = "# 🏗️ Framework Capabilities Comparison\n\n"
    content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Collect metrics per agent
    agent_stats = {}
    for agent_name, tests in results.items():
        test_data = list(tests.values())
        if not test_data:
            continue

        # Extract metrics
        successful = [t["metadata"] for t in test_data if t["metadata"].get("success")]
        if not successful:
            continue

        times = [m.get("timing", {}).get("total_time_ms", 0) for m in successful]
        streaming = [m.get("streaming", {}) for m in successful]
        tool_calls = [m.get("tools", {}).get("tool_calls", 0) for m in successful]

        throughputs = [s.get("throughput_chars_per_sec", 0) for s in streaming if s and s.get("throughput_chars_per_sec", 0) > 0]

        agent_stats[agent_name] = {
            "success_rate": (len(successful) / len(test_data)) * 100,
            "median_time_ms": median(times) if times else 0,
            "avg_time_ms": mean(times) if times else 0,
            "throughput": median(throughputs) if throughputs else 0,
            "tool_calls_total": sum(tool_calls),
            "tests_count": len(test_data),
        }

    # Sort by success rate, then speed
    sorted_agents = sorted(
        agent_stats.items(),
        key=lambda x: (-x[1]["success_rate"], x[1]["median_time_ms"])
    )

    # Generate table
    content += "## 📊 Framework Performance Matrix\n\n"
    content += "| Framework | Tests | Success | Median Time (ms) | Throughput (c/s) | Tool Calls |\n"
    content += "|-----------|-------|---------|------------------|------------------|------------|\n"

    for agent, stats in sorted_agents:
        content += f"| {agent} | {stats['tests_count']} | "
        content += f"{stats['success_rate']:.0f}% | "
        content += f"{stats['median_time_ms']:.0f} | "
        content += f"{stats['throughput']:.0f} | "
        content += f"{stats['tool_calls_total']} |\n"

    # Feature coverage
    content += "\n## 🎯 Feature Support Matrix\n\n"

    feature_matrix = {
        "Streaming": ["TOOL_CALL", "TEXT_MESSAGE"],
        "Tools": ["TOOL_CALL_START", "TOOL_CALL_RESULT"],
        "State": ["STATE_SNAPSHOT", "STATE_DELTA"],
        "Steps": ["STEP_STARTED", "STEP_FINISHED"],
        "Observability": ["RAW", "CUSTOM"],
    }

    content += "| Framework |"
    for feature in feature_matrix:
        content += f" {feature} |"
    content += "\n|-----------|"
    for _ in feature_matrix:
        content += "----------|"
    content += "\n"

    # Get agent events for features
    agent_events = {}
    for agent_name, tests in results.items():
        all_events = set()
        for test_data in tests.values():
            all_events.update(test_data["event_types"])
        agent_events[agent_name] = all_events

    agents = sorted(agent_events.keys())
    for agent in agents:
        content += f"| {agent} |"
        for feature, required_events in feature_matrix.items():
            has_feature = any(e in agent_events.get(agent, set()) for e in required_events)
            content += " ✅ |" if has_feature else " ❌ |"
        content += "\n"

    with open(output_file, "w") as f:
        f.write(content)

    print(f"✅ Generated: {output_file}")


def generate_event_type_analysis(results, output_file):
    """Generate detailed event type analysis."""

    content = "# 📊 Event Type Analysis\n\n"
    content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Count occurrences and coverage
    event_stats = defaultdict(lambda: {"count": 0, "agents": set()})

    for agent_name, tests in results.items():
        for test_data in tests.values():
            for event_type in test_data["event_types"]:
                event_stats[event_type]["count"] += 1
                event_stats[event_type]["agents"].add(agent_name)

    total_agents = len(results)

    content += "## Event Coverage by Type\n\n"
    content += "| Event Type | Agents | Coverage | Occurrences |\n"
    content += "|------------|--------|----------|-------------|\n"

    for event_type in sorted(event_stats.keys()):
        stats = event_stats[event_type]
        coverage_pct = (len(stats["agents"]) / total_agents) * 100
        content += f"| {event_type} | {len(stats['agents'])}/{total_agents} | "
        content += f"{coverage_pct:.0f}% | {stats['count']} |\n"

    # Group by category
    content += "\n## Events by Category\n\n"

    categories = {
        "Lifecycle": ["RUN_STARTED", "RUN_FINISHED", "RUN_ERROR"],
        "Text Streaming": ["TEXT_MESSAGE_START", "TEXT_MESSAGE_CONTENT", "TEXT_MESSAGE_END", "TEXT_MESSAGE_CHUNK"],
        "Thinking": ["THINKING_START", "THINKING_END", "THINKING_TEXT_MESSAGE_START", "THINKING_TEXT_MESSAGE_CONTENT", "THINKING_TEXT_MESSAGE_END"],
        "Tools": ["TOOL_CALL_START", "TOOL_CALL_ARGS", "TOOL_CALL_END", "TOOL_CALL_CHUNK", "TOOL_CALL_RESULT"],
        "State": ["STATE_SNAPSHOT", "STATE_DELTA", "MESSAGES_SNAPSHOT", "ACTIVITY_SNAPSHOT", "ACTIVITY_DELTA"],
        "Steps": ["STEP_STARTED", "STEP_FINISHED"],
        "Framework": ["RAW", "CUSTOM"],
    }

    for category, events in categories.items():
        content += f"### {category}\n"
        for event in events:
            if event in event_stats:
                stats = event_stats[event]
                coverage_pct = (len(stats["agents"]) / total_agents) * 100
                content += f"- **{event}**: {coverage_pct:.0f}% ({len(stats['agents'])} agents)\n"
        content += "\n"

    with open(output_file, "w") as f:
        f.write(content)

    print(f"✅ Generated: {output_file}")


def generate_summary_report(results, output_file):
    """Generate overall summary report."""

    content = "# 📈 Benchmark Summary Report\n\n"
    content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    # Overall stats
    total_tests = sum(len(tests) for tests in results.values())
    total_agents = len(results)

    content += "## 🎯 Overall Statistics\n\n"
    content += f"- **Total Agents:** {total_agents}\n"
    content += f"- **Total Tests:** {total_tests}\n"
    content += f"- **Average Tests per Agent:** {total_tests / total_agents:.0f}\n"

    # Success rates
    successful_tests = 0
    for tests in results.values():
        for test_data in tests.values():
            if test_data["metadata"].get("success"):
                successful_tests += 1

    content += f"- **Overall Success Rate:** {(successful_tests / total_tests * 100):.1f}%\n\n"

    # Performance stats
    all_times = []
    all_throughputs = []
    for tests in results.values():
        for test_data in tests.values():
            if test_data["metadata"].get("success"):
                timing = test_data["metadata"].get("timing", {})
                if timing and timing.get("total_time_ms"):
                    all_times.append(timing["total_time_ms"])
                streaming = test_data["metadata"].get("streaming")
                if streaming and streaming.get("throughput_chars_per_sec"):
                    all_throughputs.append(streaming["throughput_chars_per_sec"])

    content += "## ⚡ Performance Metrics\n\n"
    if all_times:
        content += f"- **Fastest Test:** {min(all_times):.0f}ms\n"
        content += f"- **Slowest Test:** {max(all_times):.0f}ms\n"
        content += f"- **Median Response Time:** {median(all_times):.0f}ms\n"
        content += f"- **Average Response Time:** {mean(all_times):.0f}ms\n\n"

    if all_throughputs:
        content += f"- **Fastest Streaming:** {max(all_throughputs):.0f} chars/sec\n"
        content += f"- **Slowest Streaming:** {min(all_throughputs):.0f} chars/sec\n"
        content += f"- **Median Throughput:** {median(all_throughputs):.0f} chars/sec\n"
        content += f"- **Average Throughput:** {mean(all_throughputs):.0f} chars/sec\n\n"

    # Event coverage
    all_event_types = set()
    for tests in results.values():
        for test_data in tests.values():
            all_event_types.update(test_data["event_types"])

    content += "## 📊 Event Coverage\n\n"
    content += f"- **Unique Event Types Captured:** {len(all_event_types)}\n"
    content += f"- **AG-UI Spec Total:** 26 events\n"
    content += f"- **Coverage:** {(len(all_event_types) / 26 * 100):.1f}%\n\n"

    content += "## 🏆 Top Performers\n\n"

    # Fastest
    agent_times = {}
    for agent_name, tests in results.items():
        successful = [t["metadata"] for t in tests.values() if t["metadata"].get("success")]
        if successful:
            times = [m.get("timing", {}).get("total_time_ms", 0) for m in successful]
            agent_times[agent_name] = median(times) if times else float('inf')

    if agent_times:
        top_fast = sorted(agent_times.items(), key=lambda x: x[1])[:5]
        content += "**Fastest Agents:**\n"
        for agent, time in top_fast:
            content += f"- {agent}: {time:.0f}ms\n"
        content += "\n"

    # Best streaming
    agent_throughputs = {}
    for agent_name, tests in results.items():
        successful = [t["metadata"] for t in tests.values() if t["metadata"].get("success")]
        if successful:
            streaming = [m.get("streaming", {}) for m in successful]
            throughputs = [s.get("throughput_chars_per_sec", 0) for s in streaming if s]
            agent_throughputs[agent_name] = median(throughputs) if throughputs else 0

    if agent_throughputs:
        top_throughput = sorted(agent_throughputs.items(), key=lambda x: x[1], reverse=True)[:5]
        content += "**Fastest Streaming:**\n"
        for agent, tp in top_throughput:
            content += f"- {agent}: {tp:.0f} chars/sec\n"
        content += "\n"

    with open(output_file, "w") as f:
        f.write(content)

    print(f"✅ Generated: {output_file}")


def main():
    """Main entry point."""

    # Find latest benchmark run
    benchmark_dir = Path("benchmark-runs")
    if not benchmark_dir.exists():
        print("❌ No benchmark-runs directory found. Run: uv run python test_agents.py")
        return

    # Get latest run
    runs = sorted([d for d in benchmark_dir.glob("*") if d.is_dir()])
    if not runs:
        print("❌ No benchmark runs found in benchmark-runs/")
        return

    latest_run = runs[-1]
    print(f"📁 Loading results from: {latest_run}")

    # Load results
    results = load_benchmark_results(latest_run)
    if not results:
        print("❌ No results found")
        return

    print(f"✅ Loaded {len(results)} agents with results")

    # Generate reports
    print("\n🚀 Generating reports...\n")

    generate_event_coverage_matrix(
        results,
        Path("EVENT-COVERAGE-MATRIX.md")
    )

    generate_framework_comparison(
        results,
        Path("FRAMEWORK-COMPARISON-MATRIX.md")
    )

    generate_event_type_analysis(
        results,
        Path("EVENT-TYPE-ANALYSIS.md")
    )

    generate_summary_report(
        results,
        Path("BENCHMARK-SUMMARY.md")
    )

    print("\n✅ All reports generated successfully!")
    print("\n📋 Generated files:")
    print("  - EVENT-COVERAGE-MATRIX.md (26 events × agents)")
    print("  - FRAMEWORK-COMPARISON-MATRIX.md (capabilities)")
    print("  - EVENT-TYPE-ANALYSIS.md (event breakdown)")
    print("  - BENCHMARK-SUMMARY.md (overall stats)")


if __name__ == "__main__":
    main()

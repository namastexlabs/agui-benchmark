#!/usr/bin/env python3
"""
AG-UI Feature Support Matrix

Generates comprehensive reports showing which frameworks support which AG-UI features.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


AG_UI_FEATURES = {
    "core": {
        "streaming": ["RUN_STARTED", "RUN_FINISHED", "TEXT_MESSAGE_CONTENT"],
        "tool_calling": ["TOOL_CALL_START", "TOOL_CALL_END", "TOOL_CALL_RESULT"],
    },
    "advanced": {
        "thinking": ["THINKING_START", "THINKING_CONTENT", "THINKING_END"],
        "artifacts": ["ARTIFACT_START", "ARTIFACT_CONTENT", "ARTIFACT_END"],
        "hitl": ["HUMAN_INPUT_REQUESTED", "HUMAN_INPUT_RECEIVED"],
        "state": ["STATE_SNAPSHOT", "MESSAGES_SNAPSHOT"],
        "errors": ["ERROR"],
    },
}


def analyze_feature_support(run_dir: Path) -> Dict[str, Any]:
    """Analyze all test results to determine feature support."""

    feature_matrix = defaultdict(lambda: defaultdict(dict))
    agent_stats = defaultdict(lambda: {
        "total_tests": 0,
        "successful_tests": 0,
        "event_types_seen": set(),
        "features_supported": set(),
    })

    # Scan all agent directories
    for agent_dir in run_dir.iterdir():
        if not agent_dir.is_dir() or agent_dir.name in ["summary.json", "run-metadata.json"]:
            continue

        agent_name = agent_dir.name

        # Scan all test runs
        for test_dir in agent_dir.iterdir():
            if not test_dir.is_dir():
                continue

            metadata_file = test_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            with open(metadata_file) as f:
                metadata = json.load(f)

            agent_stats[agent_name]["total_tests"] += 1
            if metadata.get("success"):
                agent_stats[agent_name]["successful_tests"] += 1

            # Collect event types
            event_types = metadata.get("event_types", metadata.get("events", {}).get("event_types", []))
            agent_stats[agent_name]["event_types_seen"].update(event_types)

            # Check feature support
            features = metadata.get("features", {})
            for feature, supported in features.items():
                if supported:
                    agent_stats[agent_name]["features_supported"].add(feature)

    # Build feature matrix
    for agent_name, stats in agent_stats.items():
        event_types = stats["event_types_seen"]

        # Core features
        feature_matrix[agent_name]["streaming"] = _check_events(event_types, AG_UI_FEATURES["core"]["streaming"])
        feature_matrix[agent_name]["tool_calling"] = _check_events(event_types, AG_UI_FEATURES["core"]["tool_calling"])

        # Advanced features
        feature_matrix[agent_name]["thinking"] = _check_events(event_types, AG_UI_FEATURES["advanced"]["thinking"])
        feature_matrix[agent_name]["artifacts"] = _check_events(event_types, AG_UI_FEATURES["advanced"]["artifacts"])
        feature_matrix[agent_name]["hitl"] = _check_events(event_types, AG_UI_FEATURES["advanced"]["hitl"])
        feature_matrix[agent_name]["state"] = _check_events(event_types, AG_UI_FEATURES["advanced"]["state"])
        feature_matrix[agent_name]["errors"] = _check_events(event_types, AG_UI_FEATURES["advanced"]["errors"])

        # Multi-turn (check if agent has multi-turn tests)
        feature_matrix[agent_name]["multi_turn"] = "context_retained" in stats["features_supported"]

        # Success rate
        total = stats["total_tests"]
        success = stats["successful_tests"]
        feature_matrix[agent_name]["success_rate"] = (success / total * 100) if total > 0 else 0

    return dict(feature_matrix)


def _check_events(seen_events: set, required_events: List[str]) -> bool:
    """Check if all required events were seen."""
    return any(event in seen_events for event in required_events)


def print_feature_matrix(feature_matrix: Dict[str, Any], frameworks_info: Dict[str, Any]):
    """Print a comprehensive feature support matrix."""

    print("\n" + "=" * 120)
    print("AG-UI FEATURE SUPPORT MATRIX")
    print("=" * 120)

    # Extract unique frameworks (remove model suffix)
    framework_agents = defaultdict(list)
    for agent_name in feature_matrix.keys():
        # Parse framework name (remove model suffix)
        parts = agent_name.rsplit("-", 1)
        framework = parts[0] if len(parts) > 1 else agent_name
        framework_agents[framework].append(agent_name)

    print(f"\n{'Framework':<20} {'Streaming':<12} {'Tools':<8} {'Thinking':<10} {'Artifacts':<11} {'HITL':<8} {'Multi-turn':<12} {'State':<8} {'Success %':<10}")
    print("-" * 120)

    for framework in sorted(framework_agents.keys()):
        agents = framework_agents[framework]

        # Aggregate features across all models for this framework
        streaming = any(feature_matrix[agent]["streaming"] for agent in agents)
        tools = any(feature_matrix[agent]["tool_calling"] for agent in agents)
        thinking = any(feature_matrix[agent]["thinking"] for agent in agents)
        artifacts = any(feature_matrix[agent]["artifacts"] for agent in agents)
        hitl = any(feature_matrix[agent]["hitl"] for agent in agents)
        multi_turn = any(feature_matrix[agent]["multi_turn"] for agent in agents)
        state = any(feature_matrix[agent]["state"] for agent in agents)
        avg_success = sum(feature_matrix[agent]["success_rate"] for agent in agents) / len(agents)

        print(f"{framework:<20} {_status(streaming):<12} {_status(tools):<8} {_status(thinking):<10} "
              f"{_status(artifacts):<11} {_status(hitl):<8} {_status(multi_turn):<12} "
              f"{_status(state):<8} {avg_success:>6.1f}%")

    print()

    # Detailed per-agent breakdown
    print("\n" + "=" * 120)
    print("DETAILED AGENT-LEVEL FEATURE SUPPORT")
    print("=" * 120)

    print(f"\n{'Agent':<30} {'Model':<10} {'Stream':<8} {'Tools':<8} {'Think':<8} {'Artifact':<9} {'HITL':<6} {'Multi':<6} {'State':<6} {'Success':<8}")
    print("-" * 120)

    for agent_name in sorted(feature_matrix.keys()):
        features = feature_matrix[agent_name]

        # Extract model from agent name
        parts = agent_name.rsplit("-", 1)
        model = parts[1] if len(parts) > 1 else "N/A"

        print(f"{agent_name:<30} {model:<10} "
              f"{_icon(features['streaming']):<8} "
              f"{_icon(features['tool_calling']):<8} "
              f"{_icon(features['thinking']):<8} "
              f"{_icon(features['artifacts']):<9} "
              f"{_icon(features['hitl']):<6} "
              f"{_icon(features['multi_turn']):<6} "
              f"{_icon(features['state']):<6} "
              f"{features['success_rate']:>6.1f}%")

    print()


def _status(supported: bool) -> str:
    """Return status string."""
    return "✅ Yes" if supported else "❌ No"


def _icon(supported: bool) -> str:
    """Return icon."""
    return "✅" if supported else "❌"


def save_feature_matrix(run_dir: Path, feature_matrix: Dict):
    """Save feature matrix to JSON."""
    output_file = run_dir / "feature-matrix.json"

    # Convert sets to lists for JSON serialization
    serializable_matrix = {}
    for agent, features in feature_matrix.items():
        serializable_matrix[agent] = {
            k: (list(v) if isinstance(v, set) else v)
            for k, v in features.items()
        }

    with open(output_file, "w") as f:
        json.dump(serializable_matrix, f, indent=2)

    print(f"💾 Feature matrix saved to: {output_file}")


def main():
    """Analyze the most recent benchmark run."""
    import sys

    if len(sys.argv) > 1:
        run_dir = Path(sys.argv[1])
    else:
        # Find most recent run
        runs_dir = Path(__file__).parent / "benchmark-runs"
        run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], reverse=True)
        if not run_dirs:
            print("No benchmark runs found!")
            sys.exit(1)
        run_dir = run_dirs[0]

    print(f"📊 Analyzing: {run_dir.name}")

    # Load framework info if available
    metadata_file = run_dir / "run-metadata.json"
    frameworks_info = {}
    if metadata_file.exists():
        with open(metadata_file) as f:
            frameworks_info = json.load(f)

    # Analyze features
    feature_matrix = analyze_feature_support(run_dir)

    # Print matrix
    print_feature_matrix(feature_matrix, frameworks_info)

    # Save matrix
    save_feature_matrix(run_dir, feature_matrix)


if __name__ == "__main__":
    main()

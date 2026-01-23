#!/bin/bash
# Stop all AG-UI test agents

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🛑 Stopping AG-UI Test Agents..."

for pid_file in logs/*.pid; do
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        name=$(basename "$pid_file" .pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo "  Stopped $name (PID: $pid)"
        fi
        rm "$pid_file"
    fi
done

echo ""
echo "✅ All agents stopped"

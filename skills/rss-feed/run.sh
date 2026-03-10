#!/bin/bash
# RSS Feed Monitor wrapper
# Uses virtual environment Python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/venv/bin/python3" "$SCRIPT_DIR/agent.py" "$@"

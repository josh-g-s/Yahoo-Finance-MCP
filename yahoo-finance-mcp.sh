#!/bin/bash
set -euo pipefail

# Run from this directory
cd "$(dirname "$0")"

# Prefer local source
export PYTHONPATH="$PWD/src:${PYTHONPATH:-}"

# Prefer a project-local venv if present
if [ -x "$PWD/.venv/bin/python" ]; then
  exec "$PWD/.venv/bin/python" -m yahoo_finance_mcp
fi

# Otherwise, fall back to python3 on PATH
exec python3 -m yahoo_finance_mcp

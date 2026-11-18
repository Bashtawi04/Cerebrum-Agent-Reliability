#!/usr/bin/env bash
# Create a virtual environment inside a target agent folder and install what its requirements.txt asks for.
#   bash tools/setup_target.sh targets/<folder>
set -euo pipefail
T="${1:?usage: bash tools/setup_target.sh targets/<folder>}"
cd "$T"
python3 -m venv .venv
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt
echo "ready. Use this interpreter in --agent: $(pwd)/.venv/bin/python"
echo "and this folder in --agent-dir: $(pwd)"

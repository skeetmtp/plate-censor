#!/bin/bash
set -e

cd "$(dirname "$0")/.."

source .venv/bin/activate

echo "Starting License Plate Censor web server..."
echo "Open http://localhost:8000 in your browser"
echo ""

uv run main.py

#!/bin/bash
# 🚀 YouTube Growth Engine Smart Launcher

echo "🚀 Launching YouTube Growth Engine..."

# Define path to venv python (now in the root)
VENV_PYTHON="./.venv/bin/python3"

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Virtual environment not found at $VENV_PYTHON"
    echo "Please create one first using: python3 -m venv .venv"
    exit 1
fi

echo "🐍 Using Virtual Environment Python..."

# Set PYTHONPATH to current directory
export PYTHONPATH="."

# Run streamlit using the venv python module with HEADLESS mode
"$VENV_PYTHON" -m streamlit run app.py --server.headless true

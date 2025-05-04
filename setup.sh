#!/bin/bash
set -e

echo "Setting up agent virtual environment..."
python3 -m venv agent/.venv
echo "Installing agent dependencies..."
agent/.venv/bin/python -m pip install -r agent/requirements.txt

echo "Setting up server virtual environment..."
python3 -m venv server/.venv
echo "Installing server dependencies..."
server/.venv/bin/python -m pip install -r server/requirements.txt

echo "Setup complete!"
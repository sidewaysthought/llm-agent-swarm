#!/bin/bash

# Check if pip is installed
command -v pip >/dev/null 2>&1 || { echo >&2 "pip is required but it's not installed. Aborting."; exit 1; }

# Install dependencies
pip install -r requirements.txt

# Run python script
python -m agent_swarm

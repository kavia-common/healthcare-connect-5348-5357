#!/bin/bash

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Export PYTHONPATH to include the backend directory
export PYTHONPATH="${BASE_DIR}:${PYTHONPATH}"

# Change to the backend directory
cd "${BASE_DIR}"

# Start the uvicorn server
echo "Starting Healthcare Backend API on port 3001..."
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

trap "kill 0" EXIT

# activate venv
source .venv/bin/activate

# Navigate to the backend directory
cd "$(dirname "$0")/src/backend"

# Run the backend server
fastapi run &
echo "Backend server running on http://localhost:8000"

# run the frontend server
cd "$(dirname "$0")/../frontend"

# build frontend first before running
# bun run build
# echo "Built frontend"
bun run dev --host 0.0.0.0 --port 5173 &
echo "Frontend server running."

wait

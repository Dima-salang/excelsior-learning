#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

trap "kill 0" EXIT

# activate venv
source .venv/bin/activate

# Navigate to the backend directory
cd "$(dirname "$0")/src/backend"

# Run the backend server
fastapi dev &

# run the frontend server
cd "$(dirname "$0")/../frontend"
bun run dev &


wait
#!/bin/bash

# Save the directory where the script was called from
CALL_DIR="$PWD"

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Move to the src directory
cd "$SCRIPT_DIR/../src" || {
    echo "Failed to cd into $SCRIPT_DIR/../src"
    cd "$CALL_DIR"
    exit 1
}

# Run BentoML and capture success/failure
if ! bentoml serve service:model_service --reload; then
    echo "done"
fi

# Always go back to the original directory
cd "$CALL_DIR"
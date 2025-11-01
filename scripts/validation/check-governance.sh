#!/bin/bash
# Wrapper for governance check that handles pre-commit filenames properly

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Convert all arguments to a list of filenames, one per line
for file in "$@"; do
    echo "$file"
done | python "${SCRIPT_DIR}/enforce-doc-governance.py"

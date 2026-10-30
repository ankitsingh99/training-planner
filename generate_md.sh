#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the Python generator
python3 generate_all_md.py "$@"

# Display the contents of PLAN.md in the terminal
if [ -f "PLAN.md" ]; then
  printf "\n========================================\n"
  printf "          PLAN.md (COMPLETE)\n"
  printf "========================================\n\n"
  cat "PLAN.md"
  printf "\n========================================\n"
  printf "          End of PLAN.md\n"
  printf "========================================\n\n"
fi

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the Python generator
python3 generate_all_md.py

# Display the contents of ALL_WORKOUTS.md in the terminal
if [ -f "ALL_WORKOUTS.md" ]; then
  printf "\n========================================\n"
  printf "          ALL_WORKOUTS.md\n"
  printf "========================================\n\n"
  cat "ALL_WORKOUTS.md"
  printf "\n========================================\n"
  printf "       End of ALL_WORKOUTS.md\n"
  printf "========================================\n\n"
fi

echo "✅ Generated and displayed ALL_WORKOUTS.md with the complete 8-week plan."

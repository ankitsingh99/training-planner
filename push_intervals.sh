#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the upload script
# upload_intervals_plan.py automatically loads INTERVALS_API_KEY from .env
# Pass any optional flags (such as --force) directly through
python3 upload_intervals_plan.py --upload "$@"

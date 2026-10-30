#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Run the upload script
# upload_intervals_plan.py automatically loads INTERVALS_API_KEY from .env
python3 upload_intervals_plan.py --upload

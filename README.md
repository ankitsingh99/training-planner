# Training Planner

A tiny Python utility that generates an 8‑week running and cycling schedule for **Intervals.icu** and optionally uploads the events via the Intervals API.

## Features
- Generates runs, easy rides, optional bike intervals and weekend club‑ride reminders.
- Dry‑run mode (default) prints a JSON preview of all events.
- `--upload` flag pushes the events to Intervals.icu (requires an API key).
- No external dependencies – pure Python standard library.

## Usage
```bash
# Set your Intervals API key (recommended via a .env file or environment variable)
export INTERVALS_API_KEY="YOUR_KEY"

# Dry run – see the plan without uploading
python3 upload_intervals_plan.py

# Real upload
python3 upload_intervals_plan.py --upload
```

## Project Structure
- `upload_intervals_plan.py` – the main script.
- `PLAN.md` – generated plan (dry‑run output) for reference.
- `.env.example` – example environment file showing where to place the API key.
- `.gitignore` – standard Python ignore patterns.
- `README.md` – this documentation.

## License
MIT License – feel free to fork, modify, and share.

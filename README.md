# AdaptPulse

> **Sports Science Powered Adaptive Training Suite & Dynamic Rolling Planner for Intervals.icu**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Strict](https://img.shields.io/badge/safety-dry--run%20by%20default-green.svg)](#safety-architecture)

AdaptPulse bridges the gap between static training plans and real-world human physiology. Instead of following rigid multi-week spreadsheets that ignore life stress, poor sleep, or unexpected fatigue, AdaptPulse dynamically evaluates rolling 30-day biometrics (HRV, resting heart rate, sleep) and completed workout data to generate or adjust personalized training plans for the upcoming 1 to 2 weeks.

It natively syncs structured workouts to [Intervals.icu](https://intervals.icu), which distributes them directly to **COROS**, **Garmin**, **Apple Watch**, and syncs completed efforts back via **Strava** and **Hevy**.

---

## Core Scientific Foundations

AdaptPulse integrates peer-reviewed exercise physiology and endurance training models:

1. **Stephen Seiler's 80/20 Polarized Model:**
   - Tracks polarization across low-intensity aerobic base (Zone 1/2), threshold "black hole" fatigue, and high-intensity interval training (HIIT).
2. **Tim Gabbett's Acute:Chronic Workload Ratio (ACWR):**
   - Compares acute workload (7-day rolling fatigue) to chronic workload (28-day rolling fitness).
   - Flags danger zones (`> 1.5`) to prevent soft-tissue injuries while identifying optimal training sweet spots (`0.8 - 1.3`).
3. **Banister & Coggan Performance Management Chart (PMC):**
   - Continuously computes Chronic Training Load (CTL / Fitness), Acute Training Load (ATL / Fatigue), and Training Stress Balance (TSB / Form).
4. **Kiviniemi / Plews Autonomic Nervous System Decision Trees:**
   - Interprets morning Heart Rate Variability (HRV rMSSD) and Resting Heart Rate (RHR) shifts relative to an athlete's 30-day baseline.
   - Automatically downgrades high-intensity interval days to active recovery or aerobic flushing when parasympathetic exhaustion or sympathetic strain is detected.

---

## System Architecture & Data Flow

```text
               +-------------------------------------------+
               |        Wearables & Hardware Inputs        |
               |  (COROS Watch, Garmin, Polar, Oura/Whoop) |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |          Intervals.icu Data Hub           |
               |   - Wellness (HRV, RHR, Sleep, Fatigue)   |
               |   - Activities (HR Zones, Power, TSS)     |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |                 AdaptPulse                |
               |                                           |
               |   [1] Analytics Engine                    |
               |       * ACWR, CTL/ATL/TSB, 80/20 Pol.     |
               |       * Autonomic Readiness Tree          |
               |                                           |
               |   [2] Athlete Profile Config              |
               |       * Goal: Hybrid, Running, Cycling    |
               |       * Weekly Time Commitment (Hours)    |
               |       * Periodization Philosophy          |
               |                                           |
               |   [3] Dynamic Rolling Planner             |
               |       * Builds 1-2 week target schedule   |
               |       * Generates COROS-compliant cues    |
               |                                           |
               |   [4] Guarded Sync Engine                 |
               |       * Dry-run preview by default        |
               |       * Pre-sync automatic backups        |
               |       * Read-back validation              |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               |          Intervals.icu Calendar           |
               +-------------------------------------------+
                                     |
                 +-------------------+-------------------+
                 |                                       |
                 v                                       v
   +---------------------------+           +---------------------------+
   |   COROS Device Calendar   |           |    Third-Party Platforms  |
   |   - Plain ASCII cues      |           |    - Strava (Social/Runs) |
   |   - <= 20 char step text  |           |    - Hevy (Strength)      |
   +---------------------------+           +---------------------------+
```

---

## Key Features

- **Interactive Multi-Page Web UI (`adaptpulse ui`):**
  - Self-contained, responsive dashboard with zero external dependencies.
  - Interactive tabs for **Dashboard & Readiness**, **PMC Analysis & Seiler 80/20 Distribution**, **Goal Setting & Athlete Profile**, **Rolling Calendar with COROS Screen Simulation**, **Ecosystem Cloud Sync**, and **Multi-Platform Export Center**.
- **Triathlon & Multi-Sport Adaptive Engine:**
  - Full periodization for **Sprint**, **Olympic**, **IRONMAN 70.3**, **IRONMAN 140.6**, **Running** (5K to Marathon), and **Cycling** (Gran Fondo / TT).
  - First-class support for **Critical Swim Speed (CSS)** intervals, stroke technique drills, and **Brick workouts** (bike immediately transitioning to run).
- **Sports Science Intra-Workout Fueling & Hydration Calculator:**
  - Evidence-based carbohydrate (g/hr), fluid (mL/hr), and sodium (mg/hr) prescriptions embedded in every workout based on duration and intensity (Jeukendrup & ACSM guidelines).
- **Planned vs. Actual Plan Compliance Engine (`adaptpulse compliance`):**
  - Evaluates execution score, volume compliance %, load compliance %, and flags overreaching or undertraining trends over rolling 7-28 days.
- **Intelligent Post-Workout Session Debrief (`adaptpulse review-session`):**
  - Analyzes Rate of Perceived Exertion (RPE 1-10), cardiac drift / aerobic decoupling (Pw:HR, Pa:HR), intensity discipline, and prescribes next-day recovery adaptations.
- **Intelligent Sports Science Coaching Advisor (`adaptpulse coach`):**
  - Synthesizes telemetry, target event timeline, periodization phase, and personal constraints into clear, actionable microcycle guidance.
- **Multi-Platform Workout Exporters (`adaptpulse export`):**
  - Export planned workouts directly to **Zwift (.zwo XML)**, **iCalendar (.ics)** for Google/Apple Calendar, and machine-readable JSON.
- **Dynamic Rolling 1-2 Week Planner (`plan-next`):**
  - Generates workout plans customized to your target weekly hours (e.g., 6h, 8h, 12h) and primary goals.
  - Automatically calculates periodization phase (**Base**, **Build**, **Peak**, **Taper**, or **Post-Race Recovery**) based on your target race date.
  - Respects life constraints (injuries, busy days, travel weekends).
- **Automated Bio-Adaptation (`adapt --auto`):**
  - Identifies acute cardiac or autonomic stress (e.g. resting heart rate spikes after weekend club rides) and swaps demanding intervals for low-stress aerobic recovery.
- **Hardware & COROS Compatibility Built-in:**
  - Standardized workout format stripped of non-ASCII characters and markdown formatting to guarantee flawless rendering on COROS watches and head units (<=20 char cues).
- **Guarded Mutations & Safety:**
  - Dry-run by default on every mutating command.
  - Requires explicit `--apply` to push changes to remote calendars.
  - Single deletion protected with `--confirm-delete`. Bulk deletion requires an exact confirmation phrase.
  - Automatic timestamped JSON backups created under `data/backups/` before any write operation.
  - Audit logging of every operation in `data/audit.log`.

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Intervals.icu account with an API key

### Setup

```bash
# Clone the repository
git clone https://github.com/ankitsingh99/training-planner.git
cd training-planner

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode
pip install -e .
```

Both `adaptpulse` and `intervals-plan` CLI commands are registered.

### Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```dotenv
# Intervals.icu Hub
INTERVALS_API_KEY=your_api_key_here
INTERVALS_ATHLETE_ID=0       # Use '0' or 'iXXXXX' for your own account
INTERVALS_BASE_URL=https://intervals.icu/api/v1

# TrainingPeaks Partner API (Optional)
TRAININGPEAKS_ACCESS_TOKEN=your_oauth_access_token_here
TRAININGPEAKS_CLIENT_ID=your_client_id_here
TRAININGPEAKS_CLIENT_SECRET=your_client_secret_here
TRAININGPEAKS_ATHLETE_ID=
TRAININGPEAKS_BASE_URL=https://api.trainingpeaks.com
```

Verify your setup:

```bash
adaptpulse doctor
```

---

## CLI Reference & Workflows

### 1. Interactive Multi-Page Web UI

Launch the embedded sports science Web UI dashboard:

```bash
# Launch server and automatically open browser at http://127.0.0.1:8080/
adaptpulse ui

# Specify custom port without opening browser
adaptpulse ui --port 9000 --no-browser
```

Features included in the Web UI:
- **Dashboard & Readiness:** Autonomic HRV/RHR delta, ACWR gauge, PMC balance card, coach briefing.
- **Analysis & PMC:** Interactive SVG PMC curves (CTL/ATL/TSB) and Stephen Seiler 80/20 polarization bar.
- **Goals & Profile:** Set target event name/date/distance, calculate periodization phase, adjust weekly hours, benchmarks, and constraints.
- **Calendar & Plan:** Day-by-day interactive workout cards, step-by-step interval drawer, and COROS watch display simulation.
- **Ecosystem & Sync:** Live connection indicators, recent backups list, and sync history.
- **Export Center:** One-click download of `.zwo` (Zwift), `.ics` (iCalendar), and `.json` files.

### 2. Intelligent Sports Science Coaching Briefing

Get personalized advice on periodization, race-phase focus, and autonomic readiness:

```bash
# Full coaching guidance in formatted text
adaptpulse coach

# Output machine-readable JSON
adaptpulse coach --json
```

### 3. Multi-Platform Exporters

Export workouts to external platforms and calendar applications:

```bash
# Export all formats (Zwift .zwo XML, iCalendar .ics, and JSON) to plans/export/
adaptpulse export

# Export only Zwift files for next 2 weeks
adaptpulse export --format zwo --weeks 2 --out-dir plans/zwift/

# Export iCalendar file for Google/Apple Calendar
adaptpulse export --format ics --out-dir plans/calendar/
```

### 4. Physiological & Training Load Analytics

Analyze your rolling 30-day physiological state:

```bash
# Full 30-day rolling analysis
adaptpulse analyze

# Custom analysis window
adaptpulse analyze --days 45

# Output raw JSON for automation or scripting
adaptpulse analyze --json
```

Output includes:
- Performance Management Chart: CTL (Fitness), ATL (Fatigue), TSB (Form)
- Acute:Chronic Workload Ratio (ACWR) and sweet-spot validation
- Autonomic readiness score (HRV baseline vs. acute RHR shift)
- Intensity distribution (Zone 1/2 base vs. Zone 3 tempo vs. Zone 4/5 HIIT)

### 5. Athlete Profile Configuration

Configure your training focus, weekly time budget, and preferred periodization:

```bash
# Display active profile settings
adaptpulse profile --show

# Interactively configure goals, hours, and horizon
adaptpulse profile --edit

# Quick update via command-line flags
adaptpulse profile --hours 9.5 --goal running --horizon 2_weeks
```

### 6. Dynamic Rolling Plan Generation

Build structured workouts tailored to your current fitness and recovery status:

```bash
# Dry-run: preview the plan for next week without writing to Intervals.icu
adaptpulse plan-next

# Preview a 2-week block with a custom hourly budget
adaptpulse plan-next --weeks 2 --hours 10.0

# Apply plan to Intervals.icu calendar (read-back verified)
adaptpulse plan-next --apply

# Force update, overwriting any conflicting managed events
adaptpulse plan-next --apply --force
```

### 7. Adaptive Adjustments

React to unexpected fatigue or schedule interruptions:

```bash
# Automatically inspect biometrics and modify upcoming scheduled workouts
adaptpulse adapt --auto --apply

# Manually substitute an intense workout after an exhausting weekend ride
adaptpulse adapt --club-ride-hard --week 1 --apply
```

### 8. Calendar Management & Safe Deletion

Safely inspect, clean up, or restore calendar events:

```bash
# List events in a date window
adaptpulse events list --from 2026-11-01 --to 2026-11-30

# Inspect a specific event
adaptpulse events show <EVENT_ID>

# Delete a single managed event
adaptpulse events delete <EVENT_ID> --confirm-delete

# Delete events matching a prefix with typed confirmation phrase
adaptpulse events delete-by-prefix dynamic --confirm-phrase "DELETE 7 EVENTS"

# Restore from a previous backup
adaptpulse events restore data/backups/backup_20261101_193116_presync.json --apply
```

### 9. COROS Watch Integration Status

Validate device communication and structured workout sync status:

```bash
adaptpulse coros-status
```

### 10. TrainingPeaks API Status

Validate TrainingPeaks Partner API connectivity, profile details, and active training zones:

```bash
adaptpulse tp-status
```

### 11. Plan Compliance & Execution Report

Evaluate planned vs. actual training execution over rolling 7 to 28 days:

```bash
# Rolling 14-day compliance analysis (default)
adaptpulse compliance

# Rolling 28-day compliance analysis
adaptpulse compliance --days 28

# Output raw JSON
adaptpulse compliance --json
```

Metrics calculated:
- Volume Compliance % (Completed vs. Planned Duration)
- Load Compliance % (Completed vs. Planned TSS)
- Execution Score % (Workout timing, discipline, and completion adherence)
- Missed workouts and unplanned training efforts breakdown

### 12. Post-Workout Session Debrief & Aerobic Decoupling

Conduct an immediate post-session debrief to evaluate intensity discipline, cardiac drift, and recovery guidance:

```bash
# Post-workout debrief with Borg RPE and perceived feeling
adaptpulse review-session --duration 60 --rpe 7 --feeling strong

# Debrief with aerobic decoupling (Pw:HR or Pa:HR cardiac drift %)
adaptpulse review-session --duration 90 --rpe 8 --drift 6.2 --avg-hr 152 --feeling heavy

# Output raw JSON
adaptpulse review-session --duration 60 --rpe 6 --json
```

Guidance provided:
- Aerobic decoupling analysis (< 5% indicates aerobic fitness; > 5% indicates drift/fatigue)
- Intensity discipline audit against prescribed target zones
- Next-day recovery adaptation recommendations
- Evidence-based intra-workout fueling critique and next-session fueling adjustments

---

## Ecosystem Integration Guide

### 1. COROS Watches & Bike Computers
1. In the **COROS App**, navigate to **Profile** > **Settings** > **3rd Party Apps**.
2. Select **Intervals.icu** and authorize.
3. Workouts uploaded by AdaptPulse sync straight to your watch calendar with target HR and pace zones.

### 2. TrainingPeaks Partner API
1. Configure `TRAININGPEAKS_ACCESS_TOKEN` in your `.env` file.
2. Run `adaptpulse tp-status` to verify credentials and athlete training zones.
3. Access connection health and sync status through the Ecosystem tab in the Web UI.

### 3. Strava (Activity Feed)
1. In **Intervals.icu**, go to **Settings** > **Connections**.
2. Connect your **Strava** account. Completed runs, rides, and outdoor activities automatically flow into Intervals.icu to update your rolling CTL/ATL and ACWR metrics.

### 4. Hevy (Strength Training)
1. Connect **Hevy** to **Strava** via **Settings** > **Integrations** in the Hevy app.
2. Resistance training workouts sync to Strava as `WeightTraining` and forward to Intervals.icu, ensuring your full training stress profile is captured.

---

## Safety Architecture

AdaptPulse follows strict rules to protect athlete training history:

- **Dry-run First:** No remote mutation occurs without the `--apply` flag.
- **Unmanaged Event Protection:** Only events created by AdaptPulse (or explicitly matching managed prefixes) can be modified or deleted. External workouts and manual entries remain untouched.
- **Activity Immutability:** Completed/recorded activities are never modified or deleted.
- **Pre-sync Backups:** A full snapshot of existing calendar events is saved to `data/backups/` before any create, update, or delete action.
- **Audit Trail:** Every mutating action is recorded in `data/audit.log` with timestamps, operation types, and target IDs.
- **Credential Masking:** API tokens and authorization headers are sanitized and masked in all console outputs and log files.

---

## Development & Testing

Run the automated test suite with coverage reporting:

```bash
coverage run -m pytest && coverage report -m
```

The test suite covers 133 unit, integration, and safety tests with **>95% test coverage (currently 96%)**:
- TrainingPeaks API connector and OAuth token error redaction
- Sports science analytics: ACWR sweet spot/danger zone, PMC (CTL/ATL/TSB), Seiler 80/20 polarization, and Plews/Kiviniemi autonomic readiness
- Intra-workout fueling & hydration prescriptions (carbs g/hr, fluids mL/hr, sodium mg/hr)
- Planned-vs-actual plan compliance engine (rolling volume and TSS adherence)
- Post-workout session review and aerobic decoupling (Pw:HR / Pa:HR drift)
- Multi-sport triathlon periodization (Sprint to 140.6, CSS swim threshold, Brick transitions)
- Periodization phase calculation (Base, Build, Peak, Taper, Recovery)
- Multi-platform workout exporters (Zwift .zwo XML, iCalendar .ics, JSON)
- Embedded multi-page Web UI REST API and request handling
- Schema validation, duration recursion, and COROS hardware display formatting
- Guarded deletions, atomic pre-sync backups, and secret token redaction

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

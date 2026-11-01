# Intervals.icu Adaptive Training Plan Tool

A reliable, safe, CLI-first adaptive training plan management tool for [Intervals.icu](https://intervals.icu).

Designed around a dual-sport 8-week VO2 max & aerobic endurance progression that coordinates seamlessly with strength training (PPL / hypertrophy) and flexible weekend club rides.

---

## Key Features

- **Adaptive Training Engine:**
  - **Hard Weekend Ride Adaptation:** If your weekend club ride is hard or high fatigue, the engine automatically suppresses Thursday's hard bike intervals, substituting a 30-minute restorative spin to protect recovery.
  - **Dynamic Rescheduling:** Move weekend club rides between Saturday and Sunday without duplicate events.
  - **Aerobic Volume Scaling:** Bulk adjust easy aerobic ride durations across weeks with a single command.
- **Safety First & Guarded Mutations:**
  - **Dry-run by default:** Every mutation command (`sync`, `events edit`, `events delete`, `plan reschedule`, `adapt`) simulates changes before writing to Intervals.icu.
  - **Guarded Deletion:** Single deletion requires `--confirm-delete`. Bulk deletion requires typing an exact confirmation phrase (e.g. `--confirm-phrase "DELETE 30 EVENTS"`).
  - **Protected Assets:** Completed activities and unmanaged events outside the plan's prefix are strictly protected.
- **Pre-Flight Diff & Read-Back Verification:**
  - Computes rich diffs between your target plan and live calendar.
  - Detects manual conflicts if workouts were edited directly on Intervals.icu.
  - Re-reads every event after writes to guarantee verified persistence.
  - Automatic JSON backups saved in `data/backups/` before any live mutation.
- **Security & Privacy:**
  - Zero credential leakage: API keys and authorization headers are masked in terminal outputs, logs, and error dumps.
  - Works with `.env` or secure hidden prompts via `getpass`.

---

## Installation & Setup

1. **Clone & Setup Environment:**
   ```bash
   git clone https://github.com/ankitsingh99/training-planner.git
   cd training-planner
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Configure API Credentials:**
   Copy `.env.example` to `.env` and set your key:
   ```bash
   cp .env.example .env
   ```
   In `.env`:
   ```dotenv
   INTERVALS_API_KEY=your_key_here
   ```

3. **Verify Connection & Diagnostics:**
   ```bash
   intervals-plan doctor
   ```
   *(Verifies your API key, discovers your Athlete ID, displays timezone and current metrics).*

---

## CLI Reference

### 1. Diagnostics & Athlete Info
```bash
intervals-plan doctor               # System check & live API connectivity test
intervals-plan athlete show         # Display authenticated athlete profile & metrics
```

### 2. Plan Validation & Preview
```bash
intervals-plan plan validate        # Offline validation of workout durations & steps
intervals-plan plan preview         # Print weekly matrix and session details
intervals-plan plan export-json     # Export plan as Intervals.icu JSON payload
```

### 3. Synchronization (Idempotent & Safe)
```bash
intervals-plan sync                 # Dry-run: shows diff (to create, to update, conflicts)
intervals-plan sync --apply         # Applies mutations with post-write read-back verification
intervals-plan sync --apply --force # Force overwrites any manual conflicts
```

### 4. Adaptive Training Adjustments
```bash
# Suppress Thursday hard bike intervals in Week 1 due to hard weekend club ride:
intervals-plan adapt --club-ride-hard --week 1

# Apply adaptation to live Intervals.icu calendar:
intervals-plan adapt --club-ride-hard --week 1 --apply

# Reschedule weekend club ride from Saturday to Sunday:
intervals-plan plan reschedule --workout weekend-club-ride --week 1 --date 2026-11-08 --apply
```

### 5. Events Inspection & Guarded Deletion
```bash
intervals-plan events list --from 2026-11-02 --to 2026-12-27 # List events in range
intervals-plan events show <EVENT_ID>                        # View complete event JSON
intervals-plan events delete <EVENT_ID> --confirm-delete     # Delete single event
intervals-plan events delete-by-prefix chatgpt-8wk --confirm-phrase "DELETE 31 EVENTS"
intervals-plan events restore <BACKUP_FILE> --apply          # Restore from data/backups/
```

### 6. Audit Trail & Manifest
```bash
intervals-plan manifest show        # View local sync manifest state
intervals-plan audit list           # View recent operations log
```

### 7. Wearable Ecosystem Research
```bash
intervals-plan watch-research       # Comparison of Galaxy Watch, Watchletic, COROS, ZonePace
```

---

## 8-Week Training Plan Architecture

| Week | Monday (Quality Run) | Tuesday (Aerobic Ride) | Thursday (Optional Bike) | Weekend (Club Ride) |
| :--- | :--- | :--- | :--- | :--- |
| **Week 1 (Progression)** | 5 x 3 min (48m 30s) | Zone 2 (40m) | 4 x 4 min (46m) | ~50 km Club Ride |
| **Week 2 (Progression)** | 4 x 4 min (49m) | Zone 2 (45m) | 2 x (10 x 30s / 30s) (48m) | ~50 km Club Ride |
| **Week 3 (Progression)** | 5 x 4 min (56m) | Zone 2 (50m) | 3 x (10 x 30s / 30s) (63m) | ~50 km Club Ride |
| **Week 4 (Deload)** | Deload: 4 x 3 min (45m) | Zone 2 (35m) | *Rest / Recovery* | ~50 km Club Ride |
| **Week 5 (Progression)** | 4 x 5 min (55m) | Zone 2 (55m) | 5 x 4 min (53m) | ~50 km Club Ride |
| **Week 6 (Progression)** | 5 x 4 min (53m 30s) | Zone 2 (60m) | 3 x (13 x 30s / 15s) (62m) | ~50 km Club Ride |
| **Week 7 (Peak)** | 6 x 4 min (63m) | Zone 2 (60m) | 4 x 6 min (58m) | ~50 km Club Ride |
| **Week 8 (Taper)** | Taper: 3 x 3 min (39m) | Zone 2 (40m) | *Rest / Recovery* | **5 km Time Trial Retest** |

- **Week 4 Deload Resolution:** High-intensity Thursday bike intervals are omitted to absorb fatigue and promote muscle recovery.
- **Week 8 Retest Resolution:** Explicit 5 km Time Trial scheduled to measure threshold and VO2 max progression.

---

## Ecosystem Integration (COROS + Strava + Hevy)

```text
       ┌───────────────────────────────┐
       │   Intervals.icu (Core Hub)    │
       │   - 8-Week Training Calendar  │
       │   - Fatigue (ATL) & Form (TSB)│
       └───┬───────────────────────▲───┘
           │ 1. Pushes planned     │ 2. Pulls completed
           │    workouts to watch  │    runs / rides
           ▼                       │
       ┌───────────┐         ┌─────┴─────┐
       │   COROS   ├────────►│  Strava   │
       │   Watch   │ Syncs   │ (Social)  │
       └───────────┘ runs    └─────▲─────┘
                                   │ Syncs gym routines
                             ┌─────┴─────┐
                             │   Hevy    │
                             │ (Strength)│
                             └───────────┘
```

1. **COROS Watch (Endurance Workouts)**:
   - In **COROS App** $\rightarrow$ **Profile** $\rightarrow$ **Settings** $\rightarrow$ **3rd Party Apps** $\rightarrow$ Connect **Intervals.icu**.
   - Your planned workouts will sync directly onto your COROS device calendar.
2. **Strava (Social & Activity Hub)**:
   - In **Intervals.icu Settings** $\rightarrow$ **Connections** $\rightarrow$ Connect **Strava**.
3. **Hevy (Strength Workouts)**:
   - In **Hevy App** $\rightarrow$ **Settings** $\rightarrow$ **Integrations** $\rightarrow$ Connect **Strava**.
   - Gym workouts upload to Strava as `WeightTraining` and sync automatically to Intervals.icu.

---

## Running the Automated Test Suite

Run all unit, integration, and safety tests:
```bash
pytest
```
*Result: 28 passing tests covering schema, duration recursion, diff detection, conflict handling, secret masking, and guarded deletion.*

---

## License
MIT License.

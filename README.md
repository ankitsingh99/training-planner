# Intervals.icu Adaptive Training Plan Tool & Sports Science Suite

A reliable, safe, CLI-first adaptive training suite for [Intervals.icu](https://intervals.icu).

Combines **real-time body analytics (HRV, resting HR, sleep, wellness)** and **completed workout data** to dynamically plan and adapt your next 1 or 2 weeks of training. Grounded in peer-reviewed sports science research: **Stephen Seiler's 80/20 Polarized Model**, **Tim Gabbett's Acute:Chronic Workload Ratio (ACWR)**, **Coggan/Banister Performance Management (CTL/ATL/TSB)**, and **Kiviniemi/Plews HRV & Resting Heart Rate Autonomic Decision Trees**.

Coordinates seamlessly with **COROS** watches/bike computers, **Strava**, and **Hevy** strength training.

---

## Key Features

- **Rolling 30-Day Physiological & Training Load Analytics (`analyze`):**
  - **Performance Management Chart (PMC):** Real-time Fitness (CTL), Fatigue (ATL), and Form (TSB).
  - **Acute:Chronic Workload Ratio (ACWR):** Evaluates injury risk and workload progression using Tim Gabbett's "Sweet Spot" (0.8–1.3) vs. Danger Zone (>1.5).
  - **Autonomic Nervous System & Recovery:** Tracks 30-day baseline resting HR and HRV. Automatically detects acute sympathetic strain (e.g. resting HR spike after hard weekend rides).
  - **Intensity Polarization:** Evaluates actual time in Stephen Seiler's 3-zone model (low aerobic base vs. moderate grey zone vs. high-intensity intervals).
- **Personalized Rolling Training Planner (`plan-next`):**
  - Synthesizes 30-day body data and completed workouts to plan the next **1 or 2 weeks**.
  - Dynamically scales volume to your weekly time commitment (e.g. **8+ hours/week**).
  - **Auto-Adapts Intensity to Recovery:** Automatically substitutes high-intensity VO2 intervals with active recovery spins or aerobic flushes whenever elevated fatigue or resting HR spikes are detected.
  - Fully compatible with COROS watches (plain ASCII, short <=20 character step cues, complete coaching notes).
- **Configurable Athlete Profile & Training Goals (`profile`):**
  - Interactive prompts and CLI flags to adjust your primary athletic goal (dual-sport hybrid, running, cycling, general fitness), weekly commitment hours, training philosophy (80/20 polarized, pyramidal, HRV-governed), and planning horizon.
- **Safety First & Guarded Mutations:**
  - **Dry-run by default:** Every mutation command (`plan-next`, `sync`, `events delete`, `adapt`) defaults to preview mode.
  - Requires explicit `--apply` to update Intervals.icu.
  - Single deletion requires `--confirm-delete`. Bulk deletion requires typing an exact confirmation phrase.
  - Pre-flight diff checking and read-back verification on all remote mutations.
  - Automatic timestamped backups saved in `data/backups/`.
- **Security & Privacy:**
  - Zero credential leakage: API keys and authorization headers masked across all CLI outputs and logs.

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

---

## Complete Training Suite CLI Reference

### 1. Physiological Analytics & Training Load
```bash
intervals-plan analyze              # Run 30-day rolling analysis (CTL/ATL/TSB, ACWR, Resting HR, Seiler 80/20)
intervals-plan analyze --days 60    # Analyze over 60-day window
intervals-plan analyze --json       # Output machine-readable JSON metrics
```

### 2. Athlete Goals & Profile Configuration
```bash
intervals-plan profile --show       # View current goal, weekly hours, benchmarks, and philosophy
intervals-plan profile --edit       # Interactively edit goals, hours, or periodization model
intervals-plan profile --hours 9.0  # Adjust weekly training budget via CLI flag
intervals-plan profile --goal running --horizon 2_weeks
```

### 3. Dynamic Rolling Plan Generator
```bash
intervals-plan plan-next            # Preview next week's personalized plan (Dry Run)
intervals-plan plan-next --weeks 2  # Plan next 2 weeks (14 days)
intervals-plan plan-next --apply    # Commit personalized plan to Intervals.icu & queue for COROS
intervals-plan plan-next --hours 8.5 --apply --force
```

### 4. Adaptive Adjustments
```bash
intervals-plan adapt --auto         # Auto-detect fatigue from 30d wellness/activities and adapt schedule
intervals-plan adapt --club-ride-hard --week 1 --apply  # Manually substitute recovery spin for hard ride
```

### 5. Calendar Events & Guarded Deletion
```bash
intervals-plan events list --from 2026-11-02 --to 2026-11-15 # List live events
intervals-plan events show <EVENT_ID>                        # View complete event JSON
intervals-plan events delete <EVENT_ID> --confirm-delete     # Delete single event
intervals-plan events delete-by-prefix dynamic --confirm-phrase "DELETE 7 EVENTS"
intervals-plan events restore <BACKUP_FILE> --apply          # Restore from data/backups/
```

### 6. COROS Watch Connection Status
```bash
intervals-plan coros-status         # Check live COROS cloud connection and workout upload status
```

---

## Running the Automated Test Suite

Run all unit, integration, and sports science analytics tests:
```bash
pytest
```
*Result: 40 passing tests covering schema, ACWR sweet spot & danger zone calculations, autonomic readiness, Seiler 80/20 distribution, dynamic periodization, and guarded deletion.*

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

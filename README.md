# Training Planner

An 8-week run & bike training plan generator and bulk uploader for [Intervals.icu](https://intervals.icu).

## Features
- **Structured 8-Week Progression:** Monday quality runs, Tuesday easy aerobic rides, optional Thursday bike VO2 intervals, and Saturday club-ride notes.
- **Intervals.icu Bulk API Integration:** Upserts workouts and reminders via the bulk API with idempotency through unique `external_id` tags.
- **No External Dependencies:** Built with pure Python standard library.
- **Convenient Tooling:** Includes scripts to generate formatted Markdown overviews and push to Intervals.icu with one command.

---

## Getting Started

### 1. Configure Credentials
Copy `.env.example` to `.env` and insert your Intervals.icu API key:
```bash
cp .env.example .env
```
Edit `.env`:
```dotenv
INTERVALS_API_KEY=your_intervals_api_key_here
```
*(You can obtain your API key in Intervals.icu under Settings → Developer / API Access).*

---

## Usage

### Generate and View Workouts in Terminal & Markdown
To generate the full human-readable workout breakdown and print it to your terminal:
```bash
./generate_md.sh
```
This produces `ALL_WORKOUTS.md` with every workout's target zones, intervals, duration, and structure.

### Upload Workouts to Intervals.icu
To push all 30 events to your Intervals.icu calendar:
```bash
./push_intervals.sh
```
Alternatively, using the Python script directly:
```bash
# Dry run preview (no changes made)
python3 upload_intervals_plan.py

# Push to calendar
python3 upload_intervals_plan.py --upload
```

---

## Comprehensive Training Ecosystem (COROS + Strava + Hevy)

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
   - In the **COROS App** $\rightarrow$ **Profile** $\rightarrow$ **Settings** $\rightarrow$ **3rd Party Apps** $\rightarrow$ Connect **Intervals.icu**.
   - Your planned workouts will sync directly onto your COROS watch calendar. Completed runs and rides will automatically upload back to Intervals.icu.
2. **Strava (Social & Activity Hub)**:
   - In **Intervals.icu Settings** $\rightarrow$ **Connections** $\rightarrow$ Connect **Strava**.
   - Also connect Strava inside the COROS app so watch workouts post to your social feed.
3. **Hevy (Strength Workouts)**:
   - In the **Hevy App** $\rightarrow$ **Settings** $\rightarrow$ **Integrations** $\rightarrow$ Connect **Strava**.
   - When you log a workout in Hevy, it uploads to Strava as `WeightTraining`. Intervals.icu will automatically import it, tracking your gym load against your fatigue curve!

---

## Project Structure

```text
├── upload_intervals_plan.py  # Core script: builds events and syncs with Intervals.icu API
├── generate_all_md.py        # Generates ALL_WORKOUTS.md from the event definitions
├── generate_md.sh            # Shell wrapper to generate and print workouts to terminal
├── push_intervals.sh         # Shell script to upload workouts using .env credentials
├── ALL_WORKOUTS.md           # Full markdown breakdown of all 30 events
├── PLAN.md                   # Initial plan preview document
├── .env.example              # Template for environment configuration
├── .gitignore                # Excludes secrets (.env) and temporary files
└── README.md                 # Project documentation
```

---

## License
MIT License.

# Personal AI Training Analyst
## Codex-Ready Project Specification

**Project type:** Personal fitness data platform, analytics engine and AI training coach  
**Primary objective:** Improve strength, hypertrophy, cardiovascular fitness and recovery through continuous analysis of personal training data.  
**Data sources:** COROS and Hevy  
**Optional integration:** Intervals.icu  
**Explicit exclusion:** Strava

---

# 1. Project vision

Build a personal AI-powered training analyst that consolidates endurance and strength-training data, evaluates fitness progression, identifies weaknesses and generates adaptive training recommendations.

The application should function as a long-term fitness intelligence system rather than simply a workout tracker.

It must be capable of answering questions such as:

- Am I getting stronger?
- Is my VO₂ max improving?
- Am I doing enough training volume for each muscle group?
- Is my cycling or running performance improving?
- Am I accumulating excessive fatigue?
- Is my current training split compatible with my endurance goals?
- Which exercises should I progress, replace or deload?
- What should I train today based on recent training and recovery?
- How should my next week of training change based on actual results?

The system should combine deterministic calculations with AI interpretation.

**Core architectural principle:**

1. Import and normalize training data.
2. Calculate reliable fitness metrics.
3. Identify trends and anomalies.
4. Let the AI interpret the results.
5. Generate recommendations and proposed training changes.
6. Track whether those recommendations actually improve performance.

The AI must never invent missing measurements or present estimates as verified data.

---

# 2. User profile and initial baseline

The following information represents the initial historical profile. It must be treated as a starting reference, not as permanently current information.

## 2.1 Personal metrics

| Metric | Initial reported value |
|---|---:|
| Age | 27 years |
| Height | 172 cm |
| Weight | 78.8 kg |
| Body fat | 27% |
| Fat mass | 21.3 kg |
| Muscle mass | 31.3 kg |
| Resting heart rate | 53 bpm |
| HRV | 86 ms |
| Initial VO₂ max | 42 |

COROS subsequently reported a VO₂ max of approximately 43 in the available snapshot.

The system must reconcile historical self-reported metrics with newly imported device measurements. Each measurement should retain its source and timestamp.

## 2.2 Training priorities

The system should optimize three broad objectives:

1. Hypertrophy and strength development.
2. Cardiovascular fitness and VO₂ max improvement.
3. Body composition improvement.

These goals should be configurable rather than hardcoded.

The coach must understand that strength training and endurance training compete for recovery resources. It should manage concurrent training intelligently rather than maximizing every training variable independently.

## 2.3 Training preferences

- Morning cycling or running.
- Evening gym sessions.
- Historically follows a six-day Push/Pull/Legs split.
- Tuesday has historically been the gym rest day.
- Weekend cycling club rides are flexible.
- Typical club ride: approximately 50 km, including social and coffee time.
- Prefers challenging workouts but wants fatigue and recovery monitored.
- Wants a practical system that does not require additional paid applications.

These preferences should be editable through configuration.

---

# 3. Existing equipment and platforms

| Equipment/platform | Purpose |
|---|---|
| COROS DURA | Cycling activity tracking |
| Samsung Galaxy Watch 4 | Running activity tracking |
| Chest heart-rate sensor | Heart-rate monitoring |
| Cadence sensor | Cycling cadence |
| Hevy | Strength workouts and exercise history |
| Intervals.icu | Optional endurance training planning and synchronization |

Strava is explicitly out of scope.

The application must not depend on Strava for importing activities, analyzing performance or synchronizing workouts.

---

# 4. Data ingestion

Data ingestion is the foundation of the entire application.

The system must support historical imports as well as incremental synchronization.

## 4.1 COROS integration

Retrieve all available relevant data through supported COROS interfaces and account integrations.

Required data categories:

### Activities
- Activity ID
- Activity type
- Start and end time
- Duration
- Distance
- Average speed and pace
- Average and maximum heart rate
- Average and maximum cadence
- Elevation gain and loss
- Calories
- Training effect
- Training load
- GPS data where available
- Lap and interval data
- Power data where available

### Fitness and recovery
- VO₂ max
- Resting heart rate
- HRV
- Recovery status
- Training load
- Acute and chronic training load
- Training load ratio
- Threshold pace
- Threshold heart rate
- Race predictions
- Sleep and wellness metrics where available

### Requirements
- Preserve the original source data.
- Retain timestamps and time zones.
- Support incremental imports.
- Prevent duplicate activities.
- Maintain historical snapshots of changing fitness metrics.
- Record failed imports and incomplete data.

Do not assume every COROS metric is available through every integration.

## 4.2 Hevy integration

Hevy is the primary strength-training data source.

Retrieve:

### Workout history
- Workout ID
- Workout title
- Date and time
- Duration
- Exercise names
- Exercise order
- Sets
- Repetitions
- Weight
- Distance where applicable
- Duration where applicable
- Set type
- Rest periods where available
- Notes

### Planned routines
- Routine name
- Exercise sequence
- Sets and repetitions
- Target weights where available
- Exercise notes
- Routine structure

### Requirements
- Support historical workout imports.
- Support routine imports.
- Track changes in routines.
- Identify exercise substitutions and naming variations.
- Preserve the original exercise names.
- Normalize exercise names separately.
- Distinguish planned workouts from completed workouts.

If direct API access is unavailable, investigate supported export/import methods first.

Hevy data exports should be supported as an alternative ingestion mechanism.

Do not rely on undocumented private endpoints or bypass application security.

## 4.3 Historical data

The application should support importing all available historical data, not just recent activities.

The import process must:

1. Retrieve available records.
2. Paginate through all records.
3. Identify duplicates.
4. Normalize data.
5. Store source identifiers.
6. Record import timestamps.
7. Validate record counts.
8. Produce an import report.

A partial import must never be presented as a complete historical dataset.

---

# 5. Unified data architecture

Create a normalized internal data model independent of the source platform.

Recommended entities:

## UserProfile
- user_id
- age
- height
- weight
- training_preferences
- goals
- heart_rate_zones
- available_equipment
- training_constraints

## Activity
- activity_id
- source
- source_activity_id
- activity_type
- start_time
- duration
- distance
- elevation
- average_heart_rate
- maximum_heart_rate
- average_speed
- average_pace
- calories
- training_load
- raw_data_reference

## StrengthWorkout
- workout_id
- source
- source_workout_id
- workout_name
- date
- duration
- exercises

## Exercise
- exercise_id
- original_name
- normalized_name
- muscle_groups
- movement_pattern
- equipment
- exercise_category

## ExerciseSet
- set_id
- exercise_id
- workout_id
- set_number
- repetitions
- weight
- duration
- distance
- set_type
- estimated_rir

## PlannedWorkout
- planned_workout_id
- date
- workout_type
- workout_structure
- target_intensity
- status
- source
- external_id

## FitnessSnapshot
- snapshot_id
- timestamp
- vo2_max
- resting_heart_rate
- hrv
- threshold_pace
- threshold_heart_rate
- training_load
- recovery_status

## CoachRecommendation
- recommendation_id
- created_at
- recommendation_type
- recommendation
- rationale
- confidence
- status
- outcome

All records should preserve provenance: source platform, import time and original identifier.

---

# 6. Analytics engine

The analytics engine should calculate metrics independently of the AI model.

AI should interpret calculated results, not perform critical calculations from raw data without validation.

## 6.1 Cardiovascular fitness

Track:

- VO₂ max trend
- Resting heart-rate trend
- HRV trend
- Threshold pace
- Threshold heart rate
- Aerobic endurance
- Time spent in heart-rate zones
- Training load
- Acute-to-chronic workload trends
- Cycling speed progression
- Running pace progression
- Long-duration endurance performance

Display trends over:

- 7 days
- 28 days
- 90 days
- 6 months
- All available history

Distinguish between actual measured changes and normal day-to-day variability.

## 6.2 Cycling analysis

Calculate:

- Weekly cycling distance
- Weekly cycling duration
- Average speed trends
- Elevation gain
- Heart-rate distribution
- Cadence distribution
- Training load
- Long-ride progression
- Endurance consistency
- Performance at comparable heart rates

Where power data is unavailable, do not invent power-based metrics.

Avoid interpreting average speed as a pure fitness measurement because wind, terrain, traffic and group riding can significantly affect it.

## 6.3 Running analysis

Calculate:

- Weekly running distance
- Weekly running duration
- Average pace
- Heart-rate distribution
- Pace at comparable heart rates
- Longest run
- Frequency
- Training load
- Threshold pace progression

Identify whether improvements are caused by better fitness, easier terrain or different environmental conditions where possible.

## 6.4 Strength analytics

Track:

- Total sets per muscle group
- Weekly volume
- Exercise frequency
- Weight progression
- Repetition progression
- Estimated one-rep max
- Performance at comparable repetitions
- Training frequency
- Exercise consistency
- Personal records

Use a consistent estimated one-rep-max formula and label the result as an estimate.

For example, the Epley formula:

`Estimated 1RM = Weight × (1 + Repetitions / 30)`

Do not calculate estimated 1RM from unsuitable sets, such as very high-repetition sets or sets with unreliable weight data.

## 6.5 Muscle-group mapping

Create a configurable exercise-to-muscle mapping.

Example:

| Exercise | Primary muscles | Secondary muscles |
|---|---|---|
| Bench press | Chest | Triceps, front delts |
| Incline dumbbell press | Upper chest | Triceps, front delts |
| Overhead press | Shoulders | Triceps |
| Lat pulldown | Lats | Biceps |
| Chest-supported row | Back | Biceps, rear delts |
| Squat | Quadriceps | Glutes |
| Romanian deadlift | Hamstrings | Glutes |
| Leg press | Quadriceps | Glutes |

Allow fractional contribution to secondary muscle groups.

Avoid simply counting every exercise as a full set for every involved muscle.

## 6.6 Recovery and fatigue

Analyze:

- Recent training load
- Long-term training load
- Training load ratio
- HRV deviations from baseline
- Resting heart-rate deviations
- Sleep duration where available
- Workout frequency
- High-intensity session frequency
- Muscle-group recovery exposure

The application should not use a single recovery score as the sole basis for training decisions.

Use multiple indicators and communicate uncertainty.

---

# 7. AI training coach

The AI coach is the main user-facing intelligence layer.

It should have access to:

- User profile
- Historical training data
- Recent activities
- Strength progression
- Fitness trends
- Recovery metrics
- Planned workouts
- Training goals
- User preferences

## 7.1 Daily analysis

Generate a daily assessment containing:

1. Recent training summary.
2. Recovery assessment.
3. Fatigue indicators.
4. Recommended training session.
5. Suggested intensity.
6. Any necessary modifications.
7. Explanation of the recommendation.

Example:

"Your recent cycling volume is higher than your normal baseline, while your last lower-body session was relatively recent. Keep today's cycling aerobic and avoid adding another high-intensity lower-body session."

This is illustrative, not a fixed recommendation.

## 7.2 Weekly review

Generate a structured report covering:

- Total cycling volume
- Total running volume
- Total gym sessions
- Muscle-group volume
- Strength progression
- VO₂ max progression
- Recovery trends
- Training-load trends
- Adherence to planned workouts
- Missed workouts
- Key improvements
- Potential issues

End with an actionable plan for the following week.

## 7.3 Monthly review

Assess:

- Overall fitness progression
- Strength development
- Hypertrophy-related training consistency
- Cardiovascular improvement
- Body-composition changes where measurements exist
- Recovery patterns
- Training adherence
- Goal progress

Identify which training variables are working and which should change.

## 7.4 Adaptive planning

The AI should be capable of:

- Increasing or reducing workout intensity.
- Modifying weekly volume.
- Adjusting exercise selection.
- Recommending deloads.
- Moving sessions.
- Reducing conflicting endurance and strength workloads.
- Incorporating club rides.
- Updating future training blocks.

Recommendations should be proposed first. Changes to existing planned workouts should require explicit user approval.

---

# 8. Workout planning and management

Workout planning must be a first-class feature.

The application should support creating, editing, deleting and rescheduling workouts.

## 8.1 Strength workouts

Allow the coach to generate:

- Push workouts
- Pull workouts
- Leg workouts
- Upper/lower splits
- Full-body sessions
- Custom sessions

Each workout should include:

- Exercise
- Sets
- Repetitions
- Target weight
- Target RIR
- Rest time
- Exercise notes
- Progression instructions

## 8.2 Endurance workouts

Support:

- Zone 2 cycling
- Recovery rides
- Tempo rides
- Threshold intervals
- VO₂ max intervals
- Easy runs
- Tempo runs
- Interval runs
- Long endurance sessions

Where supported, include structured interval steps:

- Warm-up
- Work interval
- Recovery interval
- Repetitions
- Cool-down

## 8.3 Planning rules

The planner must account for:

- Weekly training availability
- Existing gym schedule
- Tuesday gym rest preference
- Flexible weekend club ride
- Recovery status
- Recent workload
- Strength and endurance interference
- Goal priorities

Do not automatically schedule demanding lower-body training immediately before an important endurance session without considering recovery.

---

# 9. Intervals.icu integration

Intervals.icu is an optional integration.

The core application must remain useful without it.

Potential capabilities:

- Read athlete and training data.
- Read planned workouts.
- Create planned workouts.
- Update planned workouts.
- Delete planned workouts.
- Synchronize planned sessions.
- Track synchronization status.

Use the official API and supported authentication methods.

For API authentication, use a local environment variable or secure credential mechanism.

Never hardcode API keys in source code.

Never ask the user to paste secrets into the project documentation or commit them to Git.

Use stable external identifiers to prevent duplicate workout creation.

For bulk synchronization, investigate the supported bulk event endpoints and upsert behavior in the current API documentation before implementation.

A synchronization operation should:

1. Validate the planned workout.
2. Check whether it already exists.
3. Create or update the event.
4. Save the external identifier.
5. Record synchronization status.
6. Handle errors without silently losing local data.

Do not claim that a strength workout is fully executable on a watch unless the destination platform actually supports that functionality.

---

# 10. Dashboard

Build a clean, responsive dashboard.

## 10.1 Overview

Display:

- Current weight
- VO₂ max
- Resting heart rate
- HRV
- Weekly training duration
- Weekly distance
- Gym sessions
- Training-load trend
- Recovery status

## 10.2 Cardiovascular dashboard

Include:

- VO₂ max chart
- Running pace trend
- Cycling speed trend
- Heart-rate zones
- Weekly endurance volume
- Training-load chart

## 10.3 Strength dashboard

Include:

- Weekly muscle-group volume
- Exercise progression
- Estimated 1RM trends
- Personal records
- Training frequency
- Workout history

## 10.4 Recovery dashboard

Include:

- HRV trend
- Resting heart-rate trend
- Training load
- Recent high-intensity sessions
- Recovery indicators

## 10.5 Training calendar

Show:

- Completed workouts
- Planned workouts
- Missed workouts
- Rescheduled workouts
- Synchronization status

---

# 11. Recommended technical architecture

Use a modular architecture that is easy for Codex to understand, maintain and extend.

Suggested stack:

| Layer | Recommended technology |
|---|---|
| Backend | Python |
| API | FastAPI |
| Database | SQLite initially |
| ORM | SQLAlchemy |
| Data processing | Pandas |
| Validation | Pydantic |
| Frontend | React or a lightweight dashboard framework |
| Charts | Recharts or equivalent |
| AI integration | Configurable LLM provider |
| Testing | Pytest |
| Scheduling | APScheduler or system scheduler |
| Deployment | Local-first |

Avoid unnecessary infrastructure.

Do not introduce Kubernetes, microservices, Redis or a complex cloud architecture unless a genuine requirement emerges.

The initial product should run locally on the user's machine.

## 11.1 Suggested repository structure

```text
personal-training-analyst/
│
├── PROJECT_SPEC.md
├── README.md
├── .env.example
├── .gitignore
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── connectors/
│   │   ├── coros/
│   │   ├── hevy/
│   │   └── intervals_icu/
│   │
│   ├── ingestion/
│   │   ├── import_activities.py
│   │   ├── import_workouts.py
│   │   └── validation.py
│   │
│   ├── models/
│   │   ├── activity.py
│   │   ├── strength.py
│   │   ├── exercise.py
│   │   ├── planned_workout.py
│   │   └── fitness_snapshot.py
│   │
│   ├── analytics/
│   │   ├── cardiovascular.py
│   │   ├── cycling.py
│   │   ├── running.py
│   │   ├── strength.py
│   │   ├── recovery.py
│   │   └── training_load.py
│   │
│   ├── coach/
│   │   ├── daily_review.py
│   │   ├── weekly_review.py
│   │   ├── monthly_review.py
│   │   ├── planner.py
│   │   └── prompts/
│   │
│   ├── services/
│   │   ├── synchronization.py
│   │   └── reporting.py
│   │
│   └── tests/
│
├── frontend/
│
├── data/
│   ├── imports/
│   ├── exports/
│   └── database/
│
└── docs/
    ├── architecture.md
    ├── data_dictionary.md
    ├── integrations.md
    └── development_log.md
```

---

# 12. Data quality and safety requirements

These requirements are mandatory.

## Data integrity

- Never silently discard imported records.
- Never overwrite historical source data without retaining provenance.
- Deduplicate using source IDs wherever possible.
- Keep raw imports available for debugging.
- Record failed imports.
- Validate units and timestamps.
- Distinguish zero values from missing values.
- Identify suspicious or implausible measurements.

## Analytics integrity

- Distinguish measured metrics from estimated metrics.
- Do not fabricate missing heart-rate, power or weight values.
- Do not compare incompatible workout conditions without qualification.
- Explain uncertainty in fitness predictions.
- Avoid treating training-load ratios as medical diagnoses.

## Training safety

- Recommendations must consider accumulated fatigue.
- Do not encourage training through pain or injury.
- Flag unusual recovery patterns.
- Encourage appropriate rest.
- Avoid aggressive increases in training volume.
- Do not make medical diagnoses.

The system should provide conservative recommendations when data quality or recovery information is insufficient.

---

# 13. Development roadmap

Implement the project in phases.

## Phase 1 — Foundation

- Initialize repository.
- Create configuration.
- Set up SQLite.
- Define database models.
- Create logging.
- Add tests.
- Document architecture.

**Deliverable:** A working local application foundation.

## Phase 2 — Data ingestion

- Import COROS activities.
- Import COROS fitness metrics.
- Import Hevy workout history.
- Import Hevy routines.
- Support file-based imports.
- Normalize records.
- Deduplicate records.
- Generate an import report.

**Deliverable:** A validated historical training database.

## Phase 3 — Analytics

- Implement cycling metrics.
- Implement running metrics.
- Implement strength metrics.
- Implement muscle-group volume.
- Implement recovery metrics.
- Implement training-load trends.
- Add automated tests.

**Deliverable:** A deterministic fitness analytics engine.

## Phase 4 — AI coach

- Implement daily review.
- Implement weekly review.
- Implement monthly review.
- Implement conversational fitness analysis.
- Add adaptive recommendations.
- Add recommendation history.

**Deliverable:** A functioning AI training analyst.

## Phase 5 — Training planner

- Generate strength workouts.
- Generate endurance workouts.
- Create training weeks.
- Edit and reschedule sessions.
- Track completion.
- Compare planned versus actual training.

**Deliverable:** An adaptive training planner.

## Phase 6 — Integrations

- Implement Intervals.icu authentication.
- Read planned workouts.
- Create planned workouts.
- Update planned workouts.
- Delete planned workouts.
- Add synchronization safeguards.

**Deliverable:** Optional external workout synchronization.

## Phase 7 — Dashboard

- Build overview.
- Build cardiovascular dashboard.
- Build strength dashboard.
- Build recovery dashboard.
- Build training calendar.

**Deliverable:** A complete personal fitness intelligence platform.

---

# 14. Codex development instructions

Codex should follow these rules throughout development.

## General rules

1. Read this specification before making architectural decisions.
2. Inspect the repository before changing files.
3. Do not rewrite working modules unnecessarily.
4. Prefer small, independently testable components.
5. Keep business logic separate from AI prompts.
6. Keep external integrations separate from analytics.
7. Use type hints.
8. Add tests for calculations.
9. Document assumptions.
10. Keep secrets outside source control.

## Data rules

1. Source data must remain traceable.
2. Every imported record must have a source.
3. Historical data must be retained.
4. Duplicate records must be handled safely.
5. Missing values must remain missing.
6. Never invent metrics to fill gaps.

## AI rules

1. Provide the AI with structured analytics rather than unprocessed data dumps.
2. Require recommendations to reference supporting metrics.
3. Distinguish observations from recommendations.
4. Include uncertainty where relevant.
5. Require confirmation before destructive or external synchronization operations.
6. Preserve a record of recommendations and their outcomes.

## Development workflow

For each feature:

1. Inspect relevant modules.
2. Explain the proposed implementation briefly.
3. Implement the smallest complete version.
4. Add tests.
5. Run tests.
6. Fix regressions.
7. Update documentation.
8. Summarize changed files and remaining limitations.

Do not implement the entire system in one large code-generation operation.

---

# 15. Initial task for Codex

Start by building the project foundation and auditing the available data.

Use the following initial task:

## Task 1: Repository foundation and data audit

Read `PROJECT_SPEC.md` and inspect the current repository.

Then:

1. Identify existing files and reusable components.
2. Create a development plan.
3. Establish the project structure.
4. Implement the configuration system.
5. Create the initial SQLite database.
6. Define the core database models.
7. Implement data validation utilities.
8. Add logging and error handling.
9. Create unit tests.
10. Prepare the COROS and Hevy ingestion interfaces.

Before implementing integrations, inspect which supported connection methods and exports are actually available.

If historical data is already accessible, perform a complete import audit.

Produce a report containing:

- Number of imported activities.
- Number of imported strength workouts.
- Number of imported exercises.
- Available fitness metrics.
- Earliest and latest records.
- Duplicate records identified.
- Missing data.
- Import errors.
- Data fields unavailable through the current integration.

Do not begin AI recommendations until the underlying data has been validated.

---

# 16. Definition of success

The project is successful when it can:

- Maintain a unified historical record of cycling, running and strength training.
- Reliably calculate fitness and training trends.
- Track progression across individual exercises and muscle groups.
- Evaluate recovery and accumulated training load.
- Generate practical daily and weekly training recommendations.
- Create and manage planned workouts.
- Compare planned training with actual performance.
- Improve recommendations using observed results.
- Operate locally without requiring a collection of paid services.

The long-term goal is a personal AI coach that understands the user's training history, knows what has and has not worked, and continually improves the training strategy based on measurable outcomes.

---

# 17. Final product philosophy

Build a reliable fitness intelligence system first and an AI coach second.

The quality of the recommendations will depend on the quality of the underlying data and analytics.

Prioritize:

1. Data accuracy.
2. Historical completeness.
3. Reliable calculations.
4. Useful visualizations.
5. Explainable recommendations.
6. Adaptive training.
7. Automation.

Avoid building an impressive-looking dashboard that produces unreliable conclusions.

The system should help answer one central question:

**What is the most effective training adjustment I can make now to improve my long-term fitness and performance, given what my actual training data tells us?**

---

# 18. Acceptance tests and release gates

This section defines concrete, measurable conditions that Codex must satisfy before considering a feature complete.

Acceptance tests must be automated wherever possible. Tests should use deterministic fixtures and mocked external services; they must not depend on live COROS, Hevy, Intervals.icu or AI provider availability.

Every acceptance test must have:
- A unique ID.
- Preconditions or test data.
- An action.
- An expected result.
- A test implementation or a documented reason why automation is not possible.

A feature is not complete merely because its code has been written.

## 18.1 Test infrastructure requirements

**AT-001 — Automated test execution**

Given a clean checkout with documented dependencies installed, when the developer runs the documented test command, all automated unit and integration tests must execute and return a non-zero exit code if any test fails.

**AT-002 — Test isolation**

Tests must use a temporary database and isolated test data. Running the test suite must not modify the user's real training database or imported source files.

**AT-003 — Reproducibility**

The same test fixtures and code version must produce identical deterministic analytics results across repeated test runs.

**AT-004 — Coverage of critical logic**

All critical calculations, data normalization functions, deduplication logic and synchronization safeguards must have automated tests. Target at least 90% line coverage for these modules, without treating coverage percentage as a substitute for meaningful assertions.

## 18.2 Data ingestion acceptance tests

**AT-010 — Complete historical pagination**

Given a mocked source containing 250 activities distributed across five pages of 50 records, when the import process runs, all 250 unique activities must be stored.

Expected:
- 250 imported activities.
- No page skipped.
- Import report identifies five successfully processed pages.
- No false declaration of completeness if a page fails.

**AT-011 — Duplicate import prevention**

Given 100 unique activities, when the same export is imported twice, the database must contain 100 activities, not 200.

Expected:
- Original source IDs remain unchanged.
- Second import reports 100 existing records.
- No duplicate activity rows are created.

**AT-012 — Partial import recovery**

Given a five-page import where page four fails, the application must preserve successfully imported records and record the failed page.

When the import is retried, it must retrieve the missing data without duplicating previously imported records.

**AT-013 — Missing values**

Given an activity without heart rate, power or cadence, the application must store those fields as missing/null.

It must not substitute zero, calculate fabricated values or silently remove the activity.

**AT-014 — Unit normalization**

Given equivalent activity records expressed in supported units, the normalized database must store consistent units.

Example:
- 5 km and 5,000 m must normalize to the same distance.
- 60 minutes and 3,600 seconds must normalize to the same duration.

**AT-015 — Time-zone correctness**

Given an activity timestamp with an explicit UTC offset, the application must preserve the original timestamp and correctly calculate its local calendar date.

Activities near midnight must not be incorrectly assigned to the previous or following training day.

**AT-016 — Source provenance**

Every imported activity and strength workout must retain:
- Source platform.
- Original source ID.
- Import timestamp.
- Reference to raw source data or a recoverable source payload.

**AT-017 — Corrupt import handling**

Given a malformed record in an otherwise valid import file, the importer must:
- Reject or quarantine the malformed record.
- Continue processing valid records where safe.
- Record the validation error.
- Report valid and rejected record counts separately.

**AT-018 — Import audit**

After an import, the generated report must include:
- Records discovered.
- Records inserted.
- Records updated.
- Duplicates skipped.
- Records rejected.
- Import errors.
- Date range covered.

All reported counts must reconcile with the actual database operations.

## 18.3 Hevy and strength-data acceptance tests

**AT-020 — Workout reconstruction**

Given a Hevy export containing three workouts, five exercises and 40 sets, importing it must create the correct workout, exercise and set relationships.

No set may be attached to the wrong workout or exercise.

**AT-021 — Exercise-name normalization**

Given exercise names such as:
- Bench Press
- Barbell Bench Press
- Bench Press (Barbell)

The normalization layer may map them to one canonical exercise only when the mapping is explicitly configured or confidently established.

Original names must always remain available.

Ambiguous names must not be automatically merged.

**AT-022 — Exercise substitution**

Given a workout where a user replaces barbell bench press with dumbbell bench press, the application must preserve the distinction between exercises while allowing both to contribute to the configured chest and triceps muscle groups.

**AT-023 — Set validity**

Given sets with valid weight and repetitions alongside malformed or incomplete sets, valid sets must be retained and invalid fields must be flagged.

Missing weight must not become zero kilograms.

**AT-024 — Routine import**

Given a routine with six exercises, when imported, all six exercises must retain their order, prescribed sets, repetition ranges and available notes.

**AT-025 — Workout completion matching**

Given a planned strength workout and a completed workout with matching identifiers or an explicitly approved matching rule, the application must associate them without creating a duplicate planned session.

Ambiguous matches must be presented for review.

## 18.4 Analytics acceptance tests

Use small, explicitly documented fixture datasets with hand-calculated expected results.

**AT-030 — Weekly distance**

Given three cycling activities of 20 km, 30 km and 50 km in the same local calendar week, weekly cycling distance must equal 100 km.

A running activity must not contribute to cycling distance.

**AT-031 — Weekly training duration**

Given activities lasting 30, 45 and 60 minutes, total duration must equal 135 minutes.

Duration must not be inferred from distance when an actual duration is unavailable.

**AT-032 — Average speed**

Given a 40 km ride completed in 2 hours, average speed must equal 20 km/h.

If the activity duration is missing or zero, average speed must be reported as unavailable rather than infinity or an arbitrary value.

**AT-033 — Running pace**

Given a 10 km run completed in 60 minutes, average pace must equal 6:00 min/km.

The system must use a consistent pace representation and handle zero or missing distance safely.

**AT-034 — Heart-rate zone distribution**

Given a test activity containing 10 minutes in Zone 1, 20 minutes in Zone 2 and 30 minutes in Zone 3, the zone-duration report must show exactly those durations and a total of 60 minutes.

The test must define interval-boundary behavior, including which zone receives a value exactly on a shared boundary.

**AT-035 — VO₂ max history**

Given measurements of 42, 43 and 44 on three different dates, the application must preserve all three measurements and display the correct chronological trend.

It must not overwrite historical measurements with the latest value.

**AT-036 — Epley estimated 1RM**

Given a valid set of 50 kg for 10 repetitions, the estimated 1RM must equal:

`50 × (1 + 10/30) = 66.67 kg`

The displayed result must be labeled as estimated.

**AT-037 — Invalid estimated 1RM**

Given a set with missing weight, zero repetitions or a repetition count outside the configured estimation range, the application must not generate an estimated 1RM.

**AT-038 — Muscle-group volume**

Given:
- 3 bench press sets.
- 3 incline press sets.
- 3 triceps isolation sets.

With a configured mapping of 1.0 chest contribution per pressing set and 1.0 triceps contribution per isolation set, chest volume must equal 6 effective sets.

Triceps volume must reflect the configured secondary contribution from pressing plus the isolation sets.

The result must be reproducible from the configured mapping.

**AT-039 — Missing muscle mapping**

Given an exercise that has no muscle-group mapping, the system must flag it as unmapped.

It must not silently assign an arbitrary muscle group.

**AT-040 — Duplicate activity aggregation**

Given two records with the same source and source activity ID, weekly distance and duration must count the activity once.

**AT-041 — Training-load calculations**

Given a fixed fixture of daily training-load values and a documented acute/chronic calculation method, the calculated values must match hand-calculated expected results.

The calculation method, window lengths and handling of missing days must be documented and tested.

Do not silently switch calculation methods between reports.

**AT-042 — Recovery baseline**

Given a configured HRV baseline and a sequence of daily HRV measurements, the application must calculate deviations using the documented baseline method.

Missing days must not be treated as zero HRV.

**AT-043 — Comparable performance**

Given two rides with different distances, durations and heart rates, the analytics engine must not claim a definitive fitness improvement solely because the second ride has a higher average speed.

The comparison must either use a defined comparable-workout method or explicitly state its limitations.

## 18.5 AI coach acceptance tests

AI tests must use mocked model responses for deterministic application-level behavior. Live-model quality evaluations should be a separate evaluation suite.

**AT-050 — Evidence-backed recommendations**

Given structured analytics showing increased training load and reduced recovery indicators, the AI response must cite the relevant available metrics in its reasoning.

It must not invent a workout, HRV value or training-load value.

**AT-051 — Missing data disclosure**

Given no recent HRV measurements, the AI must state that HRV-based recovery assessment is unavailable.

It must not assume that recovery is normal.

**AT-052 — Goal prioritization**

Given configurable goals that prioritize hypertrophy over VO₂ max improvement, the generated training proposal must reflect that priority when choosing between competing training demands.

The system must not hardcode this priority into its analytics engine.

**AT-053 — Training schedule constraints**

Given Tuesday as a configured gym rest day, the weekly planner must not schedule a gym workout on Tuesday unless the user explicitly overrides that constraint.

**AT-054 — Club ride flexibility**

Given a flexible weekend club ride, the planner must treat the ride as a movable or adjustable session rather than assuming a fixed Saturday or Sunday workout.

**AT-055 — Recommendation explanation**

Every training recommendation must include:
- Proposed action.
- Supporting data.
- Reasoning.
- Confidence or uncertainty.
- Relevant constraints.
- Whether user approval is required.

**AT-056 — Pain or injury warning**

Given user-reported pain or injury, the coach must not recommend training through it.

It should avoid making a diagnosis and should advise appropriate professional evaluation where warranted.

**AT-057 — No fabricated metrics**

Given a context with missing cycling power, the AI must not invent power, FTP or power-zone values.

**AT-058 — Contradictory data**

Given conflicting recovery indicators, the coach must communicate the disagreement and avoid presenting an unjustifiably certain readiness assessment.

**AT-059 — Recommendation persistence**

When a recommendation is generated, its content, timestamp, supporting metric references and status must be stored.

**AT-060 — Approval before changes**

When the AI proposes changing an existing workout, the original planned workout must remain unchanged until the user approves the modification.

## 18.6 Workout planner acceptance tests

**AT-070 — Create workout**

Given a valid strength workout containing five exercises, the application must create a planned workout with all exercises, sets, repetitions and target parameters preserved.

**AT-071 — Edit workout**

Given an existing planned workout, changing one exercise's target repetitions must update that field without altering unrelated exercises or dates.

**AT-072 — Delete workout**

Given a planned workout, deleting it must require the configured confirmation process.

Deletion must not remove the historical completed workout or source activity.

**AT-073 — Reschedule workout**

Given a planned workout on Wednesday, moving it to Thursday must update the local calendar and retain the workout's identity and history.

**AT-074 — Planned versus completed**

Given one planned workout and one completed workout, the application must show their status separately.

A planned session must not automatically count as completed.

**AT-075 — Progression logic**

Given a configurable progression rule and a workout history that satisfies its conditions, the planner must propose the expected progression.

It must not increase the target load when the required performance or recovery conditions have not been met.

**AT-076 — Constraint preservation**

A generated weekly plan must preserve all mandatory user constraints unless the user explicitly changes them.

**AT-077 — No accidental duplicates**

Repeatedly submitting the same create request with the same idempotency key must not create multiple planned workouts.

## 18.7 Intervals.icu acceptance tests

These tests must use mocked API responses until the integration is configured.

**AT-080 — Authentication**

Given a valid API credential supplied through the configured secret mechanism, the connector must authenticate successfully.

Given an invalid credential, it must return a clear authentication error without exposing the secret in logs.

**AT-081 — Create external workout**

Given a valid local planned workout, the connector must create the corresponding external event and persist the returned external identifier.

**AT-082 — Update external workout**

Given an existing synchronized workout, editing its date or structure must update the corresponding external event rather than create a second event.

**AT-083 — Delete external workout**

Given a synchronized workout, deleting it externally must require explicit user approval.

The local record must preserve the synchronization history.

**AT-084 — Idempotent synchronization**

Running synchronization twice without local changes must not create duplicate external events.

**AT-085 — API failure recovery**

Given a network timeout during synchronization, the local planned workout must remain intact and the synchronization state must indicate failure or pending retry.

**AT-086 — Credential protection**

No API key may appear in:
- Source code.
- Git history.
- Application logs.
- Error responses.
- Exported reports.

**AT-087 — Optional integration**

When Intervals.icu is not configured, the application must still start and all non-integration features must remain usable.

## 18.8 Dashboard acceptance tests

**AT-090 — Overview consistency**

The dashboard's weekly distance, duration and workout counts must match the corresponding analytics API results for the same date range and timezone.

**AT-091 — Empty-state handling**

With an empty database, the dashboard must display an informative empty state rather than errors, fabricated charts or misleading zeros.

**AT-092 — Historical filters**

Selecting a 7-day, 28-day or 90-day period must update all applicable charts and summary metrics consistently.

**AT-093 — Missing metrics**

If VO₂ max or HRV is unavailable, the dashboard must display unavailable status rather than a fabricated value.

**AT-094 — Calendar status**

Planned, completed, missed and rescheduled workouts must have distinct statuses.

A cancelled workout must not appear as a missed workout.

## 18.9 Security and reliability acceptance tests

**AT-100 — Secret scanning**

The repository must contain no real credentials or API keys. Include a secret-scanning check in the development workflow.

**AT-101 — Input validation**

Malformed API requests and invalid import files must return structured validation errors without crashing the application.

**AT-102 — Database integrity**

Foreign-key constraints and relationship integrity must prevent orphaned workout sets or activities.

**AT-103 — Backup and restore**

Given a database backup, restoring it into a clean environment must reproduce the same record counts and analytics results.

**AT-104 — Logging**

Import and synchronization failures must be logged with enough diagnostic context to troubleshoot them, but without leaking credentials or sensitive secrets.

**AT-105 — Application startup**

The application must start successfully with an empty database and no optional external integrations configured.

## 18.10 End-to-end acceptance scenarios

These scenarios verify that separate components work together.

### E2E-001 — Historical import to dashboard

1. Import a fixture containing 10 cycling activities.
2. Import a fixture containing 5 running activities.
3. Import 8 Hevy strength workouts.
4. Run normalization and deduplication.
5. Open the dashboard.

Expected:
- All 23 unique records are represented in the appropriate sections.
- Weekly summaries match hand-calculated totals.
- Source provenance is retained.
- No duplicate activities appear.

### E2E-002 — Strength progression analysis

1. Import three successive bench press sessions.
2. Each session contains valid weights and repetitions.
3. Run strength analytics.
4. Open the exercise progression view.

Expected:
- All three sessions appear chronologically.
- Estimated 1RM is calculated using the configured formula.
- Personal records are identified correctly.
- The AI can explain the trend using the actual data.

### E2E-003 — Recovery-aware daily recommendation

1. Load a fixture with recent high training load.
2. Load a fixture with HRV below the user's configured baseline.
3. Load a planned demanding lower-body workout.
4. Request a daily recommendation.

Expected:
- The recommendation references the available recovery and training-load data.
- It identifies the planned lower-body workout.
- It proposes an appropriate adjustment or rest option.
- It does not modify the calendar automatically.

### E2E-004 — Weekly plan creation

1. Configure the user's weekly availability.
2. Set Tuesday as gym rest day.
3. Add a flexible weekend club ride.
4. Configure training priorities.
5. Generate a weekly plan.

Expected:
- Tuesday remains free of gym sessions.
- The club ride is represented as flexible.
- Strength and endurance sessions are distributed with recovery considered.
- Each session contains actionable workout details.
- The user can review and approve the plan.

### E2E-005 — Workout synchronization

1. Create a local planned workout.
2. Synchronize it using a mocked Intervals.icu API.
3. Change the workout date.
4. Synchronize again.
5. Repeat synchronization without additional changes.

Expected:
- One external workout is created.
- The existing external workout is updated.
- The third synchronization creates no duplicate.
- The local and external identifiers remain correctly associated.

### E2E-006 — Full data recovery

1. Import historical fixtures.
2. Generate analytics.
3. Back up the database.
4. Restore into a clean database.
5. Recalculate analytics.

Expected:
- Record counts match.
- Relationships remain valid.
- Historical metrics are preserved.
- Analytics match the pre-backup results.

---

# 19. Release gates and completion criteria

A phase cannot be marked complete until its corresponding acceptance tests pass.

| Release gate | Required acceptance tests |
|---|---|
| Foundation | AT-001 to AT-004, AT-100 to AT-105 |
| Data ingestion | AT-010 to AT-025 |
| Analytics | AT-030 to AT-043 |
| AI coach | AT-050 to AT-060 |
| Workout planner | AT-070 to AT-077 |
| Intervals.icu | AT-080 to AT-087 |
| Dashboard | AT-090 to AT-094 |
| Final release | E2E-001 to E2E-006 |

## Final release requirements

Before declaring version 1.0 complete:

1. All mandatory automated tests pass.
2. All critical analytics have deterministic test fixtures.
3. Historical import and re-import are idempotent.
4. No real credentials are committed.
5. The application works without optional integrations.
6. Backup and restore are verified.
7. The README documents setup, configuration and testing.
8. Known limitations are documented.
9. The dashboard does not display fabricated data.
10. AI recommendations require approval before modifying existing plans.

**A feature is complete only when its implementation, automated tests, documentation and acceptance criteria are all satisfied.**

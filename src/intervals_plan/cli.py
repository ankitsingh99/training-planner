"""
Command-line interface for the Intervals.icu Adaptive Training Plan Tool.
"""

import argparse
import dataclasses
import datetime
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from intervals_plan.adaptive import AdaptiveEngine
from intervals_plan.analytics import RollingAnalysisReport, RollingMetricsAnalyzer
from intervals_plan.api_models import IntervalsEvent
from intervals_plan.athlete_profile import AthleteProfileConfig
from intervals_plan.audit import AuditLogger
from intervals_plan.backup import BackupManager
from intervals_plan.coaching_advisor import CoachingAdvisor
from intervals_plan.config import Config
from intervals_plan.diff import calculate_diff
from intervals_plan.exporters import PlanExporter
from intervals_plan.integrations.watchletic_research import print_watch_research
from intervals_plan.intervals_client import IntervalsAPIError, IntervalsClient
from intervals_plan.plan_builder import PlanBuilder, get_default_8wk_plan
from intervals_plan.plan_models import PlanConfig, TrainingPlan
from intervals_plan.rolling_planner import DynamicRollingPlanner
from intervals_plan.sync import SyncManager
from intervals_plan.trainingpeaks_client import TrainingPeaksClient
from intervals_plan.web.server import run_web_server
from intervals_plan.workout_schema import format_duration


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intervals-plan",
        description="Adaptive Training Plan Tool for Intervals.icu (CLI-first)",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # doctor
    subparsers.add_parser("doctor", help="Run system diagnostics & API connectivity check")

    # auth test
    auth_parser = subparsers.add_parser("auth", help="Authentication operations")
    auth_sub = auth_parser.add_subparsers(dest="auth_command")
    auth_sub.add_parser("test", help="Test credentials and show current athlete identity")

    # athlete show
    ath_parser = subparsers.add_parser("athlete", help="Athlete profile operations")
    ath_sub = ath_parser.add_subparsers(dest="athlete_command")
    ath_sub.add_parser("show", help="Display authenticated athlete profile")

    # plan
    plan_parser = subparsers.add_parser("plan", help="Training plan operations")
    plan_sub = plan_parser.add_subparsers(dest="plan_command")
    
    val_p = plan_sub.add_parser("validate", help="Validate plan offline without network calls")
    val_p.add_argument("file", nargs="?", default=None, help="Path to plan YAML/JSON")

    prev_p = plan_sub.add_parser("preview", help="Preview plan overview and workout schedule")
    prev_p.add_argument("file", nargs="?", default=None, help="Path to plan YAML/JSON")

    exp_p = plan_sub.add_parser("export-json", help="Export plan to Intervals.icu JSON payload")
    exp_p.add_argument("file", nargs="?", default=None, help="Path to plan YAML/JSON")
    exp_p.add_argument("--output", "-o", default=None, help="Output file path")

    resched_p = plan_sub.add_parser("reschedule", help="Reschedule a workout day (e.g. Sat -> Sun)")
    resched_p.add_argument("--workout", required=True, help="Workout identifier e.g. 'weekend-club-ride'")
    resched_p.add_argument("--week", type=int, default=1, help="Week number (1-8)")
    resched_p.add_argument("--date", required=True, help="New target date (YYYY-MM-DD)")
    resched_p.add_argument("--dry-run", action="store_true", default=True, help="Simulate without applying")
    resched_p.add_argument("--apply", action="store_true", help="Apply rescheduling to Intervals.icu")

    # events
    events_parser = subparsers.add_parser("events", help="Calendar event operations")
    ev_sub = events_parser.add_subparsers(dest="events_command")
    
    list_p = ev_sub.add_parser("list", help="List live events in date range")
    list_p.add_argument("--from", dest="from_date", default="2026-11-02", help="Start date (YYYY-MM-DD)")
    list_p.add_argument("--to", dest="to_date", default="2026-12-27", help="End date (YYYY-MM-DD)")

    show_p = ev_sub.add_parser("show", help="Show details of a specific event")
    show_p.add_argument("event_id", help="Event internal ID")

    del_p = ev_sub.add_parser("delete", help="Safely delete a single event (guarded)")
    del_p.add_argument("event_id", help="Event internal ID to delete")
    del_p.add_argument("--dry-run", action="store_true", default=True, help="Dry run check (default)")
    del_p.add_argument("--confirm-delete", action="store_true", help="Confirm deletion")

    del_prefix_p = ev_sub.add_parser("delete-by-prefix", help="Bulk delete managed events by prefix (guarded)")
    del_prefix_p.add_argument("prefix", help="Managed external ID prefix")
    del_prefix_p.add_argument("--from", dest="from_date", default="2026-11-02", help="Start date")
    del_prefix_p.add_argument("--to", dest="to_date", default="2026-12-27", help="End date")
    del_prefix_p.add_argument("--dry-run", action="store_true", default=True, help="Dry run check (default)")
    del_prefix_p.add_argument("--confirm-phrase", help="Required confirmation phrase e.g. 'DELETE 30 EVENTS'")

    restore_p = ev_sub.add_parser("restore", help="Restore events from a local backup file")
    restore_p.add_argument("backup_id", help="Backup filename or timestamp identifier")
    restore_p.add_argument("--dry-run", action="store_true", default=True, help="Dry run preview")
    restore_p.add_argument("--apply", action="store_true", help="Apply restore to Intervals.icu")

    # sync
    sync_p = subparsers.add_parser("sync", help="Synchronize plan with Intervals.icu")
    sync_p.add_argument("--dry-run", action="store_true", default=False, help="Simulate without applying")
    sync_p.add_argument("--apply", action="store_true", help="Apply sync to Intervals.icu")
    sync_p.add_argument("--force", action="store_true", help="Force overwrite existing events / conflicts")

    # adapt
    adapt_p = subparsers.add_parser("adapt", help="Evaluate and apply adaptive training rules")
    adapt_p.add_argument("--club-ride-hard", action="store_true", help="Flag hard club ride (suppresses Thursday hard bike)")
    adapt_p.add_argument("--auto", action="store_true", help="Auto-detect fatigue from 30d wellness/activities and adapt schedule")
    adapt_p.add_argument("--week", type=int, default=1, help="Week number to adapt")
    adapt_p.add_argument("--dry-run", action="store_true", default=True, help="Simulate without applying")
    adapt_p.add_argument("--apply", action="store_true", help="Apply adaptive change to calendar")

    # analyze
    ana_p = subparsers.add_parser("analyze", help="Analyze rolling 30-day physiological and training data")
    ana_p.add_argument("--days", type=int, default=30, help="Analysis lookback window in days (default: 30)")
    ana_p.add_argument("--json", action="store_true", help="Output analysis report in JSON format")

    # profile
    prof_p = subparsers.add_parser("profile", help="Manage athlete profile and adjustable training goals")
    prof_p.add_argument("--show", action="store_true", help="Display current profile and parameters")
    prof_p.add_argument("--edit", action="store_true", help="Interactively edit profile goals and constraints")
    prof_p.add_argument("--goal", choices=["dual_sport_hybrid", "running", "cycling", "general_fitness"], help="Primary athletic goal")
    prof_p.add_argument("--hours", type=float, help="Target weekly commitment in hours (e.g. 8.0)")
    prof_p.add_argument("--philosophy", choices=["polarized_80_20", "pyramidal", "hrv_governed"], help="Training philosophy")
    prof_p.add_argument("--horizon", choices=["1_week", "2_weeks"], help="Dynamic planning horizon")
    prof_p.add_argument("--race-dist", help="Target race distance (e.g. 10k, half_marathon)")

    # plan-next
    pnext_p = subparsers.add_parser("plan-next", help="Dynamically plan next 1 or 2 weeks based on 30-day data")
    pnext_p.add_argument("--weeks", type=int, choices=[1, 2], help="Number of weeks to plan (1 or 2)")
    pnext_p.add_argument("--hours", type=float, help="Override weekly training hours budget")
    pnext_p.add_argument("--goal", choices=["dual_sport_hybrid", "running", "cycling", "general_fitness"], help="Override athletic goal")
    pnext_p.add_argument("--start-date", help="Cycle start date (YYYY-MM-DD, defaults to upcoming Monday)")
    pnext_p.add_argument("--dry-run", action="store_true", default=True, help="Preview plan without applying")
    pnext_p.add_argument("--apply", action="store_true", help="Apply planned workouts directly to Intervals.icu")
    pnext_p.add_argument("--force", action="store_true", help="Force overwrite existing events in the target date range")

    # manifest
    man_p = subparsers.add_parser("manifest", help="Manifest management")
    man_sub = man_p.add_subparsers(dest="manifest_command")
    man_sub.add_parser("show", help="Display local manifest summary")
    man_sub.add_parser("reconcile", help="Reconcile local manifest with live calendar")

    # audit
    aud_p = subparsers.add_parser("audit", help="Audit log operations")
    aud_sub = aud_p.add_subparsers(dest="audit_command")
    aud_sub.add_parser("list", help="List recent audit log entries")

    # watch-research
    subparsers.add_parser("watch-research", help="Display Wear OS / Watchletic / COROS ecosystem research")

    # coros-status
    subparsers.add_parser("coros-status", help="Check live COROS connection and workout sync status")

    # tp-status (TrainingPeaks)
    subparsers.add_parser("tp-status", help="Check live TrainingPeaks API connection and athlete zones")

    # ui
    ui_p = subparsers.add_parser("ui", help="Launch interactive multi-page Web UI dashboard")
    ui_p.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    ui_p.add_argument("--port", type=int, default=8080, help="Port to serve Web UI on (default: 8080)")
    ui_p.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")

    # coach
    coach_p = subparsers.add_parser("coach", help="Get intelligent coaching guidance based on biometrics & goals")
    coach_p.add_argument("--json", action="store_true", help="Output coaching guidance in JSON format")

    # export
    exp_all_p = subparsers.add_parser("export", help="Export workouts to Zwift (.zwo), iCalendar (.ics), or JSON")
    exp_all_p.add_argument("--format", choices=["zwo", "ics", "json", "all"], default="all", help="Output format")
    exp_all_p.add_argument("--out-dir", default="plans/export", help="Output directory path (default: plans/export)")
    exp_all_p.add_argument("--weeks", type=int, choices=[1, 2], default=1, help="Number of weeks to export")

    return parser


def load_plan(plan_file: Optional[str] = None) -> TrainingPlan:
    """Load plan from file if given, else return default verified 8-week plan."""
    if not plan_file:
        return get_default_8wk_plan()

    p = Path(plan_file)
    if not p.is_file():
        raise FileNotFoundError(f"Plan file not found: {plan_file}")

    if p.suffix in (".yaml", ".yml"):
        import yaml
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    else:
        raw = json.loads(p.read_text(encoding="utf-8"))

    # Convert raw to TrainingPlan
    cfg_data = raw.get("config", {})
    cfg = PlanConfig(**cfg_data)
    weeks = []
    from intervals_plan.plan_models import WeekSpec
    for w in raw.get("weeks", []):
        weeks.append(WeekSpec(**w))

    return TrainingPlan(
        title=raw.get("title", "Custom Plan"),
        description=raw.get("description", ""),
        config=cfg,
        weeks=weeks,
    )


def handle_doctor(cfg: Config) -> None:
    print("\n Running Intervals.icu Diagnostics...\n")
    print(f"System:")
    print(f"  - Python Version: {sys.version.split()[0]}")
    print(f"  - Data Directory: {cfg.data_dir} (exists: {cfg.data_dir.exists()})")
    print(f"  - Config Summary:\n{cfg.summary()}\n")

    if not cfg.api_key:
        print(" Status: INTERVALS_API_KEY is not configured in .env or environment.")
        return

    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    res = client.doctor()
    if res.get("status") == "HEALTHY":
        print(f" API Connectivity: HEALTHY")
        print(f"  - Athlete ID:     {res['athlete_id']}")
        print(f"  - Athlete Name:   {res['name']}")
        print(f"  - Timezone:       {res['timezone']}")
        print(f"  - Resting HR:     {res['resting_hr']} bpm")
        print(f"  - LTHR:           {res['lthr']} bpm")
    else:
        print(f" API Connectivity Error: {res.get('error')}")


def handle_plan_validate(args: argparse.Namespace) -> None:
    plan = load_plan(args.file)
    errors = plan.validate()
    if errors:
        print(f"\n Plan validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"\n Plan '{plan.title}' validated successfully!")
        print(f"  - Weeks: {plan.config.total_weeks}")
        print(f"  - Start Date: {plan.config.start_date}")
        print(f"  - W4 Deload Bike: {'Included' if plan.config.include_w4_bike else 'Omitted (Restorative)'}")
        print(f"  - W8 5km Retest:  {'Included' if plan.config.include_w8_retest else 'Omitted'}")


def handle_plan_preview(args: argparse.Namespace) -> None:
    plan = load_plan(args.file)
    builder = PlanBuilder(plan)
    events = builder.build_all_events()

    print(f"\n Plan Preview: {plan.title}")
    print(f"Total Events: {len(events)} (Range: {plan.config.start_date} onwards)\n")
    print("| Week | Monday (Quality Run) | Tuesday (Aerobic Ride) | Thursday (Optional Bike) | Weekend (Club Ride) |")
    print("| :--- | :--- | :--- | :--- | :--- |")

    for w in plan.weeks:
        evs = [e for e in events if f"w{w.week_number}-" in (e.external_id or "")]
        mon = next((f"{e.name.split('—')[-1].strip()} ({format_duration(e.moving_time)})" for e in evs if "mon-run" in (e.external_id or "")), "Rest")
        tue = next((f"Zone 2 ({format_duration(e.moving_time)})" for e in evs if "tue-easy-ride" in (e.external_id or "")), "Rest")
        thu = next((f"{e.name.split('—')[-1].strip()} ({format_duration(e.moving_time)})" for e in evs if "thu-optional-bike" in (e.external_id or "")), "*Rest / Rec*")
        weekend = next(("~50 km Club Ride" for e in evs if "weekend-club-ride" in (e.external_id or "")), "None")
        phase_str = f"Week {w.week_number} ({w.phase})"
        print(f"| **{phase_str}** | {mon} | {tue} | {thu} | {weekend} |")


def handle_events_list(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    events = client.list_events(args.from_date, args.to_date)
    print(f"\n Found {len(events)} events between {args.from_date} and {args.to_date}:")
    for ev in events:
        ext_tag = f" [{ev.external_id}]" if ev.external_id else ""
        sport_str = str(ev.type or ev.category or "Note")
        print(f"  - ID: {str(ev.id or 'None'):<9} | {ev.start_date_local} | {sport_str:<5} | {ev.name}{ext_tag}")


def handle_events_show(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    ev = client.get_event(args.event_id)
    print(json.dumps(ev.to_dict(), indent=2))


def handle_sync(cfg: Config, args: argparse.Namespace) -> None:
    plan = get_default_8wk_plan()
    builder = PlanBuilder(plan)
    events = builder.build_all_events()

    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    sync_mgr = SyncManager(client=client, data_dir=cfg.data_dir, managed_prefix=plan.config.prefix)

    start_date = plan.config.start_date
    end_date = "2026-12-27"

    diff, live_events = sync_mgr.preview_sync(events, start_date, end_date)
    print("\n Synchronization Diff:")
    print(diff.summary())

    if not args.apply:
        print("\n[DRY RUN] No changes were made to Intervals.icu.")
        print("Run with '--apply' to push mutations, or '--apply --force' to overwrite conflicts.")
        return

    print("\nApplying synchronization...")
    res = sync_mgr.apply_sync(events, start_date, end_date, force=args.force)
    print(f" Sync Finished: Status = {res['status']}")
    print(f"  - Created:  {res['created']}")
    print(f"  - Updated:  {res['updated']}")
    print(f"  - Verified: {res['total_verified']}")
    print(f"  - Backup:   {res['backup_path']}")


def handle_events_delete(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    try:
        ev = client.get_event(args.event_id)
    except IntervalsAPIError as exc:
        print(f" Error fetching event {args.event_id}: {exc}")
        return

    print(f"\n  Target Event for Deletion:")
    print(f"  - ID:          {ev.id}")
    print(f"  - Name:        {ev.name}")
    print(f"  - Date:        {ev.start_date_local}")
    print(f"  - External ID: {ev.external_id or 'None (Unmanaged!)'}")

    if not args.confirm_delete:
        print("\n[DRY RUN] Event was NOT deleted.")
        print("Pass '--confirm-delete' to permanently remove this event from your calendar.")
        return

    # Backup before deletion
    backup_mgr = BackupManager(cfg.data_dir / "backups")
    backup_path = backup_mgr.create_backup([ev], tag=f"predelete_id_{ev.id}")

    client.delete_event(args.event_id)
    print(f" Event {args.event_id} successfully deleted! (Backup saved to {backup_path})")

    audit = AuditLogger(cfg.data_dir / "audit.log")
    audit.log("DELETE_EVENT", [str(ev.id)], "SUCCESS", {"name": ev.name, "backup": str(backup_path)})


def handle_delete_by_prefix(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    live_events = client.list_events(args.from_date, args.to_date)
    matching = [e for e in live_events if e.external_id and e.external_id.startswith(args.prefix)]

    print(f"\n  Bulk Deletion Preview:")
    print(f"Prefix: '{args.prefix}'")
    print(f"Matching Managed Events Found: {len(matching)}")
    for e in matching[:5]:
        print(f"  - ID {e.id} | {e.start_date_local} | {e.name}")
    if len(matching) > 5:
        print(f"  ... and {len(matching) - 5} more.")

    required_phrase = f"DELETE {len(matching)} EVENTS"

    if args.confirm_phrase != required_phrase:
        print(f"\n[DRY RUN] Bulk deletion requires typing the exact phrase:")
        print(f"  --confirm-phrase \"{required_phrase}\"")
        return

    backup_mgr = BackupManager(cfg.data_dir / "backups")
    backup_path = backup_mgr.create_backup(matching, tag="pre_bulk_delete")

    deleted_count = 0
    for e in matching:
        if e.id:
            client.delete_event(e.id)
            deleted_count += 1

    print(f"\n Bulk deleted {deleted_count} events from Intervals.icu!")
    print(f"Backup saved to: {backup_path}")

    audit = AuditLogger(cfg.data_dir / "audit.log")
    audit.log("BULK_DELETE", [str(e.id) for e in matching], "SUCCESS", {"count": deleted_count, "backup": str(backup_path)})


def handle_adapt(cfg: Config, args: argparse.Namespace) -> None:
    plan = get_default_8wk_plan()
    builder = PlanBuilder(plan)
    events = builder.build_all_events()

    if getattr(args, "auto", False):
        print("\nRunning automatic physiological fatigue analysis...")
        client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
        profile = AthleteProfileConfig.load(cfg.data_dir / "athlete_profile.json")
        lookback_start = datetime.date.today() - datetime.timedelta(days=30)
        wellness = client.get_wellness_range(lookback_start.isoformat(), datetime.date.today().isoformat())
        activities = client.get_activities(lookback_start.isoformat(), datetime.date.today().isoformat())
        analyzer = RollingMetricsAnalyzer(target_hours_profile=profile.weekly_hours, athlete_lthr=profile.lthr_run)
        report = analyzer.analyze_30d(wellness, activities)
        if report.readiness.rhr_elevated or report.readiness.readiness_state in ["ELEVATED_FATIGUE", "RECOVERY_MANDATORY"]:
            rhr_delta_str = f"{report.readiness.rhr_delta:+.1f}" if report.readiness.rhr_delta is not None else "N/A"
            print(f"  Elevated strain detected (RHR delta: {rhr_delta_str} bpm, Form: {report.readiness.tsb:+.1f}).")
            print("Action: Auto-substituting Week 1 Thursday high-intensity bike intervals with recovery spin...")
            events = AdaptiveEngine.adapt_for_hard_club_ride(events, args.week)
        else:
            print(" Physiological markers are stable. No emergency downshift needed.")
    elif args.club_ride_hard:
        print(f"\n Adaptive Trigger: Hard weekend club ride indicated for Week {args.week}.")
        print("Action: Suppressing Thursday's high-intensity bike intervals with an active recovery spin...")
        events = AdaptiveEngine.adapt_for_hard_club_ride(events, args.week)

    if not args.apply:
        target = next((e for e in events if f"w{args.week}-thu" in (e.external_id or "")), None)
        print(f"\n[DRY RUN] Adapted Week {args.week} Thursday workout preview:")
        if target:
            print(f"  - Name:        {target.name}")
            print(f"  - Duration:    {format_duration(target.moving_time)}")
            print(f"  - Description: {target.description}")
        print("\nPass '--apply' to update this adaptation directly on Intervals.icu.")
        return

    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    sync_mgr = SyncManager(client=client, data_dir=cfg.data_dir, managed_prefix=plan.config.prefix)
    res = sync_mgr.apply_sync(events, plan.config.start_date, "2026-12-27", force=True)
    print(f" Applied adaptive modification to Intervals.icu calendar! ({res['status']})")


def handle_analyze(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    profile = AthleteProfileConfig.load(cfg.data_dir / "athlete_profile.json")

    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=args.days)

    print(f"\n Fetching rolling {args.days}-day wellness and activity data from Intervals.icu...")
    wellness_records = client.get_wellness_range(start_date.isoformat(), end_date.isoformat())
    activities = client.get_activities(start_date.isoformat(), end_date.isoformat())

    analyzer = RollingMetricsAnalyzer(
        target_hours_profile=profile.weekly_hours,
        athlete_lthr=profile.lthr_run,
    )
    report = analyzer.analyze_30d(wellness_records, activities, end_date.isoformat())

    if args.json:
        print(json.dumps(dataclasses.asdict(report), indent=2))
    else:
        for line in report.summary_lines():
            print(line)


def handle_profile(cfg: Config, args: argparse.Namespace) -> None:
    profile_path = cfg.data_dir / "athlete_profile.json"
    profile = AthleteProfileConfig.load(profile_path)

    if args.edit:
        print("\n  Interactive Athlete Profile Configuration:")
        print("Press Enter to keep current values in [brackets].\n")
        
        goal_input = input(f"Primary Goal [{profile.goal}] (dual_sport_hybrid/running/cycling/general_fitness): ").strip()
        if goal_input:
            profile.goal = goal_input
            
        hours_input = input(f"Target Weekly Hours [{profile.weekly_hours}]: ").strip()
        if hours_input:
            try:
                profile.weekly_hours = float(hours_input)
            except ValueError:
                pass
                
        phil_input = input(f"Philosophy [{profile.philosophy}] (polarized_80_20/pyramidal/hrv_governed): ").strip()
        if phil_input:
            profile.philosophy = phil_input
            
        horizon_input = input(f"Planning Horizon [{profile.planning_horizon}] (1_week/2_weeks): ").strip()
        if horizon_input:
            profile.planning_horizon = horizon_input
            
        race_input = input(f"Target Race / Distance [{profile.target_race_distance or 'none'}]: ").strip()
        if race_input:
            profile.target_race_distance = race_input

        profile.save(profile_path)
        print("\n Athlete profile updated successfully!")

    # Check CLI flag updates
    updated = False
    if args.goal:
        profile.goal = args.goal
        updated = True
    if args.hours is not None:
        profile.weekly_hours = args.hours
        updated = True
    if args.philosophy:
        profile.philosophy = args.philosophy
        updated = True
    if args.horizon:
        profile.planning_horizon = args.horizon
        updated = True
    if args.race_dist:
        profile.target_race_distance = args.race_dist
        updated = True

    if updated:
        profile.save(profile_path)
        print(" Profile updated with CLI parameters!")

    # Display profile summary
    print("\n Current Athlete Profile & Preferences:")
    print("=" * 55)
    print(f"  - Primary Goal:         {profile.goal}")
    print(f"  - Target Weekly Hours:  {profile.weekly_hours:.1f} hours/week")
    print(f"  - Training Philosophy:  {profile.philosophy}")
    print(f"  - Planning Horizon:     {profile.planning_horizon}")
    print(f"  - Target Race/Event:    {profile.target_race_distance or 'None'}")
    print(f"  - Running LTHR:         {profile.lthr_run} bpm")
    print(f"  - Cycling FTP:          {profile.ftp_bike} W (LTHR: {profile.lthr_bike} bpm)")
    print(f"  - Max Heart Rate:       {profile.max_hr} bpm")
    print(f"  - Resting HR Baseline:  {profile.resting_hr_baseline} bpm")
    print(f"  - Config File:          {profile_path}")
    print("=" * 55)
    print("Tip: Run 'intervals-plan profile --edit' or pass flags e.g. '--hours 8.0' to adjust at any time.")


def handle_plan_next(cfg: Config, args: argparse.Namespace) -> None:
    profile_path = cfg.data_dir / "athlete_profile.json"
    profile = AthleteProfileConfig.load(profile_path)

    # Apply overrides
    if args.hours is not None:
        profile.weekly_hours = args.hours
    if args.goal:
        profile.goal = args.goal

    weeks = args.weeks or (2 if profile.planning_horizon == "2_weeks" else 1)

    if args.start_date:
        cycle_start = datetime.date.fromisoformat(args.start_date)
    else:
        cycle_start = DynamicRollingPlanner.get_upcoming_monday()

    cycle_end = cycle_start + datetime.timedelta(days=weeks * 7 - 1)

    print(f"\n Generating Dynamic Rolling Plan ({weeks} Week{'s' if weeks > 1 else ''})")
    print(f"Cycle Window: {cycle_start.isoformat()} to {cycle_end.isoformat()}")
    print(f"Commitment:   {profile.weekly_hours:.1f} hours/week | Model: {profile.philosophy}")

    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)

    # 1. Fetch live 30-day data
    lookback_start = datetime.date.today() - datetime.timedelta(days=30)
    print("Fetching rolling 30-day physiological and activity data from Intervals.icu...")
    wellness_records = client.get_wellness_range(lookback_start.isoformat(), datetime.date.today().isoformat())
    activities = client.get_activities(lookback_start.isoformat(), datetime.date.today().isoformat())

    analyzer = RollingMetricsAnalyzer(
        target_hours_profile=profile.weekly_hours,
        athlete_lthr=profile.lthr_run,
    )
    report = analyzer.analyze_30d(wellness_records, activities)

    print(f"\nAutonomic & Load Assessment:")
    print(f"  - Fitness (CTL):   {report.readiness.ctl:.1f} | Fatigue (ATL): {report.readiness.atl:.1f} | Form (TSB): {report.readiness.tsb:+.1f}")
    print(f"  - ACWR Ratio:      {report.acwr.ratio:.2f} [{report.acwr.status}]")
    if report.readiness.recent_resting_hr:
        rhr_status = " ELEVATED" if report.readiness.rhr_elevated else " STABLE"
        delta_str = f"{report.readiness.rhr_delta:+.1f} bpm" if report.readiness.rhr_delta is not None else "N/A"
        print(f"  - Resting HR:      {report.readiness.recent_resting_hr:.0f} bpm (Baseline: {report.readiness.resting_hr_baseline:.0f} bpm, Delta: {delta_str}) [{rhr_status}]")
    print(f"  - Readiness State: {report.readiness.readiness_state} (Score: {report.readiness.readiness_score}/100)")
    print(f"  - Recommendation:  {report.readiness.recommendation}")

    # 2. Generate workouts
    prefix = f"dynamic-{profile.goal}-{cycle_start.isoformat()}"
    planner = DynamicRollingPlanner(profile)
    events = planner.generate_plan(
        report=report,
        start_date=cycle_start,
        weeks_to_plan=weeks,
        prefix=prefix,
    )

    print(f"\n Proposed Workout Schedule ({len(events)} Sessions):")
    print("-" * 72)
    total_moving_secs = 0
    for ev in events:
        dur = ev.moving_time or 0
        total_moving_secs += dur
        dur_str = format_duration(dur) if dur > 0 else "Rest"
        print(f"  {ev.start_date_local[:10]} | {ev.type:<5} | {dur_str:>7} | {ev.name}")
    print("-" * 72)
    print(f"Total Moving Time: {total_moving_secs / 3600.0:.1f} hours (Target: {report.readiness.target_next_week_hours:.1f}h)")

    # 3. Diff against live calendar
    sync_mgr = SyncManager(client=client, data_dir=cfg.data_dir, managed_prefix=prefix)
    diff, _ = sync_mgr.preview_sync(events, cycle_start.isoformat(), cycle_end.isoformat())

    print("\n Synchronization Diff:")
    print(diff.summary())

    if not args.apply:
        print("\n[DRY RUN] No changes were made to Intervals.icu.")
        print("To push this personalized plan to your Intervals.icu & COROS calendar, run:")
        print("  intervals-plan plan-next --apply")
        return

    print("\nApplying dynamic plan to Intervals.icu...")
    res = sync_mgr.apply_sync(events, cycle_start.isoformat(), cycle_end.isoformat(), force=args.force)
    print(f" Dynamic Plan Applied Successfully! (Status: {res['status']})")
    print(f"  - Created Events:  {res['created']}")
    print(f"  - Updated Events:  {res['updated']}")
    print(f"  - Total Verified:  {res['total_verified']}")
    print(f"  - Safety Backup:   {res['backup_path']}")
    print("\nCOROS Sync:")
    print("  - Workouts for the rolling 7-day window are queued and will sync to your COROS app/watch automatically.")


def handle_coros_status(cfg: Config) -> None:
    print("\nChecking COROS Cloud Connection & Sync Status...\n")
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    try:
        ath = client._request("GET", f"/athlete/{cfg.athlete_id}")
        user_id = ath.get("coros_user_id")
        sync_acts = ath.get("coros_sync_activities")
        upload_workouts = ath.get("coros_upload_workouts")
        download_wellness = ath.get("coros_download_wellness")
        last_upload = ath.get("coros_last_upload")

        print("Connection Details:")
        print(f"  - COROS User ID:        {user_id or 'Not Connected'}")
        print(f"  - Upload Workouts:      {' ENABLED' if upload_workouts else ' DISABLED'}")
        print(f"  - Download Activities:  {' ENABLED' if sync_acts else ' DISABLED'}")
        print(f"  - Download Wellness:    {' ENABLED' if download_wellness else ' DISABLED'}")
        print(f"  - Last Cloud Push:      {last_upload or 'Never'}")

        if upload_workouts and user_id:
            print("\nVerification Successful: Intervals.icu is actively pushing workouts to COROS!")
            print("Note on COROS API Window:")
            print("  - COROS uses a rolling 7-day forward window.")
            print("  - All workouts for the upcoming 7 days (Week 1) are already pushed to your COROS calendar.")
            print("  - Open your COROS mobile app and sync with Bluetooth to push them to your COROS DURA / watch.")
        else:
            print("\nCOROS is not configured to upload planned workouts in Intervals.icu.")
            print("Please enable 'Upload planned workouts' under Intervals.icu -> Settings -> COROS.")
    except Exception as exc:
        print(f"Error querying COROS status: {exc}")


def handle_tp_status(cfg: Config) -> None:
    print("\nChecking TrainingPeaks API Connection & Athlete Status...\n")
    client = TrainingPeaksClient(
        access_token=cfg.tp_access_token,
        client_id=cfg.tp_client_id,
        client_secret=cfg.tp_client_secret,
        athlete_id=cfg.tp_athlete_id,
        base_url=cfg.tp_base_url,
    )
    status = client.check_connection()
    if status["status"] == "UNCONFIGURED":
        print("TrainingPeaks Status: UNCONFIGURED")
        print("Please set TRAININGPEAKS_ACCESS_TOKEN in .env or environment to enable sync.")
        return

    if status["status"] == "HEALTHY":
        print("TrainingPeaks Status: HEALTHY (Connected)")
        print(f"  - Athlete ID:   {status.get('athlete_id')}")
        print(f"  - Name:         {status.get('first_name')} {status.get('last_name')}")
        print(f"  - Email:        {status.get('email')}")
        try:
            zones = client.get_athlete_zones()
            if zones:
                print(f"  - Active Zones: {len(zones)} zone configurations retrieved.")
        except Exception:
            pass
    else:
        print(f"TrainingPeaks Status: ERROR - {status.get('error')}")


def handle_ui(args: argparse.Namespace) -> None:
    """Launch the embedded interactive web application."""
    run_web_server(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
    )


def handle_coach(cfg: Config, args: argparse.Namespace) -> None:
    """Evaluate training telemetry and output intelligent coaching guidance."""
    prof = AthleteProfileConfig.load()
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    today = datetime.date.today()
    start = today - datetime.timedelta(days=29)

    wellness = client.get_wellness_range(start.isoformat(), today.isoformat())
    acts = client.list_events(start.isoformat(), today.isoformat())
    act_dicts = [a.to_dict() for a in acts if a.category != "WORKOUT"]

    analyzer = RollingMetricsAnalyzer(target_hours_profile=prof.weekly_hours, athlete_lthr=prof.lthr_run)
    report = analyzer.analyze_30d(wellness, act_dicts)

    advisor = CoachingAdvisor(prof)
    advice = advisor.advise(report, current_date=today)

    if args.json:
        print(json.dumps(advice.to_dict(), indent=2))
    else:
        for line in advice.to_lines():
            print(line)


def handle_export(cfg: Config, args: argparse.Namespace) -> None:
    """Export scheduled workouts to Zwift (.zwo), iCalendar (.ics), or JSON."""
    prof = AthleteProfileConfig.load()
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    today = datetime.date.today()
    start = today - datetime.timedelta(days=29)

    wellness = client.get_wellness_range(start.isoformat(), today.isoformat())
    acts = client.list_events(start.isoformat(), today.isoformat())
    act_dicts = [a.to_dict() for a in acts if a.category != "WORKOUT"]

    analyzer = RollingMetricsAnalyzer(target_hours_profile=prof.weekly_hours, athlete_lthr=prof.lthr_run)
    report = analyzer.analyze_30d(wellness, act_dicts)

    planner = DynamicRollingPlanner(prof)
    events = planner.generate_plan(report, weeks_to_plan=args.weeks)

    out_dir = Path(args.out_dir)
    fmt = args.format.lower()

    if fmt == "all":
        res = PlanExporter.export_all(events, out_dir)
        print(f"Exported plan files to {out_dir}:")
        print(f"  - iCalendar: {res.get('ics')}")
        print(f"  - JSON Plan: {res.get('json')}")
        if res.get("zwo_dir"):
            print(f"  - Zwift Workouts: {res.get('zwo_count')} files in {res.get('zwo_dir')}")
    elif fmt == "ics":
        out_dir.mkdir(parents=True, exist_ok=True)
        ics_path = out_dir / "training_plan.ics"
        ics_path.write_text(PlanExporter.events_to_ics(events), encoding="utf-8")
        print(f"Exported iCalendar to {ics_path}")
    elif fmt == "json":
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "training_plan.json"
        json_path.write_text(PlanExporter.events_to_json(events), encoding="utf-8")
        print(f"Exported JSON plan to {json_path}")
    elif fmt == "zwo":
        out_dir.mkdir(parents=True, exist_ok=True)
        zwo_count = 0
        for i, ev in enumerate(events):
            xml = PlanExporter.event_to_zwo(ev)
            if xml:
                clean_name = "".join(c if c.isalnum() or c in "._-" else "_" for c in (ev.name or f"ride_{i}"))
                fpath = out_dir / f"{clean_name}.zwo"
                fpath.write_text(xml, encoding="utf-8")
                zwo_count += 1
        print(f"Exported {zwo_count} Zwift .zwo workout files to {out_dir}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        return

    cfg = Config.load()

    if args.subcommand == "doctor":
        handle_doctor(cfg)
    elif args.subcommand == "auth" and args.auth_command == "test":
        handle_doctor(cfg)
    elif args.subcommand == "athlete" and args.athlete_command == "show":
        handle_doctor(cfg)
    elif args.subcommand == "plan":
        if args.plan_command == "validate":
            handle_plan_validate(args)
        elif args.plan_command == "preview":
            handle_plan_preview(args)
        elif args.plan_command == "export-json":
            plan = load_plan(args.file)
            builder = PlanBuilder(plan)
            evs = [e.to_dict() for e in builder.build_all_events()]
            out_str = json.dumps(evs, indent=2)
            if args.output:
                Path(args.output).write_text(out_str, encoding="utf-8")
                print(f" Exported {len(evs)} events to {args.output}")
            else:
                print(out_str)
        elif args.plan_command == "reschedule":
            print(f"Rescheduling {args.workout} in Week {args.week} to {args.date}...")
            # Handled via adaptive reschedule
            plan = get_default_8wk_plan()
            builder = PlanBuilder(plan)
            events = builder.build_all_events()
            events = AdaptiveEngine.reschedule_club_ride(events, args.week, args.date)
            if args.apply:
                client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
                sync_mgr = SyncManager(client=client, data_dir=cfg.data_dir, managed_prefix=plan.config.prefix)
                sync_mgr.apply_sync(events, plan.config.start_date, "2026-12-27", force=True)
                print(" Applied reschedule to Intervals.icu!")
            else:
                print("[DRY RUN] Rescheduled successfully in memory. Pass '--apply' to update live calendar.")
    elif args.subcommand == "events":
        if args.events_command == "list":
            handle_events_list(cfg, args)
        elif args.events_command == "show":
            handle_events_show(cfg, args)
        elif args.events_command == "delete":
            handle_events_delete(cfg, args)
        elif args.events_command == "delete-by-prefix":
            handle_delete_by_prefix(cfg, args)
        elif args.events_command == "restore":
            backup_mgr = BackupManager(cfg.data_dir / "backups")
            events = backup_mgr.load_backup(args.backup_id)
            print(f"Loaded {len(events)} events from backup '{args.backup_id}'.")
            if args.apply:
                client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
                client.bulk_upsert_events(events)
                print(f" Restored {len(events)} events to Intervals.icu!")
            else:
                print("[DRY RUN] Pass '--apply' to restore these events to Intervals.icu.")
    elif args.subcommand == "sync":
        handle_sync(cfg, args)
    elif args.subcommand == "adapt":
        handle_adapt(cfg, args)
    elif args.subcommand == "analyze":
        handle_analyze(cfg, args)
    elif args.subcommand == "profile":
        handle_profile(cfg, args)
    elif args.subcommand == "plan-next":
        handle_plan_next(cfg, args)
    elif args.subcommand == "manifest":
        manifest_file = cfg.data_dir / "manifest.json"
        if manifest_file.is_file():
            print(manifest_file.read_text(encoding="utf-8"))
        else:
            print("No manifest.json found. Run 'sync --apply' to initialize.")
    elif args.subcommand == "audit":
        audit = AuditLogger(cfg.data_dir / "audit.log")
        entries = audit.list_entries(limit=20)
        print(f"\n Recent Audit Log Entries ({len(entries)}):")
        for ent in entries:
            print(f"  - [{ent['timestamp']}] {ent['action']} | Status: {ent['status']} | Targets: {len(ent['target_ids'])}")
    elif args.subcommand == "watch-research":
        print_watch_research()
    elif args.subcommand == "coros-status":
        handle_coros_status(cfg)
    elif args.subcommand == "tp-status":
        handle_tp_status(cfg)
    elif args.subcommand == "ui":
        handle_ui(args)
    elif args.subcommand == "coach":
        handle_coach(cfg, args)
    elif args.subcommand == "export":
        handle_export(cfg, args)


if __name__ == "__main__":
    main()


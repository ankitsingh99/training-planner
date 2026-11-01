"""
Command-line interface for the Intervals.icu Adaptive Training Plan Tool.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from intervals_plan.adaptive import AdaptiveEngine
from intervals_plan.api_models import IntervalsEvent
from intervals_plan.audit import AuditLogger
from intervals_plan.backup import BackupManager
from intervals_plan.config import Config
from intervals_plan.diff import calculate_diff
from intervals_plan.integrations.watchletic_research import print_watch_research
from intervals_plan.intervals_client import IntervalsAPIError, IntervalsClient
from intervals_plan.plan_builder import PlanBuilder, get_default_8wk_plan
from intervals_plan.plan_models import PlanConfig, TrainingPlan
from intervals_plan.sync import SyncManager
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
    adapt_p.add_argument("--week", type=int, default=1, help="Week number to adapt")
    adapt_p.add_argument("--dry-run", action="store_true", default=True, help="Simulate without applying")
    adapt_p.add_argument("--apply", action="store_true", help="Apply adaptive change to calendar")

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
    print("\n🔍 Running Intervals.icu Diagnostics...\n")
    print(f"System:")
    print(f"  - Python Version: {sys.version.split()[0]}")
    print(f"  - Data Directory: {cfg.data_dir} (exists: {cfg.data_dir.exists()})")
    print(f"  - Config Summary:\n{cfg.summary()}\n")

    if not cfg.api_key:
        print("❌ Status: INTERVALS_API_KEY is not configured in .env or environment.")
        return

    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    res = client.doctor()
    if res.get("status") == "HEALTHY":
        print(f"✅ API Connectivity: HEALTHY")
        print(f"  - Athlete ID:     {res['athlete_id']}")
        print(f"  - Athlete Name:   {res['name']}")
        print(f"  - Timezone:       {res['timezone']}")
        print(f"  - Resting HR:     {res['resting_hr']} bpm")
        print(f"  - LTHR:           {res['lthr']} bpm")
    else:
        print(f"❌ API Connectivity Error: {res.get('error')}")


def handle_plan_validate(args: argparse.Namespace) -> None:
    plan = load_plan(args.file)
    errors = plan.validate()
    if errors:
        print(f"\n❌ Plan validation failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(f"\n✅ Plan '{plan.title}' validated successfully!")
        print(f"  - Weeks: {plan.config.total_weeks}")
        print(f"  - Start Date: {plan.config.start_date}")
        print(f"  - W4 Deload Bike: {'Included' if plan.config.include_w4_bike else 'Omitted (Restorative)'}")
        print(f"  - W8 5km Retest:  {'Included' if plan.config.include_w8_retest else 'Omitted'}")


def handle_plan_preview(args: argparse.Namespace) -> None:
    plan = load_plan(args.file)
    builder = PlanBuilder(plan)
    events = builder.build_all_events()

    print(f"\n📋 Plan Preview: {plan.title}")
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
    print(f"\n📅 Found {len(events)} events between {args.from_date} and {args.to_date}:")
    for ev in events:
        ext_tag = f" [{ev.external_id}]" if ev.external_id else ""
        print(f"  - ID: {ev.id or 'None':<9} | {ev.start_date_local} | {ev.type:<5} | {ev.name}{ext_tag}")


def handle_sync(cfg: Config, args: argparse.Namespace) -> None:
    plan = get_default_8wk_plan()
    builder = PlanBuilder(plan)
    events = builder.build_all_events()

    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    sync_mgr = SyncManager(client=client, data_dir=cfg.data_dir, managed_prefix=plan.config.prefix)

    start_date = plan.config.start_date
    end_date = "2026-12-27"

    diff, live_events = sync_mgr.preview_sync(events, start_date, end_date)
    print("\n🔄 Synchronization Diff:")
    print(diff.summary())

    if not args.apply:
        print("\n[DRY RUN] No changes were made to Intervals.icu.")
        print("Run with '--apply' to push mutations, or '--apply --force' to overwrite conflicts.")
        return

    print("\nApplying synchronization...")
    res = sync_mgr.apply_sync(events, start_date, end_date, force=args.force)
    print(f"✅ Sync Finished: Status = {res['status']}")
    print(f"  - Created:  {res['created']}")
    print(f"  - Updated:  {res['updated']}")
    print(f"  - Verified: {res['total_verified']}")
    print(f"  - Backup:   {res['backup_path']}")


def handle_events_delete(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    try:
        ev = client.get_event(args.event_id)
    except IntervalsAPIError as exc:
        print(f"❌ Error fetching event {args.event_id}: {exc}")
        return

    print(f"\n⚠️  Target Event for Deletion:")
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
    print(f"✅ Event {args.event_id} successfully deleted! (Backup saved to {backup_path})")

    audit = AuditLogger(cfg.data_dir / "audit.log")
    audit.log("DELETE_EVENT", [str(ev.id)], "SUCCESS", {"name": ev.name, "backup": str(backup_path)})


def handle_delete_by_prefix(cfg: Config, args: argparse.Namespace) -> None:
    client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
    live_events = client.list_events(args.from_date, args.to_date)
    matching = [e for e in live_events if e.external_id and e.external_id.startswith(args.prefix)]

    print(f"\n⚠️  Bulk Deletion Preview:")
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

    print(f"\n✅ Bulk deleted {deleted_count} events from Intervals.icu!")
    print(f"Backup saved to: {backup_path}")

    audit = AuditLogger(cfg.data_dir / "audit.log")
    audit.log("BULK_DELETE", [str(e.id) for e in matching], "SUCCESS", {"count": deleted_count, "backup": str(backup_path)})


def handle_adapt(cfg: Config, args: argparse.Namespace) -> None:
    plan = get_default_8wk_plan()
    builder = PlanBuilder(plan)
    events = builder.build_all_events()

    if args.club_ride_hard:
        print(f"\n🏃 Adaptive Trigger: Hard weekend club ride indicated for Week {args.week}.")
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
    print(f"✅ Applied adaptive modification to Intervals.icu calendar! ({res['status']})")


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
                print(f"✅ Exported {len(evs)} events to {args.output}")
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
                print("✅ Applied reschedule to Intervals.icu!")
            else:
                print("[DRY RUN] Rescheduled successfully in memory. Pass '--apply' to update live calendar.")
    elif args.subcommand == "events":
        if args.events_command == "list":
            handle_events_list(cfg, args)
        elif args.events_command == "show":
            client = IntervalsClient(api_key=cfg.api_key, athlete_id=cfg.athlete_id, base_url=cfg.base_url)
            ev = client.get_event(args.event_id)
            print(json.dumps(ev.to_dict(), indent=2))
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
                print(f"✅ Restored {len(events)} events to Intervals.icu!")
            else:
                print("[DRY RUN] Pass '--apply' to restore these events to Intervals.icu.")
    elif args.subcommand == "sync":
        handle_sync(cfg, args)
    elif args.subcommand == "adapt":
        handle_adapt(cfg, args)
    elif args.subcommand == "manifest":
        manifest_file = cfg.data_dir / "manifest.json"
        if manifest_file.is_file():
            print(manifest_file.read_text(encoding="utf-8"))
        else:
            print("No manifest.json found. Run 'sync --apply' to initialize.")
    elif args.subcommand == "audit":
        audit = AuditLogger(cfg.data_dir / "audit.log")
        entries = audit.list_entries(limit=20)
        print(f"\n📜 Recent Audit Log Entries ({len(entries)}):")
        for ent in entries:
            print(f"  - [{ent['timestamp']}] {ent['action']} | Status: {ent['status']} | Targets: {len(ent['target_ids'])}")
    elif args.subcommand == "watch-research":
        print_watch_research()


if __name__ == "__main__":
    main()

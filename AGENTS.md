# AGENTS.md — Guidelines for AI Coding Agents

## Mission & Architecture
`intervals-plan` is an adaptive, safe, user-operated CLI tool for managing multi-week endurance training plans on Intervals.icu.

### Principles:
1. **Never Log or Expose Secrets**: API keys must be loaded via `.env`, environment variables, or secure prompt (`getpass`). All authorization headers and tokens must be redacted in logs and CLI outputs.
2. **Safety First**:
   - Every mutation (create, edit, delete) defaults to **dry-run** mode.
   - Updates and creates require explicit `--apply`.
   - Single event deletion requires `--confirm-delete`.
   - Bulk deletion requires an exact typed confirmation phrase (e.g., `DELETE 30 EVENTS`).
   - Unmanaged events (outside the plan's prefix) and recorded activities are strictly protected.
3. **Read-Back Verification**: Never assume an HTTP success response means the database is updated. Re-read every modified or created event from Intervals.icu to verify IDs, timestamps, and contents.
4. **Offline Validation**: Plan schemas, interval structures, and workout documents must be completely testable offline with unit tests without making live network calls.
5. **Backups & Audit**: Create a timestamped backup before modifying or deleting any live events. Record every action in `data/audit.log` and track state in `data/manifest.json`.


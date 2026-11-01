"""Token and Context Size Audit for AdaptPulse.
Measures tracked file sizes, per-turn always-on context weight, and flags bloat.
Zero emojis, strict token accounting.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List

BUDGET_TOKENS = 8_000
FILE_LIMIT_BYTES = 10_000
BULK_EXT = {".json", ".csv", ".html", ".htm", ".pdf", ".xml"}


def tok(bytes_count: int) -> int:
    """Rough heuristic: 4 characters or bytes per token."""
    return bytes_count // 4


def get_tracked_files(root: Path) -> List[str]:
    """Retrieve list of tracked files via git or filesystem traversal."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout
        return [f for f in out.decode("utf-8", "replace").split("\0") if f]
    except Exception:
        return [
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts
        ]


def parse_frontmatter(text: str) -> Dict[str, str]:
    """Extract YAML frontmatter key-value pairs."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*(\n|$)", text, re.DOTALL)
    if not m:
        return {}
    fm: Dict[str, str] = {}
    key = None
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z_-]+:", line):
            key, _, val = line.partition(":")
            key = key.strip()
            v = val.strip().strip("\"'")
            fm[key] = "" if v in (">", "|", ">-", "|-") else v
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm


def run_token_audit(root_dir: str = ".", top: int = 20) -> Dict[str, Any]:
    """Audit repository token footprint and return structured dictionary."""
    root = Path(root_dir).resolve()
    files = get_tracked_files(root)
    sizes = {f: (root / f).stat().st_size for f in files if (root / f).is_file()}

    # Top tracked files
    top_files = sorted(sizes.items(), key=lambda kv: -kv[1])[:top]

    # Always-on context files
    always_on_items: List[Dict[str, Any]] = []
    total_always_on_tokens = 0

    for name in ("AGENTS.md", "GEMINI.md"):
        p = root / name
        if p.exists():
            s = p.stat().st_size
            t = tok(s)
            total_always_on_tokens += t
            always_on_items.append({
                "path": name,
                "bytes": s,
                "tokens": t,
                "over_limit": s > FILE_LIMIT_BYTES,
                "trigger": "always_on",
            })

    for rules_dir in (".agents/rules", ".agent/rules"):
        d = root / rules_dir
        if d.is_dir():
            for p in sorted(d.glob("*.md")):
                text = p.read_text(encoding="utf-8", errors="replace")
                fm = parse_frontmatter(text)
                s = p.stat().st_size
                t = tok(s)
                trig = fm.get("trigger", "always_on")
                total_always_on_tokens += t
                always_on_items.append({
                    "path": str(p.relative_to(root)),
                    "bytes": s,
                    "tokens": t,
                    "over_limit": s > FILE_LIMIT_BYTES,
                    "trigger": trig,
                })

    big_files = [
        {"path": f, "bytes": s, "kb": round(s / 1024, 1)}
        for f, s in sizes.items()
        if s > 50_000
    ]
    bulk_targets = [
        {"path": f, "bytes": s, "kb": round(s / 1024, 1)}
        for f, s in sizes.items()
        if Path(f).suffix.lower() in BULK_EXT and s > 20_000
    ]

    return {
        "tracked_files_count": len(files),
        "total_tracked_bytes": sum(sizes.values()),
        "total_tracked_tokens": tok(sum(sizes.values())),
        "always_on_tokens": total_always_on_tokens,
        "always_on_budget_tokens": BUDGET_TOKENS,
        "always_on_budget_pct": round(100.0 * total_always_on_tokens / BUDGET_TOKENS, 1),
        "always_on_items": always_on_items,
        "top_files": [{"path": f, "bytes": s, "tokens": tok(s)} for f, s in top_files],
        "flags": {
            "files_over_50kb": big_files,
            "bulk_targets_over_20kb": bulk_targets,
        },
    }


def format_audit_report(data: Dict[str, Any]) -> str:
    """Format audit results as readable CLI plain text."""
    lines: List[str] = []
    lines.append("=" * 64)
    lines.append("  ADAPTPULSE REPOSITORY TOKEN & CONTEXT AUDIT")
    lines.append("=" * 64)
    lines.append(f"Tracked Files: {data['tracked_files_count']}")
    lines.append(f"Total Tracked Size: {data['total_tracked_bytes']:,} Bytes (~{data['total_tracked_tokens']:,} tokens)")
    lines.append("")
    lines.append("[ALWAYS-ON CONTEXT PER TURN]")
    for item in data["always_on_items"]:
        flag = " [OVER 10KB LIMIT]" if item["over_limit"] else ""
        lines.append(f"  * {item['path']:<35} {item['bytes']:>6} B (~{item['tokens']:>4} t) trigger={item['trigger']}{flag}")
    lines.append(f"  TOTAL ALWAYS-ON: ~{data['always_on_tokens']} tokens of {data['always_on_budget_tokens']} token budget ({data['always_on_budget_pct']}%)")
    lines.append("")
    lines.append("[TOP TRACKED FILES BY TOKEN SIZE]")
    for f in data["top_files"][:10]:
        lines.append(f"  {f['bytes']:>8} B ~{f['tokens']:>6} t  {f['path']}")
    lines.append("")
    lines.append("[FLAGS & HYGIENE]")
    f50 = data["flags"]["files_over_50kb"]
    b20 = data["flags"]["bulk_targets_over_20kb"]
    lines.append(f"  Files > 50KB: {len(f50)}" + (f" ({', '.join(x['path'] for x in f50)})" if f50 else " (None)"))
    lines.append(f"  Bulk Targets > 20KB: {len(b20)}" + (f" ({', '.join(x['path'] for x in b20)})" if b20 else " (None)"))
    lines.append("=" * 64)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit token footprint and context size.")
    parser.add_argument("--top", type=int, default=15, help="Number of top files to display")
    parser.add_argument("--root", default=".", help="Root directory of repository")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    data = run_token_audit(root_dir=args.root, top=args.top)
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_audit_report(data))


if __name__ == "__main__":
    main()


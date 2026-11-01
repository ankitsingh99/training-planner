#!/usr/bin/env python3
"""Compact repository structure map tool.
Extracts symbols, class definitions, function signatures, and markdown headings with line numbers.
Enables agents to locate definitions before reading targeted line ranges.
Zero emojis, strict token accounting.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
from pathlib import Path
from typing import Callable, Dict, List

SKIP_DIRS = {"__pycache__", ".venv", "venv", "node_modules", ".git", ".cache", ".pytest_cache"}
MAX_FILE_BYTES = 250_000


def get_files_under(paths: List[str]) -> List[Path]:
    """Resolve file paths or git tracked files under given directories."""
    result: List[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            result.append(p)
            continue
        try:
            out = subprocess.run(
                ["git", "ls-files", "-z", str(p)],
                capture_output=True,
                check=True,
            ).stdout
            candidates = [Path(x) for x in out.decode("utf-8", "replace").split("\0") if x]
        except Exception:
            candidates = [x for x in p.rglob("*") if x.is_file()]
        result.extend([c for c in candidates if not SKIP_DIRS.intersection(set(c.parts))])
    return sorted(set(result))


def parse_python_symbols(text: str) -> List[str]:
    """Parse Python AST and extract classes and function signatures."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ["  (syntax error, unparsed)"]

    fn_types = (ast.FunctionDef, ast.AsyncFunctionDef)
    lines: List[str] = []

    def sig(f: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        args_list = [a.arg for a in f.args.args]
        return f"{f.name}({', '.join(args_list)})"

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            lines.append(f"  L{node.lineno} class {node.name}")
            for item in node.body:
                if isinstance(item, fn_types):
                    lines.append(f"    L{item.lineno} {sig(item)}")
        elif isinstance(node, fn_types):
            lines.append(f"  L{node.lineno} {sig(node)}")

    return lines


def parse_markdown_headings(text: str) -> List[str]:
    """Parse Markdown headings with line numbers."""
    lines: List[str] = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            m = re.match(r"^(#{1,6})\s+(.*)", line)
            if m:
                level = len(m.group(1))
                indent = "  " * level
                lines.append(f"{indent}L{i} {m.group(2)[:70]}")
    return lines


def parse_shell_functions(text: str) -> List[str]:
    """Parse Shell function declarations."""
    lines: List[str] = []
    sh_pattern = re.compile(r"^\s*(?:function\s+)?([A-Za-z0-9_-]+)\s*\(\)\s*\{")
    for i, line in enumerate(text.splitlines(), start=1):
        m = sh_pattern.match(line)
        if m:
            lines.append(f"  L{i} {m.group(1)}()")
    return lines


HANDLERS: Dict[str, Callable[[str], List[str]]] = {
    ".py": parse_python_symbols,
    ".md": parse_markdown_headings,
    ".sh": parse_shell_functions,
}


def generate_directory_summary() -> List[str]:
    """Generate high-level summary of file counts and types per top-level directory."""
    try:
        out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True).stdout
        files = [x for x in out.decode("utf-8", "replace").split("\0") if x]
    except Exception:
        files = [str(x) for x in Path(".").rglob("*") if x.is_file() and not SKIP_DIRS.intersection(set(x.parts))]

    directory_map: Dict[str, Dict[str, int]] = {}
    for f in files:
        top = f.split("/")[0] if "/" in f else "(root)"
        ext = Path(f).suffix or "(none)"
        directory_map.setdefault(top, {})
        directory_map[top][ext] = directory_map[top].get(ext, 0) + 1

    summary_lines: List[str] = []
    for top_dir, extensions in sorted(directory_map.items()):
        total = sum(extensions.values())
        ext_str = " ".join(f"{ext}:{count}" for ext, count in sorted(extensions.items(), key=lambda kv: -kv[1])[:4])
        summary_lines.append(f"{top_dir:<18} {total:>3} files   {ext_str}")
    return summary_lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Compact symbol outline and repository structure map.")
    parser.add_argument("paths", nargs="*", help="File or directory paths to map (defaults to top-level summary)")
    parser.add_argument("--max-lines", type=int, default=150, help="Maximum output lines before truncating")
    args = parser.parse_args()

    lines: List[str] = []
    if not args.paths:
        lines = generate_directory_summary()
    else:
        for file_path in get_files_under(args.paths):
            handler = HANDLERS.get(file_path.suffix.lower())
            if not handler or file_path.stat().st_size > MAX_FILE_BYTES:
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            symbols = handler(content)
            if symbols:
                lines.append(f"{file_path} ({len(content.splitlines())} lines)")
                lines.extend(symbols)

    output = "\n".join(lines[:args.max_lines])
    print(output)
    if len(lines) > args.max_lines:
        print(f"... truncated ({len(lines) - args.max_lines} more lines; specify a narrower path)")


if __name__ == "__main__":
    main()


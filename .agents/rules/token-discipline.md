---
trigger: always_on
description: "Token discipline: locate before reading, cap tool output, local-compute first."
---
# Token Discipline (Always On)
1. Locate first: Use `tools/repo_map.py <path>`, `grep -n`, or `git ls-files | grep`. Then read line ranges. Never dump whole files over 100 lines when searching.
2. Local-compute first: Always run deterministic algorithms (ACWR, PMC, CSS pacing, compliance, fueling calculations) locally in Python at 0 tokens rather than asking LLMs.
3. Cache LLM queries: Utilize local SQLite response cache so identical coaching queries consume 0 tokens.
4. Wrap noisy commands: Use `tools/q.sh <command>` when running commands that produce extensive logs or test dumps.
5. In LLM generation: Enforce strict max_tokens bounds (<= 400 tokens) and JSON mode to prevent conversational fluff.
6. Report concise summaries and diffs, not duplicated whole files.


---
description: Run a cross-session retrospective. The reflector reads every `.plans/*-reflection.md` in this repo (and the repo memory file if present), aggregates recurring themes across sessions, and writes durable trend advice to `.plans/_meta-reflection.md`. Use this after you've accumulated 3+ completed plans to surface patterns the per-session reflections can't see on their own.
argument-hint: "(no arguments — runs over every reflection file in .plans/)"
---

The user wants a **cross-session** retrospective from the autonomous-builder
plugin. This is different from the per-session reflector that runs at the
end of every plan: it looks across many sessions to find patterns.

Invoke the `reflector` subagent in **`cross-session` mode**. Do not start
the per-session reflection loop and do not invoke the orchestrator. The
reflector handles the whole thing in one dispatch.

Pass the following brief to the reflector:

```
mode: cross-session
plans_dir: .plans/
repo_memory_path: /memories/repo/autonomous-builder.md   (read-only here; reflector only reads it for context)
output_path: .plans/_meta-reflection.md
```

The reflector will:

1. Glob `.plans/*-reflection.md` and read each one (skip files starting
   with `_` to avoid reading prior meta-reflections).
2. If `/memories/repo/autonomous-builder.md` exists, read it for the
   "stable facts" context.
3. Mine for **recurring** patterns across sessions: same `failure_mode`
   appearing in multiple sessions, same advice item repeated across
   audiences, the user-prompt section saying the same thing 3+ times,
   etc. A pattern that appears once is session-local; a pattern that
   appears twice is a coincidence; a pattern that appears 3+ times is
   actionable.
4. Write `.plans/_meta-reflection.md` per the cross-session template in
   `references/reflecting-on-sessions/SKILL.md`.
5. Return a one-line artefact summary to you.

If `.plans/` has fewer than 3 `*-reflection.md` files, the reflector
returns a one-line "insufficient corpus — wait for more sessions" reply
and writes nothing. That's the correct behaviour; trend mining on a
single session is just a re-statement of the per-session reflection.

Surface the reflector's artefact summary to the user verbatim, plus a
pointer to the output file. Do not summarise the meta-reflection's
contents — the user opens the file for that.

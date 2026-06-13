---
name: reflecting-on-sessions
description: Use this skill when the reflector agent (`reflector.md`) is producing a retrospective in either of its two modes. **Per-session mode** (orchestrator dispatch at terminal Status) reads one plan file, writes `.plans/<slug>-reflection.md`, and promotes durable codebase facts to `/memories/repo/autonomous-builder.md`. **Cross-session mode** (slash-command dispatch via `/autonomous-reflect`) reads every `.plans/*-reflection.md` plus repo memory, mines for recurring patterns (3+ occurrences = actionable), and writes `.plans/_meta-reflection.md`. Defines read protocols, signal-mining checklists, the three-audience advice rule, the evidence-citation contract, the file templates, and the repo-memory promotion rules.
---

# Reflecting on Sessions

The reflector turns autonomous-builder runs into durable,
evidence-backed improvement advice. It operates in two modes —
**per-session** (one run at a time, automatic) and **cross-session**
(many runs at once, on demand) — plus an explicit hop into
repo memory so durable facts compound across sessions instead of
being re-discovered each time.

## When to use

- **Per-session mode**: loaded when the orchestrator dispatches the
  reflector at wrap-up (overall Status `Done`) or at escalation
  (overall Status `Blocked`). Output: `.plans/<slug>-reflection.md`
  AND ≤5 promoted lines in `/memories/repo/autonomous-builder.md`.
- **Cross-session mode**: loaded when the `/autonomous-reflect`
  slash command invokes the reflector with `mode=cross-session`.
  Output: `.plans/_meta-reflection.md` (or a one-line
  "insufficient corpus" reply if there are < 3 reflection files).
- Consulted by the orchestrator when crafting the per-session
  dispatch brief, and by the slash command when crafting the
  cross-session brief, so both briefs match what this skill
  expects.

## Read protocol

### Per-session mode

1. Read `.plans/<slug>.md` in full once. Do not chunk — you need
   the whole timeline to spot patterns.
2. **Read `/memories/repo/autonomous-builder.md` if it exists**
   (read-only). You need it for two reasons:
   (a) to know what's already in repo memory so you don't promote
   a duplicate fact, and (b) to spot facts in this session's
   Discoveries that *supersede* prior repo-memory entries.
3. Do NOT read:
   - Other plan files.
   - Other reflection files.
   - Agent / skill / command / manifest files in the plugin repo.
   - Product code in the target repo.
   - Any session log, transcript, or implementer scratch.

### Cross-session mode

1. Glob `<plans_dir>/*-reflection.md`. Exclude filenames starting
   with `_` (those are prior meta-reflections; reading them would
   bias toward old conclusions).
2. If the resulting corpus has < 3 files, **stop and return**
   "insufficient corpus — wait for more sessions". Trend mining
   on ≤2 reflections just re-states the per-session output.
3. Read each reflection in the corpus in full.
4. Read `/memories/repo/autonomous-builder.md` if it exists
   (read-only) for stable-facts context — it tells you what's
   already been promoted so you don't recommend re-promoting it.
5. Do NOT read:
   - Plan files (`.plans/<slug>.md`) — reflection files are
     already distilled summaries; plan files would blow context.
   - Agent / skill files.
   - Product code.

The isolation is intentional in both modes. The reflector runs
cheaply and reproducibly because it can only see the same
"shared knowledge" surface every other agent could see.

## Signal-mining checklist

Walk the plan file once, collecting:

### Per-task

- Number of attempts before `Done` (or `Blocked`).
- Per-attempt verdict (PASS / FAIL / PLAN_WRONG).
- For each FAIL: the `failure_mode:` label.
- Whether two attempts in a row had the same `failure_mode` (adaptive
  retry should have caught this).
- Whether any AC was rejected as `PLAN_WRONG` for well-formedness
  (untagged, banned phrasing, destructive command).

### Per-phase

- Phase Definition of Done verdict on first run.
- Whether the phase produced a revision block.

### Plan-wide

- Count and trigger of `## Revision N (proposed)` blocks.
- `## Discoveries` volume by author (planner / researcher / implementer
  / reviewer) and by phase (late-phase Discoveries from the planner are
  a smell — they should have been seeded up front).
- Tasks marked `Blocked` and the path that got them there.
- Total attempts vs. tasks ratio (over ~1.5 suggests systemic issue).

## Audience rule

Every reflection produces advice across **exactly three audiences**:

### 1. User prompt

Could the original goal have been phrased differently to avoid the
churn observed? Specifically:

- If `## Revision 1` was triggered by a scope clarification the user
  could have given up front → suggest the missing phrasing.
- If multiple revisions originated from "we discovered file X is gone"
  → suggest including a "current state of the area" sentence in the
  goal.
- If the plan finished `Done` with zero revisions and ≤1 retry per
  task → say so explicitly under "User prompt" — the prompt was good.

### 2. Agent prompts

Each worker has its own bar; mine the plan for hits against each:

- **Planner** — late Discoveries from `[planner · …]` in mid- or
  late-phase rows, AC rejected for vagueness, tasks that needed
  splitting (multiple PLAN_WRONGs on one task).
- **Implementer** — repeated `failure_mode:` across attempts on the
  same task (didn't read reviewer feedback?), Discoveries that should
  have been a researcher dispatch instead.
- **Reviewer** — vague feedback that didn't help the next attempt,
  missed a destructive AC the planner sneaked in, accepted a vague AC
  on the first attempt only to reject it later.
- **Orchestrator** — wrong AC mode (`fast+full` too early or never;
  `dod` skipped),
  skipped phase checkpoints, advanced past a Blocked task.

If a worker's prompt is fine, omit it from this section — don't pad.

### 3. Plan / process

Anything that doesn't pin to a single agent's prompt:

- Phase boundaries that bundled too much / too little.
- AC cadence choices (`[Full]` AC that should have been `[Fast]` or
  vice-versa; `[Journey]` AC missing where they would have caught a
  regression).
  vice-versa).
- Retry budget (3 was too many / too few for this kind of work).
- Whether researcher should have been dispatched proactively at plan
  time on areas that produced late Discoveries.

## Evidence-citation contract

Every advice item must cite **at least one** concrete plan-file
location, in one of these forms:

- `Task <X.Y> Review log attempt <N>` (e.g. "Task 2.3 Review log
  attempt 2 — failure_mode: import-error repeated from attempt 1").
- `## Revision <N>` (e.g. "Revision 1 triggered by Task 2.3 PLAN_WRONG").
- `## Discoveries entry [<agent> · <date>]` (e.g. "Discoveries entry
  [planner · 2026-06-10] arrived after Phase 2 started").
- `Phase <N> Definition of Done` (when a DoD AC outcome is the
  signal).

No advice item without a citation is allowed in the reflection file.
"This kind of session usually struggles with X" with no plan-file
evidence is decoration — drop it.

## Banned phrases

The reflection file inherits the same banned-phrase list the workers
have. Reject (rewrite, do not ship) any of:

- "I would suggest"
- "should work"
- "may need"
- "appears to"
- "likely"
- "left as future work"
- "for now"

These hide the same uncertainty the worker prompts forbid. If you find
yourself reaching for one, you're missing evidence — go re-read the
plan file or omit the item.

Also banned: any advice that boils down to **"the agent should try
harder"** or **"be more careful"**. Improvement advice must always
name a *missing mechanism* — an AC that should have been written, a
researcher dispatch that should have happened, a checkpoint that
should have been added — never an exhortation to a future invocation.

## Reflection-file template

Write the file at `.plans/<slug>-reflection.md`. Overwrite if it
exists. Use this exact skeleton:

````markdown
# Reflection: <plan title>

**Plan file:** `.plans/<slug>.md`
**Terminal Status:** Done | Blocked
**Generated:** <YYYY-MM-DD>

## Session stats

- Phases: <P> (Done: <p_done>, Blocked: <p_blocked>)
- Tasks: <T> (Done: <t_done>, Blocked: <t_blocked>)
- Total implementer attempts: <A> (ratio A/T = <a_per_t>)
- FAIL verdicts: <F>
- PLAN_WRONG verdicts: <pw>
- Revisions: <R>
- Discoveries appended: <D> (planner: <dp>, researcher: <dr>, implementer: <di>, reviewer: <drv>)

## What worked

- <Bullet — concrete thing the session did well, with citation.>
- <Bullet — …>

## What didn't

- <Bullet — concrete pattern that hurt the session, with citation.>
- <Bullet — …>

## Advice — user prompt

<One-paragraph diagnosis, then 1–5 bullet items. If the prompt was
fine, write a single line saying so and stop.>

- <Item> — Evidence: <citation>.
- <Item> — Evidence: <citation>.

## Advice — agent prompts

<Subsection per worker that has actionable advice. Omit workers with
none.>

### Planner

- <Item> — Evidence: <citation>.

### Implementer

- <Item> — Evidence: <citation>.

### Reviewer

- <Item> — Evidence: <citation>.

### Orchestrator

- <Item> — Evidence: <citation>.

## Advice — plan / process

- <Item> — Evidence: <citation>.
- <Item> — Evidence: <citation>.

## Suggested follow-up

<≤3 bullet items the user could act on next. Each is either:
- a concrete prompt-edit (e.g. "next time start the goal with: '<text>'"), or
- a concrete agent-or-skill edit (e.g. "in `agents/planner.md`, add a
  bullet under Self-review: 'researcher dispatched proactively for any
  area touching unfamiliar files'").

If nothing actionable, write "None — session ran cleanly." and stop.>

## Promotion summary

<List which Discoveries from this session were promoted to
`/memories/repo/autonomous-builder.md`, and which were considered
but held back (with one-line reason). If none promoted, write
"None — no Discovery this session met the promotion gate (stable +
cited + cross-plan-useful + non-redundant + not banned-content)."

Format:

**Promoted (N/5):**
- `[implementer · 2026-06-13]` Tests run via `pytest` from repo root (`pyproject.toml:42`).
  → `## Build / test / run`.
- ...

**Considered but held back:**
- `[implementer · 2026-06-13]` Added `--verbose` flag to `cli.py:24`.
  → Held: not stable (this session's diff, not a cross-plan fact).
- ...>
````

## Repo-memory promotion protocol (per-session mode only)

Per-session mode is the **only** writer of
`/memories/repo/autonomous-builder.md`. Cross-session mode reads
but never writes it.

### Path resolution

Resolve `/memories/repo/autonomous-builder.md` against the **plan
file's containing repo root** (the directory containing the
`.plans/` directory of the plan you're reflecting on), not against
the agent's cwd. This ensures a plan run in
`~/work/projectA/.plans/foo.md` writes to
`~/work/projectA/memories/repo/autonomous-builder.md`, not to
some other repo's memory.

### Magic-header refusal

Before writing, read the file's first line if it exists.

- If file does not exist → create it with the canonical skeleton
  (see "File shape" below).
- If file exists AND first line is exactly
  `# Autonomous-builder repo memory` → safe to Edit (append).
- If file exists with any other first line → **refuse**: skip the
  promotion step entirely, do not modify the file, and log in the
  reflection file's "Promotion summary" section:
  `Skipped: repo memory path collides with a non-autonomous-builder file (first line: "<actual first line>"). User must resolve by renaming or deleting the existing file.`

### Promotion gate (all five must pass)

Walk this session's `## Discoveries`. For each Discovery, ask:

1. **Stable.** Would this fact still be true 3 months from now,
   assuming the codebase grows but doesn't get rewritten? "Tests
   run via X" — stable. "We added flag Y" — not stable (that's
   the diff).
2. **Cited.** The Discovery has a `file:line` citation. Before
   promoting, **`Read` the cited file** and confirm the line still
   says something matching the fact. If the line moved or
   changed, either update the citation (re-grep) or drop the
   promotion. No fabricated citations into repo memory ever.
3. **Cross-plan-useful.** Would a future plan in this repo, on a
   different goal, benefit from knowing this? "Auth middleware
   at X" — useful. "This fixture's ID is 42" — not useful.
4. **Non-redundant.** Grep repo memory for the fact's key terms.
   If the same fact already exists and hasn't changed, skip. If
   it exists but is materially different (file moved, command
   changed), append a `supersedes <prior-date>` line instead of
   a fresh one.
5. **Not banned content.** Reject if the fact contains any of:
   - **Secrets / values.** Env-var values, API tokens, passwords,
     private keys. The env-var **name** is fine (`TEST_PASSWORD`);
     the value is not.
   - **Customer identifiers.** Real customer names, real
     account IDs, real email domains that aren't `*.test.local`
     or `*.example.com`.
   - **Internal infra disclosure.** URLs with `.internal`,
     `*.corp.*`, private IP ranges, internal ticket-tracker
     IDs that reveal product strategy.
   - **Credentials of any kind**, even ones that look fake.

### Promotion cap: 5 per session

Hard cap. Forces curation. If more than 5 Discoveries pass the
gate, rank by usefulness (architecture landmarks > build/test
commands > sharp edges > conventions) and promote the top 5. Log
the rest under "Considered but held back".

### File shape

```markdown
# Autonomous-builder repo memory

Curated facts the autonomous-builder plugin has learned about
this repo across sessions. Append-only with `supersedes` markers.
Read by the planner during initial discovery (step 0); the
per-session reflector is the only writer.

**Last updated:** YYYY-MM-DD by reflector for plan `<slug>`.

## Build / test / run

- [reflector · YYYY-MM-DD · plan: <slug>] <fact> (<file:line>)

## Architecture landmarks

- [reflector · YYYY-MM-DD · plan: <slug>] <fact> (<file:line>)

## Test environment

- [reflector · YYYY-MM-DD · plan: <slug>] <fact> (<file:line>)

## Known sharp edges

- [reflector · YYYY-MM-DD · plan: <slug>] <fact> (<file:line>)

## Conventions

- [reflector · YYYY-MM-DD · plan: <slug>] <fact> (<file:line>)
```

The reflector creates this skeleton on first write (all five
section headers, even if some sections start empty). Subsequent
writes append under the appropriate section.

### Section vocabulary (fixed)

Pick exactly one section per promoted line:

- `## Build / test / run` — how to invoke tests, lints, builds, runs.
- `## Architecture landmarks` — where things live (file paths +
  responsibilities). Stable-ish; superseded when files move.
- `## Test environment` — bring-up commands, fixtures, seed data,
  test-cred *locations* (env-var names; never values).
- `## Known sharp edges` — gotchas the next session will trip on.
- `## Conventions` — coding/style/naming rules the implementer
  should mirror.

No other section names. If a Discovery doesn't fit one of these,
it's not a stable fact and shouldn't be promoted.

### Line format with supersede

```
- [reflector · YYYY-MM-DD · plan: <slug>] <fact> (<file:line or N/A>)
- [reflector · YYYY-MM-DD · plan: <slug> · supersedes YYYY-MM-DD] <updated fact> (<file:line>)
```

The plan slug lets a human find the originating session if the
fact is wrong. Supersede lines are appended; old lines stay (the
audit trail is part of the value).

### Size cap: 200 lines

Past 200 lines, the next write **compacts** before appending:

1. For each topic, keep the most recent `supersedes` line and
   drop the older superseded lines.
2. If still > 200 after compaction, drop oldest-by-date lines
   from `## Known sharp edges` first (most likely to be stale),
   then from `## Conventions`. Never auto-drop from
   `## Build / test / run` or `## Architecture landmarks` — surface
   to the user instead via the reflection file's Promotion
   summary section.

## Cross-session reflection (meta-reflection)

When the reflector runs in cross-session mode, it writes
`.plans/_meta-reflection.md` per the template below. The
**3+-occurrences threshold** is the core rule: a pattern that
appears in three or more reflections is systemic; one or two
times is local and stays in the per-session reflections.

### Cross-session signal-mining

Walk the reflection corpus once, building counts:

- **failure_mode tallies.** For each unique failure_mode label
  across all reflections, count occurrences. Anything ≥3 is a
  pattern. (Pull from per-session "Session stats" or
  parenthetical `(failure_mode: X)` mentions.)
- **PLAN_WRONG trigger tallies.** Same idea for trigger
  categories (`unharvested-research`, `mis-tagged AC`, etc.).
- **Per-audience advice clusters.** Group advice items that
  paraphrase each other. Three reflections all saying "planner
  under-decomposed Phase 2" → one pattern.
- **User-prompt pattern.** If three or more reflections critique
  the user's prompt with the same shape ("goal was too broad",
  "missing 'current state' context"), surface a single
  user-facing trend.
- **Promotion-summary signal.** If three reflections in a row
  show "0 promoted" or "all held back: stale citations", the
  repo's pace of change is outrunning the promotion gate — a
  process-level signal.

### Cross-session template

Write to `.plans/_meta-reflection.md`. Overwrite if exists.

````markdown
# Meta-reflection: autonomous-builder corpus

**Generated:** <YYYY-MM-DD>
**Reflections analysed:** <N> (from `.plans/*-reflection.md`, excluding `_*`)
**Date range:** <earliest YYYY-MM-DD> → <latest YYYY-MM-DD>
**Repo memory present:** yes | no

## Corpus stats

- Total plans: <N>
- Done / Blocked split: <d> / <b>
- Median attempts/task across corpus: <m>
- Total promoted facts (in repo memory): <p>

## Recurring patterns (≥3 occurrences)

For each pattern, list the evidence reflections explicitly so a
human can audit. Drop patterns with only 1 or 2 occurrences.

### Pattern: <one-line description>

- Occurrences: <N>
- Evidence: `<slug-a>-reflection.md`, `<slug-b>-reflection.md`, `<slug-c>-reflection.md`
- Diagnosis: <2–3 sentences. What's the common thread?>
- Recommendation: <one of:
  - "User prompt: <concrete phrasing change>"
  - "Agent prompt edit: in `agents/<agent>.md`, <concrete change>"
  - "Process: <skill or workflow change>"
  - "Repo memory: <missing fact that would have prevented this>">

### Pattern: ...

## Trends in repo memory

- Compaction events in the last N sessions: <count> (sustained > 0
  means promotions are outpacing curation).
- Supersede chains > 2 deep on any topic: <list, with topic + chain
  length>. Long supersede chains suggest the underlying fact is
  actually unstable and should NOT be in repo memory.

## Honest gaps

- Patterns the reflector noticed but couldn't pin to ≥3 evidence
  files (interesting but below threshold; surface for the human
  to watch):
  - <Pattern> — only <N> occurrence(s) so far.

If no recurring patterns exist (every reflection is unique), say
so in two lines and stop. Padding is forbidden — same as
per-session mode.
````

### Honesty rule (cross-session)

Same bar as per-session. If the corpus has < 3 reflections, the
file is one line: "Insufficient corpus (only <N> reflection(s);
need ≥3 for trend analysis)." Don't pad.

## Dispatch brief

### Per-session (orchestrator)

The orchestrator dispatches the reflector with:

- `mode: per-session` (explicit; default if omitted for backwards
  compatibility).
- Plan-file path (e.g. `.plans/add-hello-command.md`).
- Slug (e.g. `add-hello-command`).
- Terminal Status (`Done` or `Blocked`).
- (Optional) one-line note on why this run is interesting
  (e.g. "two PLAN_WRONGs in Phase 2 — please dig").

### Cross-session (slash command)

The `/autonomous-reflect` slash command dispatches with:

- `mode: cross-session`.
- `plans_dir: .plans/` (or whatever the command resolves to).
- `repo_memory_path: /memories/repo/autonomous-builder.md`
  (read-only in this mode).
- `output_path: .plans/_meta-reflection.md`.

If any required field for the chosen mode is missing, the
reflector returns a one-line clarification request instead of
guessing.

## Honesty rule (both modes)

If there is genuinely nothing substantive to surface, the
output is allowed to be short. Padding is forbidden.

**Per-session:**
- "Session stats" — full block always.
- "What worked" — at least 1 bullet.
- "What didn't" — write `- None observed in this session.` if true.
- "Advice — *" — write `- None — session ran cleanly.` if true.
- "Suggested follow-up" — same.
- "Promotion summary" — write the gate-failure reason if none
  promoted; never silently skip the section.

**Cross-session:**
- < 3 reflections in corpus → one line: `Insufficient corpus
  (<N>; need ≥3 for trend analysis).` Write nothing else.
- ≥ 3 reflections but no ≥3-occurrence patterns → "Corpus
  stats" full block + "## Recurring patterns: none above the
  3+-occurrences threshold." + "## Honest gaps" listing the
  near-miss patterns. Stop.

A short, honest reflection is better than a padded one. The
banned-phrase list above is the trip-wire.

## Self-review before returning

### Per-session

- [ ] Read only `.plans/<slug>.md` (+ repo memory read-only,
      if present) — no other source files.
- [ ] Computed all session stats from the plan file (no estimates).
- [ ] Each advice item cites a concrete plan-file location.
- [ ] Promotion summary section is present (filled or honestly
      empty with reason).
- [ ] If promoting: ran the magic-header check on repo memory
      first; refused if mismatch.
- [ ] Each promoted line passes all 5 gate checks (stable,
      cited & confirmed by Read, cross-plan-useful, non-redundant,
      not banned content).
- [ ] At most 5 promotions.
- [ ] No banned phrases.
- [ ] No "try harder" / "be more careful" advice.
- [ ] If session was clean, reflection is short and honest
      (not padded).
- [ ] Wrote exactly `.plans/<slug>-reflection.md` and (if
      promoting) `/memories/repo/autonomous-builder.md` — no
      other files.
- [ ] Did not edit the plan file or any agent / skill file.
- [ ] Returned artefact summary (paths + counts) to orchestrator.

### Cross-session

- [ ] Read only `<plans_dir>/*-reflection.md` (excluded `_*`)
      plus repo memory (read-only) — no plan files, no product
      code, no agent files.
- [ ] If corpus < 3: returned "insufficient corpus" and wrote
      nothing.
- [ ] Each pattern reported names ≥3 specific reflection files
      as evidence.
- [ ] No banned phrases.
- [ ] No "try harder" advice.
- [ ] Did NOT modify repo memory (per-session is the only writer).
- [ ] Wrote exactly `.plans/_meta-reflection.md` — no other files.
- [ ] Returned artefact summary.

## References

- `../plan-file-format/SKILL.md` — Status / Review log / Discoveries /
  Revision block semantics.
- `../orchestration-loop/SKILL.md` — when the orchestrator dispatches
  the reflector and how the wrap-up message links to the reflection
  file.

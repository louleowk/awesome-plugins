---
name: reflecting-on-sessions
description: Use this skill when the reflector agent (`reflector.md`) is producing the end-of-session retrospective. It defines the read protocol (plan file only), the signal-mining checklist (Review logs, retries, PLAN_WRONG, revisions, Discoveries, Blocked tasks), the three-audience advice rule (user prompt / agent prompts / plan-process), the evidence-citation contract, and the reflection-file template. Loaded by the reflector and consulted by the orchestrator when it dispatches the reflector at wrap-up.
---

# Reflecting on Sessions

The reflector turns one finished autonomous-builder run into durable,
evidence-backed improvement advice. Its only output is the reflection
file `.plans/<slug>-reflection.md`. Its only input is `.plans/<slug>.md`.

## When to use

- Loaded by the `reflector` agent when the orchestrator dispatches it
  at wrap-up (overall Status `Done`) or at escalation (overall Status
  `Blocked`).
- Consulted by the orchestrator when deciding what brief to send the
  reflector (so the brief matches what this skill expects).

## Read protocol

1. Read `.plans/<slug>.md` in full once. Do not chunk — you need the
   whole timeline to spot patterns.
2. Do NOT read:
   - Other plan files.
   - Agent / skill / command / manifest files in the plugin repo.
   - Product code in the target repo.
   - Any session log, transcript, or implementer scratch.
3. The plan file is the durable session record. Anything not durable
   enough to make it into the plan file (Context, Discoveries, Review
   log) is by definition out of scope for reflection.

This isolation is intentional. Reflection runs cheaply and reproducibly
because it can only see what every other agent could see — the same
"shared knowledge" surface the reviewer judges against.

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

- Phase regression AC verdict on first run.
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
- **Orchestrator** — wrong AC mode (cheap+gate too early or never),
  skipped phase checkpoints, advanced past a Blocked task.

If a worker's prompt is fine, omit it from this section — don't pad.

### 3. Plan / process

Anything that doesn't pin to a single agent's prompt:

- Phase boundaries that bundled too much / too little.
- AC tier choices (`[gate]` AC that should have been `[cheap]` or
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
- `Phase <N> regression AC` (when a regression AC outcome is the
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
````

## Honesty rule

If the session genuinely had nothing substantive to improve, the
reflection file is allowed to be short:

- "Session stats" — full block always.
- "What worked" — at least 1 bullet.
- "What didn't" — write `- None observed in this session.` if true.
- "Advice — user prompt" / "Advice — agent prompts" / "Advice — plan /
  process" — write `- None — session ran cleanly.` if true.
- "Suggested follow-up" — same.

A short, honest reflection is better than a padded one.

## Dispatch brief expected from the orchestrator

The orchestrator dispatches the reflector with a brief that includes:

- Plan-file path (e.g. `.plans/add-hello-command.md`).
- Slug (e.g. `add-hello-command`).
- Terminal Status (`Done` or `Blocked`).
- (Optional) one-line note on why this run is interesting (e.g. "two
  PLAN_WRONGs in Phase 2 — please dig").

If any of the first three fields is missing, the reflector returns a
one-line clarification request instead of guessing.

## Self-review before returning

- [ ] Read only `.plans/<slug>.md` — no other files.
- [ ] Computed all session stats from the plan file (no estimates).
- [ ] Each advice item cites a concrete plan-file location.
- [ ] No banned phrases.
- [ ] No "try harder" / "be more careful" advice.
- [ ] If session was clean, reflection is short and honest (not padded).
- [ ] Wrote exactly `.plans/<slug>-reflection.md` (no other files).
- [ ] Did not edit the plan file.
- [ ] Returned artefact summary to orchestrator.

## References

- `../plan-file-format/SKILL.md` — Status / Review log / Discoveries /
  Revision block semantics.
- `../orchestration-loop/SKILL.md` — when the orchestrator dispatches
  the reflector and how the wrap-up message links to the reflection
  file.

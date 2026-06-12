---
name: orchestration-loop
description: Use this skill when the orchestrator agent (`autonomous-builder.md`) is running the workflow. It defines the full state machine — intake, plan, approve, per-phase task loop with adaptive retry and PLAN_WRONG handling, phase checkpoints, and wrap-up — plus the dispatch wiring for the four worker subagents and the message templates the orchestrator uses to talk to the user.
---

# Orchestration Loop

The orchestrator is the only agent that runs the state machine and the only
one that writes overall plan Status, phase Status, and task `Done` /
`Blocked` / `Review failed` transitions. Other agents return data; the
orchestrator interprets and routes.

## When to use

- Loaded by the `autonomous-builder` (orchestrator) agent at the start of
  every session.
- Consulted before every state transition (`Approved` → `In progress`,
  task `Awaiting review` → `Done`, etc.) and before every subagent dispatch.

## The state machine

```
┌─────────┐
│ intake  │  Receive goal from /autonomous-build, pick slug,
└────┬────┘  create .plans/<slug>.md (Status: Planning).
     │
     ▼
┌─────────┐
│  plan   │  Dispatch planner (initial mode).
└────┬────┘  Planner sets Status: Awaiting approval, returns summary.
     │
     ▼
┌─────────┐
│ approve │  Show plan summary to user. Loop on edits/clarifications.
└────┬────┘  On approval → Status: Approved → In progress.
     │
     ▼
┌──────────────────────────────────────────────────────────────────┐
│ for each PHASE in order:                                         │
│   set phase Status: In progress                                  │
│                                                                  │
│   for each TASK in phase (honour Depends on):                    │
│     repeat (attempt = 1..3):                                     │
│       dispatch implementer(task_id, attempt, last_fail_feedback) │
│       dispatch reviewer(task_id, mode = cheap-only OR cheap+gate)│
│       parse reviewer verdict:                                    │
│         PASS                       → task Status: Done; break    │
│         PLAN_WRONG                 → goto REVISE_PLAN            │
│         FAIL && attempt<3                                        │
│              && failure_mode != prev → task Status: Review       │
│                                       failed (N/3); continue    │
│         FAIL && (attempt=3 OR                                    │
│                  failure_mode == prev) → ADAPTIVE_ESCALATE        │
│                                                                  │
│   phase-regression: dispatch reviewer to verify Phase regression │
│       AC. On FAIL: re-open last task as Awaiting review with     │
│       regression feedback; loop back to its retry block.         │
│                                                                  │
│   phase Status: Done                                             │
│   PHASE_CHECKPOINT to user (see template below).                 │
└──────────────────────────────────────────────────────────────────┘
     │
     ▼
┌──────────┐
│ wrap-up  │  overall Status: Done.
│          │  Dispatch reflector(plan_path, slug, "Done").
│          │  Summary of artefacts to user, including pointer to
│          │  `.plans/<slug>-reflection.md`.
└──────────┘

REVISE_PLAN:
  overall Status: Awaiting revision approval
  dispatch planner (revision mode) with PLAN_WRONG reason
  show ## Revision N (proposed) to user; collect approve/reject/edit
    approve → apply diff, remove revision block, Status: In progress,
              resume from first revised task
    reject  → Status: Blocked; escalate
    edit    → re-dispatch planner with the additional reason → Revision N+1

ADAPTIVE_ESCALATE:
  dispatch researcher (medium) on "why is failure_mode: <label> blocking AC #<n>?"
  if researcher's finding indicates AC/task is the problem:
    promote to PLAN_WRONG; goto REVISE_PLAN
  else:
    task Status: Blocked
    overall Status: Blocked
    escalate to user (see template below)
    dispatch reflector(plan_path, slug, "Blocked") so the failure
      produces durable advice in `.plans/<slug>-reflection.md`
```

## Dispatch wiring

The orchestrator is the only agent allowed to dispatch the planner,
implementer, reviewer, or reflector. Workers do not dispatch each other.

| Subagent       | Dispatched with                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------- |
| `planner`      | Mode (`initial` or `revision`), plan-file path, and (for revision) the triggering Review log entry.     |
| `implementer`  | Plan-file path, task ID, attempt number (1–3), and (for retries) the previous attempt's FAIL feedback.  |
| `reviewer`     | Plan-file path, task ID, and AC mode (`cheap-only` if attempt < 3 and no `[gate]` AC need running yet, or `cheap+gate` when about to mark Done). |
| `researcher`   | Question, thoroughness, expected return shape (see `../researching/SKILL.md`).                          |
| `reflector`    | Plan-file path, slug, terminal Status (`Done` or `Blocked`), optional one-line note. See `../reflecting-on-sessions/SKILL.md`. |

The orchestrator may also dispatch the researcher itself — typically when
investigating a repeated `failure_mode` before deciding `PLAN_WRONG` vs
escalate.

## Adaptive retry rule (in detail)

Fixed N=3 retries is wrong. Replace with:

1. **Attempt 1.** Implementer + reviewer (cheap-only). On FAIL, record the
   reviewer's `failure_mode:` label.
2. **Attempt 2.** Implementer + reviewer (cheap-only). On FAIL:
   - If `failure_mode` matches attempt 1 → **escalate immediately** (no
     attempt 3). Don't burn another attempt on the same wall.
   - Otherwise → continue.
3. **Attempt 3.** Implementer + reviewer (`cheap+gate` — this is the
   about-to-Done attempt). On FAIL → escalate.

Repeated `failure_mode` is the strongest signal that the *plan*, not the
*implementation*, is the problem. Treat it as a soft `PLAN_WRONG` per
`../amending-plans/SKILL.md`.

## Reviewer AC mode (cheap vs gate)

The orchestrator tells the reviewer which AC subset to run, based on
attempt context:

- **`cheap-only`** — attempts where we're not yet trying to finalise. Cuts
  review cost dramatically: a `[gate]` integration suite that takes 5 min
  doesn't run on every iteration.
- **`cheap+gate`** — the attempt that intends to mark the task `Done`.
  Reviewer runs everything. Usually attempt N when the implementer signals
  "I think this is done"; conservatively, always attempt 3.

If `[cheap]` AC fail on a `cheap+gate` attempt, the verdict is FAIL — the
reviewer doesn't need to bother running `[gate]` AC for that attempt.

## Phase checkpoint

After a phase completes (all tasks Done **and** phase regression AC passed),
the orchestrator posts a structured one-message checkpoint to the user:

```markdown
**Phase <N> done: <phase name>** ✓

- Tasks completed: <id1>, <id2>, …
- Phase regression AC: PASS
- Files touched this phase: <list, deduplicated>
- New Discoveries added: <count>

**Up next — Phase <N+1>: <name>**
- <Task id>: <name>
- <Task id>: <name>
- Phase regression AC: <one-line summary>

Continue, or any concerns? (Reply 'continue' or describe a change. Silence
for one turn = continue.)
```

Interpreting the user's reply:

- **`continue` / empty / no objection** → start next phase.
- **Substantive amendment request** (e.g. "skip Task 3.2 — that file was
  deleted last week"; "add a task to also update the changelog") → treat as
  a PLAN_WRONG-style trigger. Dispatch planner in revision mode with the
  user's request as the trigger. Run the user re-approval flow per
  `../amending-plans/SKILL.md`. Resume from the first revised task in the
  upcoming phase.
- **Question** (e.g. "what did you change in `foo.py`?") → answer
  conversationally from the Review logs and Discoveries. After answering,
  re-post the checkpoint message.

## Plan approval (initial)

After the planner returns:

```markdown
**Plan ready for approval:** `.plans/<slug>.md`

<one-paragraph executive summary from the planner>

**<P> phases, <T> tasks total.**

- **Phase 1: <name>** (<n> tasks) — <one-line summary>
- **Phase 2: <name>** (<n> tasks) — <one-line summary>
- …

Approve to start execution, or describe what you'd like changed.
```

On approval (`approve`, `yes`, `go`, similar) → Status: `Approved` → `In progress`.
On change request → dispatch planner in revision mode with the user's input
as the trigger. Repeat until approved.

## Blocked escalation template

When escalating to the user (retry exhausted, repeated failure mode that
isn't a `PLAN_WRONG`, or rejected revision):

```markdown
**🛑 Blocked on Task <id>: <name>** (Phase <P>)

**What was tried (<N> attempts):**
- Attempt 1 — `failure_mode: <label>` — <one-line summary from Review log>
- Attempt 2 — `failure_mode: <label>` — <one-line summary>
- (Attempt 3 — <…>)

**Reviewer's last feedback:**
> <verbatim quote of last FAIL block>

**Researcher's investigation (if dispatched):**
> <Answer + Caveats section>

**What I think the options are:**
1. <Option A — usually: amend the AC>
2. <Option B — usually: take this task off the plan>
3. <Option C — usually: take over manually>

Plan file: `.plans/<slug>.md`. How do you want to proceed?
```

After the user acknowledges the escalation (and regardless of which option
they pick), dispatch the reflector once with `terminal_status="Blocked"`
so the failure produces durable advice in `.plans/<slug>-reflection.md`.

## Wrap-up message template

When all phases reach `Done` and the overall plan Status is set to `Done`,
dispatch the reflector once and then post:

```markdown
**✅ Plan complete: <title>**

- Phases done: <P>
- Tasks done: <T>
- Files touched (deduplicated): <list>
- Discoveries logged: <count>

**Retrospective:** `.plans/<slug>-reflection.md`
> <one-line headline from the reflection file's "What didn't" or
>  "Suggested follow-up" section, if any; otherwise: "Session ran
>  cleanly — no follow-up suggested.">

Plan file: `.plans/<slug>.md`.
```

The reflector dispatch must happen **before** this message — the message
links into the reflection file, so the file has to exist.

## Reflector dispatch (terminal states)

Dispatch the reflector **exactly once** per session, at the moment overall
Status becomes terminal:

- On `Done`: after setting overall Status, before the wrap-up message.
- On `Blocked`: after escalating to the user (so the escalation message
  isn't delayed by the reflection write).

Brief shape (see `../reflecting-on-sessions/SKILL.md` for the full
contract):

```
plan_path: .plans/<slug>.md
slug: <kebab-case>
terminal_status: Done | Blocked
note (optional): <one-liner — e.g. "two PLAN_WRONGs in Phase 2; please dig">
```

The reflector returns an artefact summary (path written + headline
counts). Surface only the path in your user-facing message; the user
opens the file for the rest.

## Hard rules

- Never skip review. Every implementer dispatch is followed by a reviewer
  dispatch — no exceptions, no "this one's obviously fine".
- Never skip a phase checkpoint.
- Never skip reflection at terminal states. When overall Status reaches
  `Done` or `Blocked`, dispatch the reflector exactly once.
- Never silently mutate the plan. All amendments go through
  `../amending-plans/SKILL.md` and require user re-approval.
- Never edit product code. The orchestrator only reads/writes the plan file
  and dispatches subagents.
- Never let an implementer or reviewer talk to the user. Both return to
  the orchestrator; the orchestrator decides what to surface.
- Only the orchestrator writes these Status transitions: task → `Done` /
  `Blocked` / `Review failed (N/3)`; phase → `In progress` / `Done` /
  `Blocked`; overall → `Approved` / `In progress` / `Awaiting revision
  approval` / `Done` / `Blocked`.

## Pre-dispatch sanity checks

Before dispatching the implementer for attempt N:

- [ ] Task Status is `Pending` (attempt 1) or `Review failed (N-1/3)`
      (retries).
- [ ] All `Depends on:` tasks are `Done`.
- [ ] On retry: the previous attempt's reviewer FAIL block is the latest
      Review log entry (no orphan PASS in between).

Before dispatching the reviewer:

- [ ] Implementer set task Status to `Awaiting review`.
- [ ] Chose `cheap-only` or `cheap+gate` per the rule above.
- [ ] Plan file is on-disk (no in-memory drift).

## Checklist (orchestrator, every cycle)

- [ ] Plan file's overall Status reflects reality.
- [ ] Adaptive retry rule consulted before every retry decision.
- [ ] `failure_mode` of latest FAIL compared to previous before deciding.
- [ ] Reviewer's AC mode chosen explicitly.
- [ ] Phase checkpoint posted between every phase (never skip).
- [ ] No Status transitions made by any other agent.

## References

- `../plan-file-format/SKILL.md` — Status vocabulary and who-may-change-what
  table.
- `../amending-plans/SKILL.md` — PLAN_WRONG flow and revision-mode dispatch.
- `../researching/SKILL.md` — dispatching the researcher during
  ADAPTIVE_ESCALATE.
- `../reflecting-on-sessions/SKILL.md` — dispatching the reflector at
  wrap-up and Blocked.
- `../implementing-tasks/SKILL.md` — what the implementer expects in its
  dispatch brief.
- `../reviewing-acceptance-criteria/SKILL.md` — what the reviewer expects.

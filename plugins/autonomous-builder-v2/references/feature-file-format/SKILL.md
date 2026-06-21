---
name: feature-file-format
description: Use this skill whenever any autonomous-builder-v2 agent reads or writes anything under `.features/<slug>/`. It defines the canonical layout and structure for the design doc, the projected plan, the per-task ledgers, the shared knowledge base, the scorecard, and the reflection — plus the status vocabulary and the who-may-change-what rules that keep eight agents coordinated through plain markdown.
---

# Feature File Format

A v2 run is coordinated entirely through files under `.features/<slug>/` in
the **target** repo (the repo the work is happening in — not this plugin's
repo). The structure below is non-negotiable; every agent depends on it.

## When to use

- Before reading or writing the design doc, the plan, a task ledger, the
  knowledge base, the scorecard, or the reflection.
- Before changing any `**Status:**` line.

## Directory layout

```
.features/<slug>/
  <slug>-design.md      # the design — the ONLY user-approved artefact
  <slug>-plan.md        # phases/tasks/AC, projected from the approved design
  knowledge.md          # shared, list-based per-feature knowledge base (KB)
  tasks/
    <task-id>.md        # per-task ledger (implementer/tester/reviewer notes)
  scorecard.md          # one row per terminal run (appended by reflector)
  <slug>-reflection.md  # developer-facing retrospective (terminal states)
```

- **Slug:** kebab-case, derived from the goal (e.g. `add-hello-command`).
  The orchestrator picks it at intake and uses it for every dispatch.

## Status vocabulary

The **overall** Status (in the design doc header) is the single source of
truth for where the run is:

```
Design | Awaiting design approval | Design approved | In progress
       | Awaiting design revision approval | Done | Blocked
```

There is **no plan-approval status** — the design gate is the only
pre-code approval (see `../orchestration-loop/SKILL.md`, decision D7).

Phase Status (in the plan): `Not started | In progress | Done | Blocked`.
Task Status (in the plan + ledger): `Not started | In progress |
Implementation bounced (N/5) | Review failed (N/5) | Done | Blocked`.

## 1. Design doc — `<slug>-design.md`

The design is the contract the user approves. It MUST be clear enough that
the plan is a mechanical projection of it.

````markdown
# Design: <title>

**Status:** Design | Awaiting design approval | Design approved | In progress | Awaiting design revision approval | Done | Blocked
**Goal:** <one-line restatement>
**Slug:** <kebab-case>
**Created:** <YYYY-MM-DD>

## Summary
<2–4 sentences: what we're building and why.>

## Changing components
- <component> — <what changes>

## Changing / new APIs
- <signature or endpoint> — <new | changed | removed> — <why>

## Key decisions
- <decision> — <chosen option> — <trade-off / alternatives rejected>
- New libraries / tools introduced: <name + reason, or "none">

## Scope
**In scope:** <bullets.>
**Out of scope:** <bullets — so the user can judge size.>
**Rough size:** <S / M / L + one-line justification.>

## Open questions for the user
- <anything that must be resolved before approval, or "none">
````

## 2. Plan — `<slug>-plan.md`

Projected from the approved design by the designer (`plan` mode). Shown to
the user as an FYI; **not** separately approved.

````markdown
# Plan: <title>   (projected from design — FYI, not a gate)

**Design:** ./<slug>-design.md
**Generated:** <YYYY-MM-DD>

## Phase <N>: <name>
**Status:** Not started
**Definition of Done:** <one or more AC that verify the whole phase.>

### Task <N>.<M>: <name>
**Status:** Not started
**Depends on:** <task ids, or "none">
**Ledger:** ./tasks/<N>.<M>.md

**Acceptance criteria:**
- [Must] [Fast] <objective, checkable AC>
- [Should] [Full] <…>
- [Could] [Journey] <user-journey AC, exercised by the tester>
````

**AC tiers.** Priority `[Must] | [Should] | [Could]` (MoSCoW) × cadence
`[Fast] | [Full] | [Journey]`. Only `Must` failures cause FAIL/retry;
`Should` → WARN, `Could` → INFO. See `../reviewing/SKILL.md`.

## 3. Task ledger — `tasks/<task-id>.md`

The shared working memory for one task's inner loop. The implementer,
tester, and reviewer each append their own section; nobody overwrites
another agent's section. The user can read it to follow the work.

````markdown
# Task <id>: <name>

**Status:** In progress
**impl_bounces:** 0/5   **review_bounces:** 0/5

## Implementer log
- [<date> attempt <n>] Files changed:
  - `path/to/file` — <what + why>
  - Tests: `path/to/test` — <what it covers>
  - All tests green: <yes/no + how verified (command + exit code)>

## Tester log
- [<date>] Thoroughness vs AC: <assessment>
  - Tests added by tester: `path` — <why the gap mattered>
  - Verdict: tests-OK | implementation-wrong (<reason>)

## Reviewer log
- [<date> mode=<fast-only|fast+full|dod>] Verdict: PASS | FAIL | PLAN_WRONG
  - Evidence: <commands run + exit codes / AC checked>
  - Opinion: <reviewer's note on top of the ledger>
````

## 4. Knowledge base — `knowledge.md`

Shared, **list-based**, append-with-dedupe. One bullet per fact. See
`../researching/SKILL.md` for the check-first + dedupe contract.

````markdown
# Knowledge base: <slug>

<!-- One fact per line. Check before appending. Humans may prune freely. -->
- [<YYYY-MM-DD> · <agent>] <fact> — <file:line or URL>
````

## 5. Scorecard — `scorecard.md`

Appended by the reflector at every terminal state (one row per run). Fields
per `../reflecting-on-sessions/SKILL.md`.

## 6. Reflection — `<slug>-reflection.md`

Developer-facing retrospective written by the reflector at terminal states.
It is **not** fed back into the agent at runtime; it exists for the
developers to improve prompts / design / workflow. Format owned by
`../reflecting-on-sessions/SKILL.md`.

## Who may change what

| Artefact            | Writer(s)                                              |
| ------------------- | ----------------------------------------------------- |
| Design doc + Status | designer (content) · orchestrator (Status transitions)|
| Plan                | designer (initial projection + revisions)             |
| Phase Status        | orchestrator                                          |
| Task Status         | task-coordinator                                      |
| Task ledger         | implementer / tester / reviewer (own sections only)   |
| `knowledge.md`      | any agent via the researcher's append-with-dedupe     |
| Scorecard           | reflector                                             |
| Reflection          | reflector                                             |

Nobody edits another agent's ledger section. Only the orchestrator writes
overall Status; only the task-coordinator writes task Status.

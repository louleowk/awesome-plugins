---
name: plan-file-format
description: Use this skill whenever any autonomous-builder agent reads or writes a `.plans/<slug>.md` file. It defines the canonical structure (phases, tasks, Discoveries, tiered acceptance criteria, status vocabulary) and the who-may-change-what rules that keep five agents coordinated through one markdown file.
---

# Plan File Format

The plan file is the single source of truth for an autonomous-builder run.
Every agent reads and writes it; the structure below is non-negotiable.

## When to use

- Any time the planner, orchestrator, implementer, reviewer, or researcher
  touches `.plans/<slug>.md`.
- Before writing a new plan, before parsing an existing one, before appending
  to `## Discoveries`, before changing any `**Status:**` line.

## Path and slug

- Location: `.plans/<slug>.md` inside the **target** repo (the repo the work
  is happening in — not this plugin's repo).
- Slug: kebab-case, derived from the goal (e.g. `add-hello-command`,
  `rename-foobar-to-foo-bar`). Planner picks it; orchestrator uses it for
  dispatch.
- Companion file: `.plans/<slug>-reflection.md` is written by the
  `reflector` agent at the end of the session (terminal Status `Done` or
  `Blocked`). The reflection file is **not** part of the plan-file
  contract below — it has its own format owned by
  `../reflecting-on-sessions/SKILL.md`. No other agent reads or writes it.

## File skeleton

````markdown
# Plan: <title>

**Status:** Planning | Awaiting approval | Approved | In progress | Awaiting revision approval | Done | Blocked
**Goal:** <one-line restatement of what we're building>
**Slug:** <kebab-case>
**Created:** <YYYY-MM-DD>

## Context

<Background the planner gathered: repo conventions, constraints, scope
boundaries, prior art, anything the implementer and reviewer need but that
doesn't fit in a specific task block.>

## Discoveries

<!-- Append-only shared knowledge. Any agent may add lines but no one
rewrites or deletes existing lines. Format:
- [<agent> · YYYY-MM-DD] <fact> (`path/to/file.ext:Lstart-Lend`)
-->

- (empty until first discovery)

## Phase 1: <short phase name>

**Status:** Pending | In progress | Done | Blocked
**Definition of Done:**
- [ ] [Must] [Full] <plan-level check run once after the last task in this phase passes — e.g. "full test suite green", "no new lint warnings", "binary still boots">
- [ ] [Must] [Journey] (cli|api|web) <optional — exercise the running system like a real user; only allowed here, not on tasks; dispatches `tester`>
- [ ] [Should] [Full] <optional — passes if it can; failure is a warning, not a block>

### Task 1.1: <short task name>

**Status:** Pending | In progress | Awaiting review | Review failed (attempt N/3) | Done | Blocked
**Depends on:** none | Task 1.0 | Task 2.3
**Reasoning:** <Why this task exists; why it's in this position in the order.>
**Implementation notes:** <Files to touch, approach, key APIs, the planner's recommendation — not the implementer's transcript.>
**Acceptance criteria:**
- [ ] [Must]   [Fast] <fast deterministic check — file content, single unit test, lint of one file, exit-code of a fast command>
- [ ] [Must]   [Full] <slower check — full module test, integration run, behaviour observable only end-to-end>
- [ ] [Should] [Fast] <optional — useful but non-blocking; failure logged as WARN at phase checkpoint>

**Review log:**
- (empty until first attempt)

### Task 1.2: ...

## Phase 2: ...
````

## Status vocabulary

**Overall plan `**Status:**`** (one per file):

| Value                           | Meaning                                                                          | Set by                  |
| ------------------------------- | -------------------------------------------------------------------------------- | ----------------------- |
| `Planning`                      | Planner is drafting; file may be incomplete.                                     | Planner                 |
| `Awaiting approval`             | Initial plan ready; waiting for user.                                            | Planner                 |
| `Approved`                      | User approved. Orchestrator about to start execution.                            | Orchestrator            |
| `In progress`                   | A phase is currently executing.                                                  | Orchestrator            |
| `Awaiting revision approval`    | Planner produced a revision diff; waiting for user re-approval.                  | Orchestrator            |
| `Done`                          | All phases Done.                                                                 | Orchestrator            |
| `Blocked`                       | Escalated to user (retry exhausted, repeated failure mode, or rejected revision). | Orchestrator           |

**Per-phase `**Status:**`**:

| Value         | Meaning                                                          | Set by         |
| ------------- | ---------------------------------------------------------------- | -------------- |
| `Pending`     | Not yet started.                                                 | Planner        |
| `In progress` | Some task in the phase is in flight.                             | Orchestrator   |
| `Done`        | All tasks in phase Done **and** phase Definition of Done passed. | Orchestrator   |
| `Blocked`     | A task in the phase escalated; phase cannot complete.            | Orchestrator   |

**Per-task `**Status:**`**:

| Value                            | Meaning                                                              | Set by         |
| -------------------------------- | -------------------------------------------------------------------- | -------------- |
| `Pending`                        | Waiting for its turn.                                                | Planner        |
| `In progress`                    | Implementer is editing.                                              | Implementer    |
| `Awaiting review`                | Implementer finished; reviewer not yet started.                      | Implementer    |
| `Review failed (attempt N/3)`    | Reviewer FAILed; will retry.                                         | Orchestrator   |
| `Done`                           | Reviewer PASSed (including any `[Full]` AC).                         | Orchestrator   |
| `Blocked`                        | Escalated.                                                           | Orchestrator   |

## Who may change what

| Field                                | Planner (init) | Planner (revision) | Implementer | Reviewer | Orchestrator | Researcher | Tester |
| ------------------------------------ | -------------- | ------------------ | ----------- | -------- | ------------ | ---------- | -------------- |
| File creation                        | yes            | no                 | no          | no       | no           | no         | no             |
| `## Context`                         | write          | append only        | read        | read     | read         | read       | read           |
| `## Discoveries`                     | seed           | append             | append      | append   | append       | read (see researcher rule) | read (see tester rule) |
| Phase definitions                    | write          | amend affected     | read        | read     | read         | read       | read           |
| Task `Implementation notes`, `Reasoning`, `Acceptance criteria` | write | amend affected | read | read | read | read | read           |
| Phase `**Definition of Done:**`      | write          | amend affected     | read        | read     | read         | read       | read           |
| Task `**Status:**` → `In progress` / `Awaiting review` | — | — | yes | — | — | — | —              |
| Task `Review log` entries            | —              | —                  | —           | append   | —            | —          | —              |
| Task `**Status:**` → `Done` / `Blocked` / `Review failed (N/3)` | — | — | — | — | yes | — | —              |
| Phase `**Status:**`                  | initial Pending| —                  | —           | —        | yes          | —          | —              |
| Overall `**Status:**`                | initial values | —                  | —           | —        | yes          | —          | —              |
| `## Revision <N> (proposed)` block   | —              | append             | —           | —        | —            | —          | —              |

The researcher does not write to the plan file directly. Findings get into
`## Discoveries` via whichever agent dispatched the researcher.

The tester likewise does not write to the plan file directly.
It returns a structured journey log to the reviewer; the reviewer
folds it into the Review log entry and (if durable) appends a
`[reviewer · YYYY-MM-DD]` Discovery line citing the journey result.

## Acceptance criteria rules

Acceptance criteria use plain agile vocabulary so a reader who has never
touched this plugin can understand them at a glance: **MoSCoW priority**
(`Must` / `Should` / `Could`) plus a **cadence** (`Fast` / `Full` /
`Journey`) describing when the check runs.

### Grammar (every AC, no exceptions)

```
- [ ] [<priority>] [<cadence>] <concrete command, file, or observable behaviour>
```

- `<priority>` ∈ `Must` | `Should` | `Could`. **Required.**
- `<cadence>` ∈ `Fast` | `Full` | `Journey`. **Required.**
- No defaults. Untagged or single-tagged AC → reviewer rejects as
  `PLAN_WRONG` with trigger `mis-tagged AC`.
- `Won't` is **not** an AC tag. Use it in `## Context` to declare
  scope-out items: "Won't: support IE11."

### Priority semantics (MoSCoW)

| Priority  | If the check fails on a single AC | Effect on the task / phase verdict |
| --------- | --------------------------------- | ---------------------------------- |
| `Must`    | per-AC verdict: **FAIL**          | task FAIL (or, in Definition of Done, phase FAIL) |
| `Should`  | per-AC verdict: **WARN**          | logged in Review log, surfaced at phase checkpoint, **does not** block the task or phase |
| `Could`   | per-AC verdict: **INFO**          | logged in Review log, **does not** surface unless the user asks |

Only `Must`-priority failures produce a `failure_mode:` label.
`Should` / `Could` failures never trigger adaptive retry, never
trigger PLAN_WRONG, and never block a Done transition.

### Cadence semantics (when each runs)

| Cadence    | Per-attempt review (`fast-only` mode) | Pre-Done review (`fast+full` mode) | Phase Definition of Done (`dod` mode) |
| ---------- | ------------------------------------- | ---------------------------------- | ------------------------------------- |
| `[Fast]`   | runs                                  | runs                               | runs (rare; usually only `Full`)      |
| `[Full]`   | SKIPPED                               | runs                               | runs                                  |
| `[Journey]`| not allowed at task level             | not allowed at task level          | runs — dispatches `tester` per surface (`cli` / `api` / `web`) |

- `[Fast]` = runs in seconds, deterministic, no external services,
  safe to run on every implementer attempt. Examples: a `grep` content
  assertion, a single unit test, a one-file lint, a
  `python -c "import json; json.load(...)"`-style check.
- `[Full]` = slow, expensive, or has setup cost; runs only when the
  attempt is finalising or as part of phase Definition of Done.
  Examples: full module test suite, full integration run, a build
  that takes minutes.
- `[Journey]` = exercises the running system like a real user.
  Allowed ONLY in a phase's `**Definition of Done:**` block —
  never in a task's `**Acceptance criteria:**`. Reviewer dispatches
  the `tester` subagent to verify it on one of three surfaces:
  - `(cli)` — a binary on PATH or at a Discoveries-recorded path,
    observed via stdout / stderr / exit code.
  - `(api)` — an HTTP base URL, observed via status / headers /
    response body / side-effect verification.
  - `(web)` — a browser app at a URL, observed via Playwright
    user-facing locators / screenshots / console-error budget.

  **Every `[Journey]` AC body MUST begin with a `(cli|api|web)`
  surface prefix.** A missing or wrong prefix → reviewer rejects
  as `PLAN_WRONG` with trigger `mis-tagged AC`.

  Examples:
  ```
  - [ ] [Must] [Journey] (cli) `myapp init <dir>` creates the dir with `config.toml`; running `myapp init` again on the same dir exits non-zero with a clear "already initialised" message.
  - [ ] [Must] [Journey] (api) POST /users with `{email, password}` returns 201 and a `Location: /users/<id>` header; a follow-up `GET /users/<id>` returns the same email.
  - [ ] [Must] [Journey] (web) New user signs up at `/signup` and reaches `/dashboard` with a "Welcome" banner; no console errors; no 5xx.
  ```

A `[Journey]` AC under a task → reviewer rejects as `PLAN_WRONG`
with trigger `mis-placed AC`.

### AC body rules

- **Every AC must name a concrete command, file, or observable
  behaviour.** Banned phrasings (reviewer rejects as `PLAN_WRONG`,
  trigger `impossible AC`):
  "looks good", "is clean", "works correctly", "code is
  well-structured", "no issues", "passes review", "follows best
  practices".
- **AC must be checkable with shared knowledge only** — i.e. an
  agent that has read `## Context` and `## Discoveries` (but not the
  implementer's scratch) can verify it. If an AC requires private
  implementer reasoning to evaluate, it is mis-written.

### Definition of Done (per phase)

Every phase must have **≥1 `[Must] [Full]` AC** in its
`**Definition of Done:**` block — the "we didn't break the rest of
the system" regression check, run once after the last task in the
phase passes.

A phase MAY include `[Journey]` AC in its Definition of Done. If it
does, the plan must also include a first "Environment" phase whose
Definition of Done establishes the runnable app (one-command
bring-up + health check + seed data); see
`../planning-tasks/SKILL.md` for the convention. The reviewer
rejects a plan with `[Journey]` AC but no Environment phase as
`PLAN_WRONG` with trigger `missing-environment-phase`.

### Mixed-vocabulary rejection

A plan that mixes the legacy `[cheap]` / `[gate]` syntax with the
new `[Priority] [Cadence]` syntax in the same file is invalid.
Reviewer rejects on first encounter as `PLAN_WRONG` with trigger
`mixed-vocabulary`. Plans currently in flight finish on whichever
vocabulary they started with.

## Append-only `## Discoveries`

The Discoveries section is the project's growing legacy map. It compresses
repeat exploration cost — instead of every agent re-searching for "where is
the test config", they read one line in Discoveries.

- **Append-only.** Never rewrite or delete a line.
- **One fact per line**, with the agent and date prefix and a file:line
  reference where possible:
  ```
  - [researcher · 2026-06-10] Slash commands are loaded from `commands/` via `plugin.json`'s `commands` array (`plugins/plugin-creator/skills/writing-commands/SKILL.md:42-50`).
  - [implementer · 2026-06-10] `frontmatter` PyPI library not installed; use yaml-parsing fallback when verifying AC.
  ```
- **Discoveries take precedence over assumptions.** When an agent's prior
  belief conflicts with a Discovery, the Discovery wins; the agent appends a
  new line correcting itself.

## Plan revision blocks

When the orchestrator dispatches the planner in revision mode (triggered by
a reviewer `PLAN_WRONG` verdict, or by user input at a phase checkpoint),
the planner appends a block at the bottom of the file:

````markdown
## Revision 1 (proposed)

**Triggered by:** Task 2.3 PLAN_WRONG — reviewer reason: <one-liner>
**Proposed changes:**
- Task 2.3: <before → after summary>
- Task 2.4 (new): <name + AC>
- Task 3.1: <before → after summary>

<Diff or full replacement of affected task blocks. AC use the `[Priority]
[Cadence]` grammar above. Tasks not listed are unchanged.>
````

The orchestrator shows this block to the user; on approval it applies the
changes in place and sets overall Status back to `In progress`. On rejection
it sets overall Status to `Blocked` and escalates.

## Checklist before writing or accepting a plan file

- [ ] Has a top-level `# Plan: <title>` and the four header fields.
- [ ] Has `## Context` and `## Discoveries`.
- [ ] At least one `## Phase N:` block.
- [ ] Each phase has `**Definition of Done:**` with ≥1 `[Must] [Full]` AC.
- [ ] Each task has Status, Reasoning, Implementation notes, ≥2 AC, and an
      empty Review log.
- [ ] Every AC is tagged with **both** a priority
      (`[Must]` / `[Should]` / `[Could]`) and a cadence
      (`[Fast]` / `[Full]` / `[Journey]`) and names a concrete
      command / file / behaviour.
- [ ] Every `[Journey]` AC body begins with a `(cli)`, `(api)`,
      or `(web)` surface prefix.
- [ ] No `[Journey]` AC at the task level (only inside Definition of Done).
- [ ] If any phase's Definition of Done has a `[Journey]` AC, an
      "Environment" phase exists earlier whose DoD establishes the
      runnable app.
- [ ] No mix of legacy `[cheap]` / `[gate]` syntax and new
      `[Priority] [Cadence]` syntax in the same file.
- [ ] Status values use the exact vocabulary above (no free-text variants).

## References

- `../planning-tasks/SKILL.md` — how the planner produces this file.
- `../amending-plans/SKILL.md` — revision mode and `PLAN_WRONG` flow.
- `../orchestration-loop/SKILL.md` — who transitions which status when.

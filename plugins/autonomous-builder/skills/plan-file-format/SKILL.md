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
**Phase regression AC:**
- [ ] [gate] <plan-level check run once after the last task in this phase passes — e.g. "full test suite green", "no new lint warnings", "binary still boots">

### Task 1.1: <short task name>

**Status:** Pending | In progress | Awaiting review | Review failed (attempt N/3) | Done | Blocked
**Depends on:** none | Task 1.0 | Task 2.3
**Reasoning:** <Why this task exists; why it's in this position in the order.>
**Implementation notes:** <Files to touch, approach, key APIs, the planner's recommendation — not the implementer's transcript.>
**Acceptance criteria:**
- [ ] [cheap] <fast, deterministic check — file content, single unit test, lint of one file, exit-code of a fast command>
- [ ] [gate]  <slower check — full module test, integration run, behaviour observable only end-to-end>

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
| `Done`        | All tasks in phase Done **and** phase regression AC passed.      | Orchestrator   |
| `Blocked`     | A task in the phase escalated; phase cannot complete.            | Orchestrator   |

**Per-task `**Status:**`**:

| Value                            | Meaning                                                              | Set by         |
| -------------------------------- | -------------------------------------------------------------------- | -------------- |
| `Pending`                        | Waiting for its turn.                                                | Planner        |
| `In progress`                    | Implementer is editing.                                              | Implementer    |
| `Awaiting review`                | Implementer finished; reviewer not yet started.                      | Implementer    |
| `Review failed (attempt N/3)`    | Reviewer FAILed; will retry.                                         | Orchestrator   |
| `Done`                           | Reviewer PASSed (including any `[gate]` AC).                         | Orchestrator   |
| `Blocked`                        | Escalated.                                                           | Orchestrator   |

## Who may change what

| Field                                | Planner (init) | Planner (revision) | Implementer | Reviewer | Orchestrator | Researcher |
| ------------------------------------ | -------------- | ------------------ | ----------- | -------- | ------------ | ---------- |
| File creation                        | yes            | no                 | no          | no       | no           | no         |
| `## Context`                         | write          | append only        | read        | read     | read         | read       |
| `## Discoveries`                     | seed           | append             | append      | append   | append       | read (see researcher rule) |
| Phase definitions                    | write          | amend affected     | read        | read     | read         | read       |
| Task `Implementation notes`, `Reasoning`, `Acceptance criteria` | write | amend affected | read | read | read | read |
| Task `**Status:**` → `In progress` / `Awaiting review` | — | — | yes | — | — | — |
| Task `Review log` entries            | —              | —                  | —           | append   | —            | —          |
| Task `**Status:**` → `Done` / `Blocked` / `Review failed (N/3)` | — | — | — | — | yes | — |
| Phase `**Status:**`                  | initial Pending| —                  | —           | —        | yes          | —          |
| Overall `**Status:**`                | initial values | —                  | —           | —        | yes          | —          |
| `## Revision <N> (proposed)` block   | —              | append             | —           | —        | —            | —          |

The researcher does not write to the plan file directly. Findings get into
`## Discoveries` via whichever agent dispatched the researcher.

## Acceptance criteria rules

- **Every AC must be tagged `[cheap]` or `[gate]`.** Untagged AC is invalid.
  Reviewer must refuse to evaluate it and emit `PLAN_WRONG` with reason
  "AC not tiered".
- **`[cheap]`** = runs in seconds, deterministic, no external services, safe
  to run every attempt. Examples: a `Read` assertion, a single unit test, a
  one-file lint, a `python -c "import json; json.load(...)"`-style check, a
  grep that should/shouldn't match.
- **`[gate]`** = slow, expensive, or has setup cost; runs only on the attempt
  that intends to mark Done. Examples: full module test suite, integration
  run, a build that takes minutes, an end-to-end behaviour check.
- **Every AC must name a concrete command, file, or observable behaviour.**
  Banned phrasings (reviewer must reject these as `PLAN_WRONG`):
  "looks good", "is clean", "works correctly", "code is well-structured",
  "no issues", "passes review", "follows best practices".
- **Every phase must have ≥1 `[gate]` phase-regression AC** under
  `**Phase regression AC:**`. This is the "we didn't break the rest of the
  system" check, run once per phase, not per task.
- **AC must be checkable with shared knowledge only** — i.e. an agent that
  has read `## Context` and `## Discoveries` (but not the implementer's
  scratch) can verify it. If an AC requires private implementer reasoning
  to evaluate, it is mis-written.

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

<Diff or full replacement of affected task blocks. Tasks not listed are unchanged.>
````

The orchestrator shows this block to the user; on approval it applies the
changes in place and sets overall Status back to `In progress`. On rejection
it sets overall Status to `Blocked` and escalates.

## Checklist before writing or accepting a plan file

- [ ] Has a top-level `# Plan: <title>` and the four header fields.
- [ ] Has `## Context` and `## Discoveries`.
- [ ] At least one `## Phase N:` block.
- [ ] Each phase has `**Phase regression AC:**` with ≥1 `[gate]` AC.
- [ ] Each task has Status, Reasoning, Implementation notes, ≥2 AC, and an
      empty Review log.
- [ ] Every AC is tagged `[cheap]` or `[gate]` and names a concrete
      command / file / behaviour.
- [ ] Status values use the exact vocabulary above (no free-text variants).

## References

- `../planning-tasks/SKILL.md` — how the planner produces this file.
- `../amending-plans/SKILL.md` — revision mode and `PLAN_WRONG` flow.
- `../orchestration-loop/SKILL.md` — who transitions which status when.

---
name: reflecting-on-sessions
description: Use this skill when the reflector agent runs at a terminal state (Done or Blocked) in autonomous-builder-v2. Reflection is an OFFLINE signal for the developers (prompt tuning, better design, workflow fixes) — it is NOT fed back to the agent at runtime and there is no memory layer. The reflector writes a developer-facing retrospective and appends one row to the per-feature scorecard.
---

# Reflecting on Sessions

The reflector runs once at a terminal Status (`Done` or `Blocked`),
dispatched by the orchestrator. Its output is **for the developers** who
maintain these agents — it is read by humans to improve prompts, designs, and
the workflow. It is **not** fed back into the running agent, and there is **no
cross-session memory layer** (Decision D5).

The reflector is read-only on every file except its own two outputs: the
reflection and the scorecard. It never edits product code, the design, the
plan, or any ledger; it never talks to the user.

## Inputs

- The design doc, the plan, every task ledger under `tasks/`, and
  `knowledge.md`.
- The terminal Status and any orchestrator note.

## Output 1 — the retrospective

Write `.features/<slug>/<slug>-reflection.md`:

```markdown
# Reflection: <slug>   (<Done|Blocked>, <date>)

## What happened
<2–4 sentences: the goal, the outcome, where time/retries went.>

## Blameless 5-Whys (per notable failure)
- Symptom: <what failed — cite the ledger>
  1. Why? …  2. Why? …  3. Why? …  4. Why? …  5. Why? …
  - **Root cause:** <a MISSING MECHANISM, never "the agent should try harder">
  - **Proposed developer fix:** <prompt change / design-skill change /
    workflow change> — checkable from a future run by: <how we'd know it worked>

## Patterns worth a developer's attention
- <recurring friction across tasks/phases>

## What worked (keep)
- <mechanisms that paid off>
```

The root cause of every failure must be a **missing mechanism** the
developers can install (a check, a clearer AC rule, a budget tweak), not an
exhortation. The proposed fix must be verifiable from a future run.

## Output 2 — the scorecard row

Append one row to `.features/<slug>/scorecard.md` (create with a header if
absent). Fields (all derivable from the plan + ledgers):

| Field                   | Source                                            |
| ----------------------- | ------------------------------------------------- |
| `slug`, `date`          | run identity                                      |
| `terminal_status`       | Done / Blocked                                    |
| `phases`, `tasks`       | plan                                              |
| `tasks_pass_first_try`  | ledgers (review_bounces == 0 and impl_bounces == 0)|
| `total_impl_bounces`    | sum across ledgers                                |
| `total_review_bounces`  | sum across ledgers                                |
| `escalations`           | count of tasks that returned ESCALATE             |
| `design_revisions`      | count of design-revision cycles                   |
| `plan_revisions`        | count of plan-revision cycles                     |
| `human_touchpoints`     | design approval + checkpoints + answered questions|
| `researcher_dispatches` | count from ledgers / KB authorship                |
| `kb_facts_added`        | new lines in knowledge.md this run                |
| `wall_to_terminal`      | rough elapsed / turn count                        |

These accumulate so the deferred strategic questions (success metric,
highest-leverage lever, approval-load calibration) become answerable from
real data after a dozen-ish features. The reflector does not interpret the
numbers — it records them.

## Guardrails

- **Offline only.** Nothing here is promoted to a runtime store or fed back
  to the agent. The audience is the developers.
- **Read-only except the two outputs.**
- **Blameless.** Root causes are missing mechanisms, not effort.

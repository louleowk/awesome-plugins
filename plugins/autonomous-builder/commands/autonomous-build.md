---
description: Plan, implement, and review a multi-step change autonomously. Drafts a phased plan with acceptance criteria, gets your approval, then executes task-by-task with per-task review.
argument-hint: "<goal — e.g. 'add a /hello slash command to plugin-creator' or 'rename fooBar to foo_bar across the codebase'>"
---

The user wants the **autonomous-builder** plugin to plan and execute a multi-step
piece of work. The goal they typed is:

$ARGUMENTS

Invoke the `autonomous-builder` agent (the orchestrator) and pass the goal
verbatim. Do not start any implementation work yourself in this turn — the
orchestrator owns the entire intake → plan → approve → per-phase execution →
wrap-up flow, including:

- Dispatching the `planner` subagent to draft `.plans/<slug>.md`.
- Presenting the plan summary back to the user for approval before any code is
  written.
- Looping per-phase through `implementer` and `reviewer` subagents with the
  three-verdict (PASS / FAIL / PLAN_WRONG) protocol, adaptive retry, plan
  revisions, and per-phase checkpoints.

If the goal is empty or trivially unclear (one or two words with no actionable
verb), ask the user one focused clarifying question before invoking the
orchestrator. Otherwise hand off immediately.

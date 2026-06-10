---
name: autonomous-builder
description: Overview skill for the autonomous-builder plugin. Use this when the user asks how the plugin works, which agent does what, when to use it vs. asking Claude directly, or how the planner / implementer / reviewer / researcher / orchestrator fit together.
---

# Autonomous Builder

This plugin plans, implements, and reviews a multi-step change autonomously.
A single **orchestrator** agent drives the workflow; four other agents do
the actual work as subagents.

## When to use

- The user gives a multi-step goal that is too big for a single edit
  ("add a `/hello` slash command and update the manifest", "rename function
  X across the codebase", "extract module Y into its own package").
- The user wants Claude to **plan first, get approval, then execute** rather
  than start editing immediately.
- The work is in unfamiliar or legacy code where it's easy to drift, and
  having a per-task reviewer plus an append-only Discoveries log is worth the
  overhead.
- Trigger phrases: "build this autonomously", "plan then implement",
  "do this step by step with review", "follow a plan to do X", and the
  `/autonomous-build <goal>` slash command.

## When NOT to use

- A single-file edit Claude can do directly.
- Exploratory / conversational questions ("how does X work?").
- Cases where the user wants tight per-step control — this plugin only
  checkpoints between phases, not between tasks.

## Agents and dispatch graph

| Agent                  | Role                                                  | Dispatched by                                            |
| ---------------------- | ----------------------------------------------------- | -------------------------------------------------------- |
| `autonomous-builder`   | Orchestrator. Owns the state machine. Only writer of overall plan status. | The slash command (entry point).                         |
| `planner`              | Drafts initial plan; amends plan on `PLAN_WRONG`.     | Orchestrator only.                                       |
| `implementer`          | Executes one task per call. Edits product code.       | Orchestrator only.                                       |
| `reviewer`             | Verifies a task against its acceptance criteria.      | Orchestrator only.                                       |
| `researcher`           | Read-only exploration / multi-file search.            | Any of the four above (incl. orchestrator). Cannot dispatch anything. |

The four workers inherit all tools. The researcher is restricted to read-only
tools (Read, Grep, Glob, WebFetch) — that's its whole purpose.

## Skills and where they're loaded

| Skill                              | Loaded by                                                                            |
| ---------------------------------- | ------------------------------------------------------------------------------------ |
| `autonomous-builder` (this)        | Orchestrator (overview / dispatch graph).                                            |
| `plan-file-format`                 | All five agents (shared contract).                                                   |
| `planning-tasks`                   | Planner.                                                                             |
| `amending-plans`                   | Planner, reviewer, orchestrator.                                                     |
| `orchestration-loop`               | Orchestrator.                                                                        |
| `implementing-tasks`               | Implementer.                                                                         |
| `reviewing-acceptance-criteria`    | Reviewer.                                                                            |
| `researching`                      | All five agents (caller contract + researcher's own rules).                          |

## Workflow at a glance

1. `intake` — orchestrator receives the goal, picks a slug.
2. `plan` — dispatches planner (initial mode) → writes `.plans/<slug>.md`
   grouped into phases, with tiered (`[cheap]` / `[gate]`) AC per task and
   `[gate]` regression AC per phase.
3. `approve` — orchestrator shows the plan to the user and negotiates until
   approved.
4. For each phase, for each task: implementer → reviewer → one of
   `PASS` / `FAIL` (retry, up to 3, with adaptive early-escalate on repeated
   failure mode) / `PLAN_WRONG` (planner-revision-mode → user re-approves
   the diff → resume).
5. After the last task in a phase: reviewer verifies the phase's regression
   AC; orchestrator posts a one-line phase summary and waits briefly for
   user objection before starting the next phase.
6. `wrap-up` — overall Status=Done; summary of artefacts.

## Plan file location

Plans live in `.plans/<slug>.md` inside the **target** repo (not this plugin's
repo). The plan file is the single source of truth — every agent reads and
writes it according to the `plan-file-format` skill's who-may-change-what
table.

## References

- `../plan-file-format/SKILL.md` — the canonical plan-file spec.
- `../orchestration-loop/SKILL.md` — the full state machine.
- `../planning-tasks/SKILL.md` — how the planner decomposes goals.
- `../amending-plans/SKILL.md` — `PLAN_WRONG` flow and planner revision mode.
- `../implementing-tasks/SKILL.md` — implementer per-attempt protocol.
- `../reviewing-acceptance-criteria/SKILL.md` — reviewer protocol.
- `../researching/SKILL.md` — when and how to dispatch the researcher.

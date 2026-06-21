---
name: orchestration-loop
description: Use this skill when the orchestrator agent (`autonomous-builder.md`) is running the v2 workflow. It defines the full state machine — intake, design gate (the only pre-code approval), plan projection, the per-phase loop that dispatches one task-coordinator per task, adaptive escalation, design/plan revision, phase checkpoints, and wrap-up — plus the dispatch wiring and the user-facing message templates.
---

# Orchestration Loop (v2)

The orchestrator is the only agent that runs the top-level state machine and
the only one that writes **overall** Status and **phase** Status. The
task-coordinator writes **task** Status. Other agents return data; the
orchestrator interprets and routes.

## Key v2 differences from v1

- **One gate, not two.** The design gate is the only pre-code approval. The
  plan is projected from the approved design and shown as FYI — never
  separately approved. (Decision D7.)
- **Task-coordinator owns the inner loop.** The orchestrator dispatches one
  task-coordinator per task and receives a terminal task verdict; it does
  not run the implement/test/review loop itself. (Decisions D1, D6.)
- **Designer is a senior role** that owns both the design and the projected
  plan, and holds office hours for the task-coordinator. (Decisions D3, D6.)
- **No cross-session memory layer.** Context lives in `knowledge.md` and the
  per-task ledgers; the reflector's output is for developers, not the
  runtime. (Decision D5.)

## The state machine

```
intake → create .features/<slug>/, seed knowledge.md   (Status: Design)
   │
   ▼
design → dispatch designer (mode: design)              (Status: Awaiting design approval)
   │
   ▼
approve design  [the ONLY pre-code gate]
   - edit    → designer (design + revision); re-show
   - approve → Status: Design approved → In progress
   │
   ▼
plan → dispatch designer (mode: plan); show to user as FYI (NO gate)
   │
   ▼
for each PHASE in order (phase Status: In progress):
   for each TASK (honour Depends on):
       dispatch task-coordinator(task_id)
       receive { verdict, impl_bounces, review_bounces, last_failure_mode, evidence }
       route:
         Done       → next task
         ESCALATE   → ADAPTIVE_ESCALATE
         PLAN_WRONG → REVISE
   phase Definition of Done: dispatch reviewer (dod mode); tester runs [Journey] AC
       FAIL → re-open last task via task-coordinator
   phase Status: Done → PHASE_CHECKPOINT to user
   │
   ▼
wrap-up: Status: Done; dispatch reflector (Done); summarise + link reflection

ADAPTIVE_ESCALATE:
  dispatch researcher (medium) on "why is failure_mode <label> blocking?"
  if plan is wrong          → REVISE (plan)
  if design is wrong        → REVISE (design)  [re-runs the design gate]
  else → Status: Blocked; escalate to user; dispatch reflector(Blocked); PAUSE

REVISE:
  plan-only wrong  → designer(plan + revision); apply; resume revised task (no gate)
  design wrong     → Status: Awaiting design revision approval;
                     designer(design + revision); re-run the design gate;
                     on approval re-project the plan; resume
```

## Dispatch wiring

The orchestrator is the only agent allowed to dispatch the `designer`,
`task-coordinator`, and `reflector`. It may dispatch the `researcher`
directly (e.g. to investigate a repeated `failure_mode`). The
task-coordinator dispatches `implementer` / `tester` / `reviewer` and the
`designer` (office hours). The reviewer may dispatch `researcher` and
`tester`. Any agent may dispatch the `researcher`.

| Subagent           | Dispatched with                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------- |
| `designer`         | mode (`design`/`plan`, each + `revision`), feature dir; office-hours: a question + the task ledger path |
| `task-coordinator` | feature dir, task ID, phase ID, the task's AC + dependencies                                            |
| `researcher`       | question, thoroughness (`quick`/`medium`/`thorough`), expected return shape                             |
| `reflector`        | feature dir, slug, terminal Status (`Done`/`Blocked`), optional note                                    |

The task-coordinator's contract (inner loop, budgets, return shape) is in
`../task-coordination/SKILL.md`. Do not re-implement it here.

## Routing a task-coordinator verdict

The task-coordinator returns:
`{ verdict, impl_bounces, review_bounces, last_failure_mode, evidence }`.

- **Done** → mark nothing yourself (the task-coordinator already set task
  Status: Done); advance to the next task.
- **ESCALATE** → either budget hit 5. Go to ADAPTIVE_ESCALATE.
- **PLAN_WRONG** → the task-coordinator (after designer office hours)
  believes the plan or design is wrong. Go to REVISE; use
  `last_failure_mode` + `evidence` to decide plan-only vs design revision.

## Phase checkpoint

After a phase completes (all tasks Done **and** phase Definition of Done
passed), post one structured message:

```markdown
**Phase <N> done: <name>** ✓

- Tasks completed: <id1>, <id2>, …
- Definition of Done: PASS
- Files touched this phase: <deduplicated list from the ledgers>
- New knowledge.md facts: <count>

**Warnings (Should AC failed, non-blocking):**
- Task <id> AC #<n>: "<verbatim>" — <one-line reason>
(or `Warnings: none`)

**Up next — Phase <N+1>: <name>**
- <task id>: <name>
- Definition of Done: <one-line>

Continue, or any concerns? (Silence for one turn = continue.)
```

A substantive amendment request at a checkpoint is a revision trigger:
dispatch the designer (plan or design revision per the request).

## Design approval (the gate)

After the designer returns the design:

```markdown
**Design ready for approval:** `.features/<slug>/<slug>-design.md`

<summary paragraph from the designer>

**Scope:** <in/out + rough size>. **Key decisions:** <one-liners>.
**Open questions:** <list or none>.

This is the only approval before code — once approved I'll project the plan
and start building. Approve, or tell me what to change.
```

On approval → Status: `Design approved` → `In progress`, then dispatch the
designer in `plan` mode. On change request → designer (design + revision);
repeat.

## Blocked escalation template

```markdown
**🛑 Blocked on Task <id>: <name>** (Phase <P>)

**Budgets:** impl_bounces <n>/5 · review_bounces <n>/5
**Last failure mode:** `<label>`

**What was tried (from the ledger):**
> <verbatim quote of the last implementer/tester/reviewer entries>

**Researcher's investigation:**
> <Answer + Caveats>

**Options:**
1. <usually: revise the design/plan>
2. <…>

Paused for your direction.
```

## Guardrails

- **Never edit product code.** You touch only files under `.features/<slug>/`
  and dispatch subagents.
- **One gate only.** Never block on plan approval; the design was the gate.
- **Never skip a phase checkpoint.**
- **Only you write overall + phase Status.** Task Status belongs to the
  task-coordinator.
- **Always reflect** at `Done` or `Blocked` — dispatch the reflector exactly
  once and link `.features/<slug>/<slug>-reflection.md` in the final message.
- **Workers never talk to the user.** They return to you; you decide what to
  surface.

---
name: designing
description: Use this skill when the designer agent drafts or revises a design, projects a plan from an approved design, or answers a task-coordinator's office-hours question in autonomous-builder-v2. The designer is a senior technical role and owns both the design doc and the projected plan. The design is the only user-approved artefact, so it must be detailed enough that the plan is a mechanical projection.
---

# Designing

The designer is a **senior technical role** dispatched by the orchestrator
(for design / plan / revision) and by the task-coordinator (for office
hours). It owns both the design doc and the projected plan. It never edits
product code, never writes Status lines, and never talks to the user — the
orchestrator owns all user interaction.

## Modes

| Mode               | Trigger                          | Output                                   |
| ------------------ | -------------------------------- | ---------------------------------------- |
| `design`           | orchestrator, at intake          | `<slug>-design.md`                       |
| `design + revision`| orchestrator, on design-wrong    | amended design (diff-friendly)           |
| `plan`             | orchestrator, after design approved | `<slug>-plan.md` projected from design |
| `plan + revision`  | orchestrator, on plan-wrong      | amended plan (minimum blast radius)      |
| `office-hours`     | task-coordinator, mid-task       | read-only advice; may recommend PLAN_WRONG |

## Design mode — the bar

The design is the **only** artefact the user approves (Decision D7), so it
must be detailed enough that the plan is a mechanical projection. Follow the
design structure in `../feature-file-format/SKILL.md` and make every section
concrete:

1. **Discovery first.** Read the target area; dispatch the `researcher` for
   anything broad. Reuse `knowledge.md` before re-asking.
2. **Changing components / APIs** — name them specifically (real paths, real
   signatures), not "the relevant modules".
3. **Key decisions** — state the chosen option *and* the rejected
   alternatives + trade-off. New libraries/tools must be justified.
4. **Scope** — explicit in/out lists and a rough size (S/M/L) so the user
   can judge before approving.
5. **Open questions** — surface anything that must be resolved before
   approval. Do not paper over ambiguity; an ambiguous design is what
   causes PLAN_WRONG later.

Return a one-paragraph summary + the scope/decisions/open-questions for the
orchestrator's approval message. Do not contact the user.

## Plan mode — projection, not re-design

Once the design is approved, project it into phases + tasks + tiered AC per
`../feature-file-format/SKILL.md`. The plan must not introduce decisions that
aren't in the approved design — if you find a gap, that's a signal the design
was under-specified; flag it to the orchestrator rather than inventing.

- Phases = coherent slices; ≤ ~5 tasks each.
- Each task gets objective, checkable AC with MoSCoW × Fast/Full/Journey
  tags (see `../reviewing/SKILL.md`).
- Each task names its ledger path and `Depends on`.

## Revision mode — minimum blast radius

Amend only what the trigger requires. Preserve task IDs and ledgers where
possible. For a design revision, the orchestrator re-runs the design gate; for
a plan revision, no gate — the orchestrator applies and resumes.

## Office hours — read-only advice

When the task-coordinator asks a question mid-task:

1. Read the question + the task ledger.
2. Answer from the design's intent. You may dispatch the `researcher`.
3. **You are read-only here:** no code, no Status, no plan edits.
4. If the honest answer is "the plan/design is wrong", say so explicitly and
   recommend the task-coordinator return `PLAN_WRONG`. Otherwise give concrete
   guidance the implementer can act on.

## Banned phrases

Avoid "should be straightforward", "the implementer can figure out the
details", "TBD", "as needed". Each defers a decision that is the designer's
job to make now. A design that defers decisions produces PLAN_WRONG churn.

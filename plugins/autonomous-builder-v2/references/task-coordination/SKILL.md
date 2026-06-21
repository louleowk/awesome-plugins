---
name: task-coordination
description: Use this skill when the task-coordinator agent is running one task's inner loop. It defines the implementer -> tester -> reviewer micro-loop, the two independent retry budgets (impl_bounces and review_bounces, 5 each), the implementer-owns-green-tests contract, the tester's add-don't-bounce rule, designer office hours, subagent session reuse, the per-task ledger, and the verdict the task-coordinator returns to the orchestrator.
---

# Task Coordination (the inner loop)

The task-coordinator owns exactly **one task**. It is dispatched by the
orchestrator, runs the implement → test → review micro-loop, writes the
**task** Status, and returns a terminal verdict. It never talks to the user
and never edits product code itself.

## When to use

- Loaded by the `task-coordinator` agent at the start of every dispatch.
- Consulted before each subagent dispatch and before returning to the
  orchestrator.

## Setup

1. Read the task block from `<slug>-plan.md` (AC + `Depends on`).
2. Create the ledger `tasks/<task-id>.md` per
   `../feature-file-format/SKILL.md` (or open it if re-opened).
3. Initialise budgets: `impl_bounces = 0`, `review_bounces = 0` (each max 5).
4. Set task Status: `In progress`.

## The micro-loop

```
loop:
  a. IMPLEMENTER  (reuse session if one exists for this task)
     - writes product code AND tests for its own changes
     - MUST get all tests green before returning (command + exit code in ledger)
     - appends Implementer log: files changed + why + green proof
  b. TESTER  (reuse session if one exists)
     - inspects test THOROUGHNESS vs the AC
     - ADDS any missing tests itself (does NOT bounce for simple gaps)
     - appends Tester log
     [?] tester verdict:
         implementation-wrong → impl_bounces++ ; ledger; 
                                 if impl_bounces == 5 → return ESCALATE
                                 else → goto a (implementer)
         tests-OK             → continue
  c. REVIEWER  (reuse session if one exists)
     - reviews against AC + the whole ledger
     - mode = fast-only (early) or fast+full (about-to-Done attempt)
     - appends Reviewer log: verdict + evidence + opinion
     [?] reviewer verdict:
         PASS       → task Status: Done ; return DONE
         FAIL       → review_bounces++ ;
                      if review_bounces == 5 → return ESCALATE
                      else → goto a (implementer) with the FAIL feedback
         PLAN_WRONG → goto OFFICE_HOURS
```

## Two independent budgets (Decision D8)

- `impl_bounces` — incremented when the **tester** finds the implementation
  wrong. Max 5.
- `review_bounces` — incremented when the **reviewer** returns FAIL. Max 5.

They are counted **separately**. Either reaching 5 returns `ESCALATE` to the
orchestrator. Do not collapse them into one counter — the split tells the
orchestrator (and the reflector) whether the task died on implementation
correctness or on review quality.

## Implementer owns green (Decision D2)

- The **implementer** writes product code **and** the tests for its own
  changes, and must make **all tests pass** before filing for review. If it
  can't get them green, that is an implementer result, not a tester bounce.
- The **tester** does not re-run a red suite as its main job; it inspects
  whether the (green) tests are *thorough enough* for the AC, and **adds
  missing tests itself**. It bounces to the implementer **only when the
  implementation is wrong** — never for a test it could simply add.

## Designer office hours (Decision D6)

```
OFFICE_HOURS:
  dispatch designer(office-hours, question, ledger_path)
  designer answers read-only (no status writes, no code, no plan edits)
  if the answer implies the plan or design must change:
      return PLAN_WRONG to the orchestrator
        (include last_failure_mode + evidence so it can pick plan vs design)
  else:
      apply the designer's guidance → goto a (implementer)
```

Use office hours when a FAIL or implementation-wrong bounce looks like it
stems from the *plan/design* being wrong (ambiguous AC, impossible
constraint, missing dependency), not from a fixable implementation error.

## Session reuse (Decision D6)

Keep a list mapping `{ role → session handle }` for this task so a retry
re-enters the **same** implementer/tester/reviewer session instead of
re-populating context. If the runtime cannot preserve a session, fall back
to re-dispatching with the **ledger** as the context carrier — the ledger is
the durable source of truth and is written precisely so a fresh session can
resume without loss.

## Return shape

Return to the orchestrator exactly:

```
{ verdict, impl_bounces, review_bounces, last_failure_mode, evidence }
```

- `verdict` ∈ `DONE | ESCALATE | PLAN_WRONG`.
- `last_failure_mode` — a short stable label for the latest blocking failure
  (e.g. `flaky-integration-test`, `missing-dependency`, `ac-ambiguous`).
  Reuse the same label across attempts when it's the same wall.
- `evidence` — the relevant ledger excerpts (verbatim) backing the verdict.

## Guardrails

- **You write task Status; nobody else does.**
- **Never edit product or test code yourself** — that's the implementer/tester.
- **Never talk to the user** — return to the orchestrator.
- **Always append to the ledger** on every sub-step; the ledger is how the
  user follows the work and how a reused-or-fresh session resumes.
- **Honesty:** the green-tests claim in the ledger must cite the command and
  exit code. A bare "tests pass" with no command is not acceptable — treat
  it as implementation-wrong and bounce.

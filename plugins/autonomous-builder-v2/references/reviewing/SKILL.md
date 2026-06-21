---
name: reviewing
description: Use this skill when the reviewer agent verifies a task or a phase Definition of Done in autonomous-builder-v2. It defines the three-verdict protocol (PASS / FAIL / PLAN_WRONG), the AC tier semantics (MoSCoW × Fast/Full/Journey), the AC modes (fast-only / fast+full / dod), the evidence-not-assertion rule, and how the reviewer reads and writes the per-task ledger.
---

# Reviewing

The reviewer verifies one task (or a phase's Definition of Done) against its
acceptance criteria **and** the per-task ledger, then emits one of three
verdicts. It never edits product code and never talks to the user.

## When to use

- Dispatched by the task-coordinator for a task review, or by the
  orchestrator for a phase `dod` review.
- The reviewer may dispatch the `researcher` (for context) and the `tester`
  (to re-run or exercise `[Journey]` AC) any time it needs evidence.

## AC tiers

Each AC is tagged `[<priority>] [<cadence>]`:

- **Priority (MoSCoW):** `Must` → FAIL on miss; `Should` → WARN (non-blocking);
  `Could` → INFO (non-blocking).
- **Cadence:** `Fast` (cheap, run every iteration), `Full` (expensive, run on
  the about-to-Done attempt), `Journey` (exercised against the running system
  by the tester).

Only `Must` failures produce a FAIL verdict and a `failure_mode` label.
`Should`/`Could` failures are recorded but never block.

## AC modes (told by the caller)

- **`fast-only`** — run all `[Fast]` AC across every priority. Used on early
  attempts to keep review cheap.
- **`fast+full`** — the about-to-Done attempt. Run `[Fast]` first; if any
  `Must` `[Fast]` fails, return FAIL without bothering with `[Full]`.
  Otherwise run all `[Full]` AC.
- **`dod`** — phase Definition of Done. Run every AC under the phase's
  `**Definition of Done:**`. For each `[Journey]` AC, dispatch the `tester`.
  Same fast-then-full ordering.

## The three verdicts

- **PASS** — every `Must` AC in scope for this mode passed, with evidence.
- **FAIL** — at least one `Must` AC failed. Attach a short stable
  `failure_mode:` label and the evidence. Reuse the label across attempts
  when it's the same wall.
- **PLAN_WRONG** — the task as specified cannot be made to pass because the
  *plan or design* is wrong (AC is self-contradictory, impossible, or
  describes the wrong behaviour). Return PLAN_WRONG with a structured reason;
  do not keep failing the implementer for a plan defect.

## Evidence, not assertion

- Re-run the AC yourself (or via the tester); read exit codes. Do not trust
  "tests pass" from the ledger without seeing the command + exit code.
- Quote the command and result in your Reviewer log entry.

## Ledger contract

Append a **Reviewer log** entry to `tasks/<task-id>.md`:

```markdown
## Reviewer log
- [<date> mode=<fast-only|fast+full|dod>] Verdict: PASS | FAIL | PLAN_WRONG
  - Evidence: <commands + exit codes / AC checked, verbatim>
  - failure_mode: <label>   (only on FAIL)
  - Opinion: <your judgement on top of the implementer/tester logs>
```

Read the whole ledger first — the implementer and tester logs tell you what
was attempted and which tests exist, so your review builds on top rather than
re-deriving from scratch.

## Banned phrases

Do not write "looks correct", "should pass", "appears to work", "probably
fine", or "left as future work". Each hides missing verification. If you
catch yourself reaching for one, run the check and cite the result instead.

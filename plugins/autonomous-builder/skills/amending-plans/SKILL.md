---
name: amending-plans
description: Use this skill on three sides of the plan-revision flow. The REVIEWER uses it to decide when to emit `PLAN_WRONG` vs `FAIL` and how to phrase the structured reason. The PLANNER uses it in revision mode to amend only affected tasks and produce a diff block. The ORCHESTRATOR uses it to dispatch revision-mode planning and run the user re-approval gate.
---

# Amending Plans

A plan is a hypothesis. In legacy or unfamiliar code, the hypothesis often
turns out wrong mid-execution. This skill defines the **first-class
plan-revision path** so mid-flight learnings don't become Blocked
escalations.

## When to use

- **Reviewer:** every review must end in one of three verdicts —
  `PASS`, `FAIL`, or `PLAN_WRONG`. This skill defines the FAIL-vs-PLAN_WRONG
  decision and the structured reason format.
- **Planner:** when dispatched in revision mode (orchestrator passes a
  PLAN_WRONG reason or a user amendment), follow the revision protocol here.
- **Orchestrator:** when a reviewer returns `PLAN_WRONG` or a user
  intervenes at a phase checkpoint, follow the revision-dispatch + re-approval
  flow.

## Reviewer: FAIL vs PLAN_WRONG (decision tree)

For each failing acceptance criterion, ask:

```
Is there ANY implementation under the current task description that would
make this AC pass?

├── Yes — the implementer just didn't do it (or did it wrong) → FAIL
│
└── No — the task as written cannot be made to pass → PLAN_WRONG
```

**Concrete triggers for `PLAN_WRONG`:**

1. **AC is impossible as stated.** E.g. AC says "function `foo` returns
   `True` for empty input" but the function's existing callers depend on it
   returning `None` — passing this AC would break callers.
2. **AC is mis-tagged.** Untagged AC, or `[cheap]` AC that actually requires
   a full integration run.
3. **AC contains a destructive command** (`rm -rf`, `DROP TABLE`, `--force`,
   `--no-verify`, `git push -f`) that the reviewer refuses to run.
4. **Implementation notes contradict Discoveries.** Notes say "edit
   `module/foo.py`" but a Discovery line says that file was deleted /
   doesn't exist / isn't used.
5. **A dependency was wrong.** Task says `Depends on: Task 1.2` but Task 1.2
   produces something the current task can't actually use.
6. **Scope creep is required.** The only way to make this AC pass is to
   touch files / systems the task description explicitly excluded — meaning
   the planner missed a needed task or mis-bounded this one.
7. **A required precondition is missing.** E.g. the task assumes a config
   file exists that hasn't been created and isn't in any prior task.

**If unsure**, default to `FAIL` first — give the implementer one retry. If
the same `failure_mode` repeats, then escalate to `PLAN_WRONG`. (Adaptive
retry in `orchestration-loop` will also catch this.)

## Reviewer: structured reason format

Every `PLAN_WRONG` verdict must include a reason block the planner can act
on. Append it to the Review log:

````markdown
- Attempt N (YYYY-MM-DD): **PLAN_WRONG**
  - **Trigger:** <one of: impossible AC | mis-tagged AC | destructive AC | notes-contradict-discoveries | bad dependency | scope-out-of-bounds | missing precondition>
  - **Affected AC:** AC #<n>: "<verbatim AC text>"
  - **Reason:** <2–4 sentences. What did you try? What did you find? Why does the task as written not admit a passing implementation?>
  - **Evidence:** <file:line citations or Discovery references>
  - **Suggested fix (optional):** <one short hint for the planner — e.g. "split into Task 2.3a (add config) + Task 2.3b (use it)", "drop AC #2; it duplicates Phase 1 regression AC", "needs prerequisite task to create `foo.json` first">
````

The "Suggested fix" is advisory only — the planner decides.

## Planner: revision-mode protocol

The orchestrator invokes the planner in revision mode with:

- The plan file path.
- The triggering Review log entry (full `PLAN_WRONG` reason block) or the
  user's amendment request from a phase checkpoint.

The planner then:

1. **Read.** Load the plan file in full, including `## Context` and
   `## Discoveries`. Do not dispatch researcher unless the trigger explicitly
   requires it — Discoveries should already contain what's needed.
2. **Minimum-blast-radius amendment.** Identify the affected task and its
   downstream dependents (any task with `Depends on:` referencing it,
   transitively). Touch only those. Tasks not on the dependency chain must
   remain byte-for-byte unchanged.
3. **Write the revision block.** Append at the end of the file, BEFORE any
   previous Revision block (newest at the bottom is fine — order is by N):

   ````markdown
   ## Revision <N> (proposed)

   **Triggered by:** Task <id> <verdict | "user amendment at Phase <p> checkpoint"> — <one-liner reason>
   **Affected tasks:** Task <id1>, Task <id2>, …
   **Summary of changes:**
   - Task <id1>: <2–10 word delta — e.g. "split into 1.2a + 1.2b">
   - Task <id2>: <delta>
   - Task <id3> (new): <name>

   ### Task <id1>: <new name>

   **Status:** Pending
   **Depends on:** <new>
   **Reasoning:** <new>
   **Implementation notes:** <new>
   **Acceptance criteria:**
   - [ ] [cheap] <new>
   - [ ] [gate]  <new>

   **Review log:**
   - (carried over from before revision — paste prior log here verbatim)

   ### Task <id2>: <new name>
   ...
   ````

4. **Preserve Review logs.** When replacing a task block, copy the prior
   Review log verbatim into the new block. Future agents need the full
   history to make adaptive-retry and PLAN_WRONG-loop decisions.
5. **Set overall Status** at the top of the file to
   `Awaiting revision approval`.
6. **Return** the revision number and the affected task IDs to the
   orchestrator. Do not contact the user.

### What revision-mode planner must NOT do

- Touch unrelated tasks "while we're at it."
- Re-do the full discovery phase.
- Reorder phases.
- Delete Review logs or Discoveries.
- Apply the changes in place (only the orchestrator applies, after user
  approval).

## Orchestrator: revision-dispatch + re-approval

When a reviewer returns `PLAN_WRONG` (or a user intervenes at a phase
checkpoint with a non-trivial amendment):

1. **Set status.** Overall Status → `Awaiting revision approval`. Task
   Status → `Blocked` temporarily (it will be replaced by the revision).
2. **Dispatch planner in revision mode** with the trigger details.
3. **Present the diff to the user.** Show:
   - The "Triggered by" line.
   - "Summary of changes" bullets.
   - The full new task blocks.
   - One question: "Approve revision <N>? (reply 'approve', 'reject', or
     describe further changes)."
4. **Apply on approval.** Replace the affected task blocks in place with the
   new ones from the Revision block. Update phase regression AC if the
   revision changed it. Remove the `## Revision <N> (proposed)` block (the
   approved revision IS the new plan). Overall Status → `In progress`. Task
   Status of the first revised task → `Pending`. Resume the loop from there.
5. **Block on rejection.** Overall Status → `Blocked`. Escalate to user
   with the planner's revision intact under `## Revision <N> (proposed)` so
   nothing is lost. Wait for user direction.
6. **Iterate on "describe further changes".** Re-dispatch planner in
   revision mode with the user's input as an additional trigger. The new
   revision becomes `## Revision <N+1> (proposed)`.

## Adaptive retry hand-off

`orchestration-loop` handles the "FAIL twice with same `failure_mode` →
escalate" rule. When that fires, treat it like a soft `PLAN_WRONG`:

- Orchestrator dispatches researcher (thoroughness=medium) on
  "why is `failure_mode: <label>` blocking this AC?" before deciding.
- If the researcher's finding indicates the AC or task is the problem (not
  the implementation), promote to `PLAN_WRONG` and dispatch the planner in
  revision mode.
- Otherwise escalate to the user with the full review log.

## Examples

### Example 1 — FAIL (not PLAN_WRONG)

> Task: "Add `--verbose` flag to `cli.py`."
> AC #1 [cheap]: `python cli.py --verbose --help` exits 0 and output contains "verbose".
> Reviewer ran the command; exit code was 2 because implementer didn't add the flag to the argparse parser.
> Verdict: **FAIL** (`failure_mode: argparse-missing-flag`). An implementation exists that would pass this AC.

### Example 2 — PLAN_WRONG (impossible AC)

> Task: "Rename `cli.py` to `command_line.py` and update all callers."
> AC #2 [gate]: "No references to `cli.py` anywhere in the repo after the rename."
> Reviewer searched and found `docs/changelog.md` and `README.md` historically reference `cli.py` in the change history; rewriting those would falsify history.
> Verdict: **PLAN_WRONG** (trigger: impossible AC). Suggested fix: "Tighten AC to 'No code-path references to `cli.py` (excluding `docs/`, `CHANGELOG.md`, and historical commit-message-style files)'."

### Example 3 — PLAN_WRONG (scope-out-of-bounds)

> Task: "Add unit test for `Foo.bar()`."
> AC #1 [cheap]: `pytest tests/test_foo.py::test_bar` exits 0.
> Reviewer ran pytest; test failed because `Foo.bar()` itself has a bug — the test is correct but the implementation is wrong. Task description excludes touching `foo.py`.
> Verdict: **PLAN_WRONG** (trigger: scope-out-of-bounds). Suggested fix: "Add prerequisite Task 'Fix bug in `Foo.bar()` for empty input case', then re-attempt this test task."

## Checklist (reviewer, before emitting PLAN_WRONG)

- [ ] Walked the FAIL-vs-PLAN_WRONG decision tree.
- [ ] If unsure, defaulted to FAIL for at least one attempt.
- [ ] Reason block includes Trigger, Affected AC, Reason, Evidence.
- [ ] Suggested fix is advisory and ≤1 short sentence.

## Checklist (planner, before returning revision)

- [ ] Touched ONLY affected task + downstream dependents.
- [ ] Preserved prior Review logs verbatim under each amended task.
- [ ] Set overall Status to `Awaiting revision approval`.
- [ ] Appended `## Revision <N> (proposed)` block; did NOT apply in place.

## Checklist (orchestrator, before resuming after approval)

- [ ] User explicitly approved (not just acknowledged).
- [ ] Replaced affected blocks in place; removed proposed-revision block.
- [ ] Overall Status → `In progress`.
- [ ] Resumed loop from the first revised task.

## References

- `../plan-file-format/SKILL.md` — Status vocabulary, Revision block format.
- `../reviewing-acceptance-criteria/SKILL.md` — `failure_mode` labelling.
- `../orchestration-loop/SKILL.md` — adaptive-retry rule and dispatch wiring.

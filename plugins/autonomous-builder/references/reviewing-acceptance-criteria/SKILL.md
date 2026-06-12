---
name: reviewing-acceptance-criteria
description: Use this skill when the reviewer agent is verifying one task attempt against its acceptance criteria. It defines the read protocol (Context + Discoveries, NOT implementer scratch), the cheap-vs-gate execution rule, the failure_mode labelling that drives adaptive retry, the three-verdict output (PASS / FAIL / PLAN_WRONG), and the destructive-AC refusal.
---

# Reviewing Acceptance Criteria

The reviewer is invoked **once per task per attempt** by the orchestrator,
immediately after the implementer. Its job is to verify the task's AC
independently and emit one of three verdicts: `PASS`, `FAIL`, or
`PLAN_WRONG`. It never edits product code and never talks to the user.

## When to use

- Loaded by the `reviewer` agent on every dispatch.
- Consulted at the start of each review and again when writing the Review
  log entry.

## Per-attempt protocol

### 1. Read the dispatch brief

The orchestrator passes you:

- Plan file path (`.plans/<slug>.md`).
- Task ID.
- AC mode: `cheap-only` or `cheap+gate`. See "Cheap vs gate" below.

### 2. Read shared knowledge, NOT implementer scratch

Open the plan file and read:

1. The assigned task block (Status, Reasoning, Implementation notes, AC,
   Review log).
2. `## Context`.
3. `## Discoveries`.

Do **NOT** read:

- The implementer's artefact list as authoritative. (You will see what
  files were touched, but you verify against the AC, not against the
  implementer's claims.)
- The implementer's internal reasoning or any commentary they may have
  added beyond Discoveries. Your independence depends on judging the result,
  not the process.

This is the key legacy-hardening rule: **fresh judgement, shared knowledge.**
Discoveries gives you the context the implementer had; you bring an
independent verdict.

### 3. Validate AC well-formedness FIRST

Before running anything, scan every AC for this task:

- Every AC must be tagged `[cheap]` or `[gate]`. Untagged → emit
  `PLAN_WRONG` (trigger: mis-tagged AC).
- No banned phrasing ("looks good", "is clean", "works correctly",
  "well-structured", "no issues", "follows best practices"). → emit
  `PLAN_WRONG` (trigger: impossible AC).
- No destructive commands (`rm -rf`, `DROP TABLE`, `--force`,
  `--no-verify`, `git push -f`, `chmod -R`, `sudo`, etc.). → emit
  `PLAN_WRONG` (trigger: destructive AC). **Do not run them.**

If any AC fails this validation, emit `PLAN_WRONG` immediately without
running anything. See `../amending-plans/SKILL.md` for the structured
reason format.

### 4. Choose which AC to run (cheap vs gate)

- **`cheap-only` mode** — run all `[cheap]` AC for this task only.
  Skip `[gate]` AC entirely.
- **`cheap+gate` mode** — run all `[cheap]` AC first. If any FAIL, emit
  FAIL immediately without bothering with `[gate]` (don't burn slow tests
  when fast ones are already red). If all `[cheap]` PASS, run all
  `[gate]` AC.

The orchestrator chooses the mode based on attempt context. Trust it.

### 5. Verify each AC

For each AC:

1. **Read what the AC asks for.** Identify the exact command, file
   assertion, or behaviour named.
2. **Run only what's named.** Run the literal command. Read the literal
   file. Verify the literal behaviour. No "while I'm at it" tangents.
3. **Capture the result** with the actual exit code, file content, or
   observed output — verbatim, not paraphrased.
4. **Dispatch the researcher** ONLY if the AC requires understanding
   beyond directly-edited files (e.g. "behaviour X holds across the
   whole module" and you don't know the call sites). See
   `../researching/SKILL.md`. Append the researcher's finding to
   `## Discoveries` before deciding.
5. **Decide per-AC verdict:** PASS or FAIL.
6. **On FAIL, write a `failure_mode:` label.** This is what drives
   adaptive retry in `../orchestration-loop/SKILL.md`. Pick a short
   kebab-case label that describes the *category* of failure, not the
   specific symptom. Examples:
   - `import-error`
   - `wrong-exit-code`
   - `missing-output-line`
   - `assertion-failed`
   - `lint-warning`
   - `regression-elsewhere`
   - `file-not-created`
   - `signature-mismatch`

   The point of the label: if two consecutive attempts fail with the same
   `failure_mode`, the orchestrator knows the implementer is stuck in the
   same way and escalates without burning attempt 3.

### 6. Decide overall verdict

```
For each AC:
  if PASS                                            → keep going
  if FAIL                                            → overall = FAIL
  if PLAN_WRONG (validation step or mid-verification)→ overall = PLAN_WRONG
                                                       (stop, no more AC)

if every AC PASS                                     → overall = PASS
if at least one FAIL and no PLAN_WRONG               → overall = FAIL
if any PLAN_WRONG                                    → overall = PLAN_WRONG
```

### 7. Optionally append to `## Discoveries`

If during verification you learned something durable (a finding the next
implementer or reviewer should know), append a Discovery line with the
`[reviewer · YYYY-MM-DD]` tag. Examples:

- A test was passing for the wrong reason that you noticed in passing.
- An AC was satisfied by a side-effect of an unrelated module — flag for
  the planner.

Do **NOT** append every per-AC result here. Those go in the Review log.

### 8. Append the Review log entry

In the assigned task block, under `**Review log:**`, append:

#### For PASS

````markdown
- Attempt <N> (YYYY-MM-DD): **PASS**
  - AC #1 [cheap]: PASS — `<command>` exit 0
  - AC #2 [gate]: PASS — `<command>` exit 0 (`<key output line>`)
  - Notes: <one line — or omit>
````

#### For FAIL

````markdown
- Attempt <N> (YYYY-MM-DD): **FAIL** (`failure_mode: <label>`)
  - AC #1 [cheap]: PASS — `<command>` exit 0
  - AC #2 [cheap]: FAIL — `<command>` exit 1
    - Output: `<verbatim ≤3 lines of actual output / error message>`
    - **Actionable feedback for implementer:** <2–3 sentences describing what's wrong and a concrete hint at what to change. E.g. "The parser doesn't add `--verbose` to its argparse — see line 24 of `cli.py`. Add `parser.add_argument('--verbose', action='store_true')` and re-run the test.">
  - AC #3 [gate]: SKIPPED (cheap-only mode)
````

#### For PLAN_WRONG

````markdown
- Attempt <N> (YYYY-MM-DD): **PLAN_WRONG**
  - **Trigger:** <impossible AC | mis-tagged AC | destructive AC | notes-contradict-discoveries | bad dependency | scope-out-of-bounds | missing precondition>
  - **Affected AC:** AC #<n>: "<verbatim AC text>"
  - **Reason:** <2–4 sentences. What did you try? What did you find? Why does the task as written not admit a passing implementation?>
  - **Evidence:** <file:line citations or Discovery references>
  - **Suggested fix (optional):** <one short sentence for the planner>
````

### 9. Return the verdict

Reply to the orchestrator with a compact verdict header:

```markdown
**Reviewer verdict — Task <id> attempt <N>: <PASS | FAIL | PLAN_WRONG>**

<For FAIL: include `failure_mode: <label>` here too.>
<For PLAN_WRONG: include trigger label here too.>

Review log entry appended.
```

That's it. No commentary beyond what's in the Review log.

## Cheap vs gate (in detail)

The plan-file format requires every AC to be tagged. The orchestrator
chooses which subset you run:

- `cheap-only`: runs only `[cheap]` AC. Used for early attempts where the
  cost of `[gate]` is wasted if a `[cheap]` is going to fail. AC #s tagged
  `[gate]` get recorded as `SKIPPED (cheap-only mode)`.
- `cheap+gate`: runs everything. Used on the about-to-Done attempt. If any
  `[cheap]` fails, do NOT run `[gate]` — emit FAIL after the `[cheap]`
  failure.

Don't second-guess the orchestrator. If it asks for `cheap-only`, don't
run `[gate]` AC "just to be thorough" — that defeats the cost discipline.

## Refusing destructive AC

Some AC may be authored carelessly with commands that would damage the
repo or environment:

- File deletion: `rm -rf`, `del /q`, `Remove-Item -Recurse -Force`.
- DB mutation: `DROP TABLE`, `TRUNCATE`, `DELETE FROM` (without WHERE).
- Git destruction: `git push -f`, `git reset --hard origin/main`,
  `git checkout .` (data-losing), `git clean -fdx`.
- Hook bypass: `--no-verify`, `--skip-hooks`.
- Privilege escalation: `sudo`, `runas`.
- Recursive permissions: `chmod -R 777`.

If an AC contains any of these verbs/flags, do **not** run it. Emit
`PLAN_WRONG` with trigger `destructive AC` and suggest a safer
reformulation. Even if it's "what the user wanted" — the planner should
reformulate so the AC asserts the post-condition without naming the
destructive command.

## Phase-regression AC mode

When the orchestrator dispatches you to verify a phase's regression AC
(after the last task in a phase passes its own AC), the protocol is the
same — but the AC live under the phase's `**Phase regression AC:**`
section, not a task block. Append the result to a new task-style block
the orchestrator creates at the bottom of the phase, OR (simpler) under a
dedicated `**Phase review log:**` section the orchestrator appends. Follow
whichever the orchestrator's brief specifies.

If a phase-regression AC FAILs, the verdict is FAIL — the orchestrator
will re-open the last task as `Awaiting review` with the regression
feedback. Treat it as a normal FAIL with a `failure_mode:
regression-elsewhere` label.

## Pitfalls

- **Reading the implementer's reasoning.** Breaks independence. Stick to
  Context + Discoveries + the task block.
- **"Looks fine."** Banned. Every AC gets a concrete PASS / FAIL with
  evidence.
- **Running `[gate]` in cheap-only mode.** Wastes minutes per attempt.
- **Editing product code to make an AC pass.** Strictly forbidden. You're
  a reviewer. If the AC is wrong, emit `PLAN_WRONG`.
- **Forgetting the `failure_mode` label.** It's how the orchestrator
  detects "stuck in the same wall" and escalates.
- **Vague `failure_mode` labels.** `error`, `bug`, `failed` are useless.
  Use category labels (`import-error`, `wrong-exit-code`,
  `regression-elsewhere`).
- **Running destructive AC commands** instead of refusing.

## Checklist (every review, before returning)

- [ ] Read only task block + Context + Discoveries (not implementer scratch).
- [ ] Validated AC well-formedness (tagging, banned phrases, destructive
      commands) — emitted PLAN_WRONG immediately if any failed.
- [ ] Honoured the orchestrator's `cheap-only` vs `cheap+gate` mode.
- [ ] Ran only the literal commands / checks the AC named.
- [ ] Per-AC verdict captured with verbatim evidence.
- [ ] On FAIL: `failure_mode: <category-label>` and actionable feedback
      included.
- [ ] On PLAN_WRONG: trigger label and structured reason included.
- [ ] Review log entry appended (not edited in place).
- [ ] Did NOT edit product code.
- [ ] Did NOT mark task `Done` or change task Status.
- [ ] Returned a compact verdict header.

## Examples

### Example A — PASS (cheap-only mode)

> Task: "Add `--verbose` flag to `cli.py`."
>
> AC #1 [cheap]: `python cli.py --verbose --help` exits 0 and stdout contains "verbose".
> AC #2 [gate]: Full CLI test suite (`pytest tests/test_cli/`) exits 0.
>
> Mode: cheap-only (attempt 1).
> Result: AC #1 PASS. AC #2 SKIPPED (cheap-only).
> **Verdict: PASS** — proceed to next task. (Orchestrator will dispatch in cheap+gate mode when finalising.)

### Example B — FAIL with actionable feedback

> AC #1 [cheap]: `pytest tests/test_cli.py::test_verbose` exits 0.
> Ran: exit 2. Output: "ArgumentError: unrecognized arguments: --verbose".
> **Verdict: FAIL** (`failure_mode: argparse-missing-flag`).
> Feedback: "`cli.py` doesn't declare `--verbose` in its argparse. Add `parser.add_argument('--verbose', action='store_true')` near line 24 (mirror the pattern of `--quiet` already there)."

### Example C — PLAN_WRONG (destructive AC)

> AC #2 [gate]: "After the migration, run `git push -f origin main` and verify the remote HEAD matches local."
> Did not run.
> **Verdict: PLAN_WRONG** (trigger: destructive AC).
> Reason: AC names `git push -f`, which rewrites shared history on the main branch. Suggested fix: "Replace with a non-destructive assertion: run `git diff origin/main..main` and verify it's empty after a normal `git push`."

## References

- `../plan-file-format/SKILL.md` — AC syntax, Review log format,
  Discoveries format.
- `../amending-plans/SKILL.md` — full FAIL-vs-PLAN_WRONG decision tree and
  structured reason format.
- `../orchestration-loop/SKILL.md` — how `failure_mode` labels drive
  adaptive retry; how `cheap-only` vs `cheap+gate` is chosen.
- `../researching/SKILL.md` — how to dispatch the researcher for AC that
  span beyond directly-edited files.

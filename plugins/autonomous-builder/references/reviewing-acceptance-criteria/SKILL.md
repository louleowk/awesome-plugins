---
name: reviewing-acceptance-criteria
description: Use this skill when the reviewer agent is verifying one task attempt against its acceptance criteria. It defines the read protocol (Context + Discoveries, NOT implementer scratch), the cadence-and-mode execution rule (`fast-only` / `fast+full` / `dod`), the MoSCoW per-AC verdict mapping (Must → PASS/FAIL, Should → PASS/WARN, Could → PASS/INFO), the failure_mode labelling that drives adaptive retry, the three-verdict output (PASS / FAIL / PLAN_WRONG), and the destructive-AC refusal.
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
- Task ID (or, in phase Definition of Done mode, the phase ID).
- AC mode: `fast-only`, `fast+full`, or `dod`. See "Cadence and modes" below.

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

Before running anything, scan every AC for this task (or every AC
in the phase's `**Definition of Done:**` block in `dod` mode):

- Every AC must be tagged with **both** a priority
  (`[Must]` / `[Should]` / `[Could]`) and a cadence
  (`[Fast]` / `[Full]` / `[Journey]`). Untagged or single-tagged →
  emit `PLAN_WRONG` (trigger: `mis-tagged AC`).
- `[Journey]` AC are only allowed in a phase's `**Definition of
  Done:**` block. Finding `[Journey]` on a task-level AC → emit
  `PLAN_WRONG` (trigger: `mis-placed AC`).
- Every `[Journey]` AC body MUST start with a `(cli)`, `(api)`,
  or `(web)` surface prefix. Missing or wrong prefix → emit
  `PLAN_WRONG` (trigger: `mis-tagged AC`).
- `Won't` is not an AC tag. Finding `[Won't]` on any AC → emit
  `PLAN_WRONG` (trigger: `mis-tagged AC`).
- A plan that mixes legacy `[cheap]` / `[gate]` syntax with the new
  `[Priority] [Cadence]` syntax in the same file → emit `PLAN_WRONG`
  (trigger: `mixed-vocabulary`).
- No banned phrasing in the body ("looks good", "is clean", "works
  correctly", "well-structured", "no issues", "follows best
  practices"). → emit `PLAN_WRONG` (trigger: `impossible AC`).
- No destructive commands (`rm -rf`, `DROP TABLE`, `--force`,
  `--no-verify`, `git push -f`, `chmod -R`, `sudo`, etc.). → emit
  `PLAN_WRONG` (trigger: `destructive AC`). **Do not run them.**
- In `dod` mode: if any `[Journey]` AC exists in the plan, an
  earlier phase (typically named "Environment") must have a Done
  Definition of Done that recorded a surface-specific entry-point
  Discovery line:
  - `(cli)` Journey AC → a `binary path: <path-or-name>` line.
  - `(api)` Journey AC → a `bring-up URL: <url>` or `api URL: <url>` line.
  - `(web)` Journey AC → a `bring-up URL: <url>` line.
  If the matching line is missing → emit `PLAN_WRONG` (trigger:
  `missing-environment-phase`).

If any AC fails this validation, emit `PLAN_WRONG` immediately
without running anything. See `../amending-plans/SKILL.md` for the
structured reason format.

### 4. Choose which AC to run (cadence + mode)

- **`fast-only` mode** (per-attempt review of one task) — run all
  `[Fast]` AC in the task block (every priority). Record `[Full]`
  AC as `SKIPPED (fast-only mode)`. `[Journey]` AC do not appear at
  task level.
- **`fast+full` mode** (about-to-Done review of one task) — run all
  `[Fast]` AC first. If any `Must`-priority `[Fast]` AC FAILs, emit
  FAIL immediately without bothering with `[Full]` (don't burn slow
  tests when fast ones are already red). If all `Must` `[Fast]` AC
  pass, run all `[Full]` AC.
- **`dod` mode** (phase Definition of Done review) — run all AC in
  the phase's `**Definition of Done:**` block. For each `[Journey]`
  AC, dispatch the `tester` subagent (see step 5b). Same
  fast-then-full ordering applies: if any `Must`-priority `[Fast]`
  DoD AC FAILs, skip the rest.

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

### 5b. Dispatching the tester for `[Journey]` AC

In `dod` mode, every `[Journey]` AC is verified by dispatching the
`tester` subagent. Do not attempt to drive the running system
yourself — the tester owns surface-specific drivers (shell for
`(cli)`, `curl` / `WebFetch` for `(api)`, Playwright for `(web)`),
evidence capture, and silently-broken signal detection.

Parse the AC body to extract surface and journey:

```
[Must] [Journey] (api) POST /users with valid payload returns 201 + Location header; ...
                 ^^^^^ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                 surface persona-journey description
```

Look up the matching entry-point Discovery line by surface:

| Surface | Discovery tag                          |
| ------- | -------------------------------------- |
| `cli`   | `binary path: <abs-or-PATH-name>`      |
| `api`   | `bring-up URL: <url>` or `api URL: <url>` |
| `web`   | `bring-up URL: <url>`                  |

If the matching line is missing, do NOT dispatch. Emit
`PLAN_WRONG` with trigger `missing-environment-phase` and stop.

Dispatch brief shape:

```
plan_path:        .plans/<slug>.md
phase_id:         <P>
journey_ac:       "<verbatim AC text including [Priority] [Journey] (surface) tags>"
surface:          cli | api | web
target:           <binary path | base URL>
persona_journey:  "<verbatim AC body text after the (surface) prefix>"
attempt:          <1–3>
```

The tester returns one of three verdicts: PASS, FAIL, or
INCONCLUSIVE. Map to per-AC verdict via the AC's MoSCoW priority:

| Tester verdict | `Must` priority   | `Should` priority | `Could` priority |
| -------------- | ----------------- | ----------------- | ---------------- |
| PASS           | PASS              | PASS              | PASS             |
| FAIL           | **FAIL** (`failure_mode: journey-failed`) | **WARN**          | **INFO**         |
| INCONCLUSIVE   | retry up to 3 → then **FAIL** (`failure_mode: journey-inconclusive`) | retry → then **WARN** | retry → then **INFO** |

Append the tester's full journey log block under the Review log
entry verbatim — it is the evidence trail for the `[Journey]` AC.
See `../exercising-journeys/SKILL.md` for the canonical template
(which varies by surface).

### 6. Decide overall verdict

The overall verdict is decided by `Must`-priority outcomes only.
`Should` (WARN) and `Could` (INFO) outcomes are recorded but never
cause FAIL or PLAN_WRONG.

```
For each AC:
  if Must PASS    → keep going
  if Must FAIL    → overall = FAIL
  if Should/Could WARN/INFO/PASS → keep going (record only)
  if PLAN_WRONG (validation step or mid-verification) → overall = PLAN_WRONG
                                                       (stop, no more AC)

if every Must AC PASS                                  → overall = PASS
if at least one Must FAIL and no PLAN_WRONG            → overall = FAIL
if any PLAN_WRONG                                      → overall = PLAN_WRONG
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
  - AC #1 [Must]   [Fast]: PASS — `<command>` exit 0
  - AC #2 [Must]   [Full]: PASS — `<command>` exit 0 (`<key output line>`)
  - AC #3 [Should] [Fast]: WARN — `<command>` exit 1 (non-blocking; recorded for phase checkpoint)
  - Notes: <one line — or omit>
````

A PASS verdict may include WARN / INFO lines from `Should` /
`Could` AC. They do not change the overall verdict but the
orchestrator surfaces WARNs at the phase checkpoint.

#### For FAIL

````markdown
- Attempt <N> (YYYY-MM-DD): **FAIL** (`failure_mode: <label>`)
  - AC #1 [Must]   [Fast]: PASS — `<command>` exit 0
  - AC #2 [Must]   [Fast]: FAIL — `<command>` exit 1
    - Output: `<verbatim ≤3 lines of actual output / error message>`
    - **Actionable feedback for implementer:** <2–3 sentences describing what's wrong and a concrete hint at what to change. E.g. "The parser doesn't add `--verbose` to its argparse — see line 24 of `cli.py`. Add `parser.add_argument('--verbose', action='store_true')` and re-run the test.">
  - AC #3 [Must]   [Full]: SKIPPED (fast-only mode)
  - AC #4 [Should] [Fast]: WARN — `<command>` exit 1 (non-blocking)
````

#### For PLAN_WRONG

````markdown
- Attempt <N> (YYYY-MM-DD): **PLAN_WRONG**
  - **Trigger:** <impossible AC | mis-tagged AC | mis-placed AC | mixed-vocabulary | destructive AC | notes-contradict-discoveries | bad dependency | scope-out-of-bounds | missing precondition | missing-environment-phase | unharvested-research>
  - **Affected AC:** AC #<n>: "<verbatim AC text>"
  - **Reason:** <2–4 sentences. What did you try? What did you find? Why does the task as written not admit a passing implementation?>
  - **Evidence:** <file:line citations or Discovery references>
  - **Suggested fix (optional):** <one short sentence for the planner>
````

#### For `[Journey]` AC (`dod` mode)

Under the AC's per-AC line, paste the tester's full journey log
block verbatim. The block shape varies by surface; see
`../exercising-journeys/SKILL.md` for the canonical template.
Examples:

````markdown
  - AC #2 [Must] [Journey] (web): <PASS|FAIL|WARN|INFO> — tester verdict: <PASS|FAIL|INCONCLUSIVE>
    ```
    ## Tester journey log
    - Phase / AC: <phase-id> / "<verbatim Journey AC text>"
    - Surface: web
    - Target: <base URL>
    - Reachability probe: curl -fsS -o /dev/null -w '%{http_code}' <url>/health → 200
    - Steps run: <N>
    - Step log: ...
    - Artefacts: .plans/.cache/tester/<phase-id>/step-1.png, ...
    - Console errors: <count>
    - HTTP errors: <4xx count> 4xx + <5xx count> 5xx
    - Verdict: <PASS|FAIL|INCONCLUSIVE>
    ```
  - AC #3 [Must] [Journey] (api): <PASS|FAIL|WARN|INFO> — tester verdict: <PASS|FAIL|INCONCLUSIVE>
    ```
    ## Tester journey log
    - Phase / AC: ...
    - Surface: api
    - Target: <base URL>
    - Status codes: step-1=201, step-2=200, ...
    - Side-effect verifications: step-1 → GET /users/<id> returned 200 + same email
    - Verdict: <PASS|FAIL|INCONCLUSIVE>
    ```
  - AC #4 [Must] [Journey] (cli): <PASS|FAIL|WARN|INFO> — tester verdict: <PASS|FAIL|INCONCLUSIVE>
    ```
    ## Tester journey log
    - Phase / AC: ...
    - Surface: cli
    - Target: <binary path>
    - Exit codes: step-1=0, step-2=2, ...
    - stderr hits: 0 matches of /error|panic|.../i
    - Verdict: <PASS|FAIL|INCONCLUSIVE>
    ```
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

## Cadence and modes (in detail)

The plan-file format requires every AC to be tagged with both a
MoSCoW priority and a cadence. The orchestrator chooses which subset
you run via the dispatch mode:

- **`fast-only`**: runs only `[Fast]` AC for the current task. Used
  for early per-task attempts where the cost of `[Full]` is wasted
  if a `[Fast]` is going to fail. AC tagged `[Full]` are recorded as
  `SKIPPED (fast-only mode)`. `[Journey]` AC do not appear at task
  level and are never run in this mode.
- **`fast+full`**: runs every task-level AC. Used on the
  about-to-Done attempt. If any `Must`-priority `[Fast]` fails, do
  NOT run `[Full]` — emit FAIL after the `[Fast]` failure.
  `[Journey]` AC do not appear at task level.
- **`dod`**: phase Definition of Done verification. Runs every AC
  in the phase's `**Definition of Done:**` block. For `[Journey]`
  AC, dispatches the `tester` subagent (see step 5b).
  Same fast-then-full ordering applies.

Don't second-guess the orchestrator. If it asks for `fast-only`,
don't run `[Full]` AC "just to be thorough" — that defeats the cost
discipline.

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

## Phase Definition of Done mode

When the orchestrator dispatches you in `dod` mode (after the last
task in a phase passes its own AC), the AC live under the phase's
`**Definition of Done:**` block, not a task block. Append the result
to a dedicated `**Phase review log:**` section the orchestrator
creates under the phase header.

In `dod` mode you run every AC priority and cadence (see step 4).
`[Journey]` AC dispatch the tester per step 5b.

If a Definition-of-Done AC FAILs (Must priority), the verdict is
FAIL — the orchestrator will re-open the last task as
`Awaiting review` with the DoD feedback. Treat it as a normal FAIL
with a `failure_mode:` label (commonly `regression-elsewhere`,
`journey-failed`, or `journey-inconclusive`).

`Should` / `Could` DoD AC failures become WARN / INFO lines under
the Phase review log; they do not block phase completion. The
orchestrator surfaces WARNs in the phase checkpoint message to the
user.

## Pitfalls

- **Reading the implementer's reasoning.** Breaks independence. Stick to
  Context + Discoveries + the task block.
- **"Looks fine."** Banned. Every AC gets a concrete PASS / FAIL / WARN /
  INFO with evidence.
- **Running `[Full]` in `fast-only` mode.** Wastes minutes per attempt.
- **Treating a `Should` failure as FAIL.** It is WARN. Only `Must`
  failures cause FAIL.
- **Forgetting to dispatch the tester for `[Journey]` AC.**
  In `dod` mode, every `[Journey]` AC must go through the tester.
- **Editing product code to make an AC pass.** Strictly forbidden. You're
  a reviewer. If the AC is wrong, emit `PLAN_WRONG`.
- **Forgetting the `failure_mode` label** on `Must` FAILs. It's how the
  orchestrator detects "stuck in the same wall" and escalates.
- **Vague `failure_mode` labels.** `error`, `bug`, `failed` are useless.
  Use category labels (`import-error`, `wrong-exit-code`,
  `regression-elsewhere`, `journey-failed`).
- **Running destructive AC commands** instead of refusing.

## Checklist (every review, before returning)

- [ ] Read only task block + Context + Discoveries (not implementer scratch).
- [ ] Validated AC well-formedness (priority + cadence tags, banned phrases,
      `[Journey]` placement, `[Won't]` rejection, mixed-vocabulary,
      destructive commands) — emitted PLAN_WRONG immediately if any failed.
- [ ] Honoured the orchestrator's `fast-only` / `fast+full` / `dod` mode.
- [ ] In `dod` mode: dispatched the tester for every `[Journey]` AC.
- [ ] Ran only the literal commands / checks the AC named.
- [ ] Per-AC verdict captured with verbatim evidence (PASS / FAIL / WARN /
      INFO mapped from priority).
- [ ] On `Must` FAIL: `failure_mode: <category-label>` and actionable
      feedback included.
- [ ] On PLAN_WRONG: trigger label and structured reason included.
- [ ] Review log entry appended (not edited in place).
- [ ] Did NOT edit product code.
- [ ] Did NOT mark task `Done` or change task Status.
- [ ] Returned a compact verdict header.

## Examples

### Example A — PASS (`fast-only` mode)

> Task: "Add `--verbose` flag to `cli.py`."
>
> AC #1 [Must] [Fast]: `python cli.py --verbose --help` exits 0 and stdout contains "verbose".
> AC #2 [Must] [Full]: Full CLI test suite (`pytest tests/test_cli/`) exits 0.
>
> Mode: `fast-only` (attempt 1).
> Result: AC #1 PASS. AC #2 SKIPPED (fast-only).
> **Verdict: PASS** — proceed to next task. (Orchestrator will dispatch in `fast+full` mode when finalising.)

### Example B — FAIL with actionable feedback

> AC #1 [Must] [Fast]: `pytest tests/test_cli.py::test_verbose` exits 0.
> Ran: exit 2. Output: "ArgumentError: unrecognized arguments: --verbose".
> **Verdict: FAIL** (`failure_mode: argparse-missing-flag`).
> Feedback: "`cli.py` doesn't declare `--verbose` in its argparse. Add `parser.add_argument('--verbose', action='store_true')` near line 24 (mirror the pattern of `--quiet` already there)."

### Example C — PLAN_WRONG (destructive AC)

> AC #2 [Must] [Full]: "After the migration, run `git push -f origin main` and verify the remote HEAD matches local."
> Did not run.
> **Verdict: PLAN_WRONG** (trigger: destructive AC).
> Reason: AC names `git push -f`, which rewrites shared history on the main branch. Suggested fix: "Replace with a non-destructive assertion: run `git diff origin/main..main` and verify it's empty after a normal `git push`."

## References

- `../plan-file-format/SKILL.md` — AC syntax, Review log format,
  Discoveries format.
- `../amending-plans/SKILL.md` — full FAIL-vs-PLAN_WRONG decision tree and
  structured reason format.
- `../orchestration-loop/SKILL.md` — how `failure_mode` labels drive
  adaptive retry; how `fast-only` / `fast+full` / `dod` is chosen.
- `../researching/SKILL.md` — how to dispatch the researcher for AC that
  span beyond directly-edited files.

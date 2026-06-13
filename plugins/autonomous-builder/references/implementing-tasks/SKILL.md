---
name: implementing-tasks
description: Use this skill when the implementer agent is executing one task per attempt. It defines what to read first, when to dispatch the researcher, how to perform minimal edits with discipline, how to self-check with `[Fast]` AC, and how to hand off cleanly to the reviewer.
---

# Implementing Tasks

The implementer is invoked **once per task per attempt** by the
orchestrator. It edits product code, runs fast self-checks, updates the
task's `**Status:**` and `## Discoveries`, and hands back to the
orchestrator with an artefact list. It does **not** mark tasks `Done` and
**never** talks to the user.

## When to use

- Loaded by the `implementer` agent on every dispatch.
- Consulted at the start of an attempt and again at the hand-off step.

## Per-attempt protocol

### 1. Read the dispatch brief

The orchestrator passes you:

- Plan file path (`.plans/<slug>.md`).
- Task ID (e.g. `1.2`).
- Attempt number (1, 2, or 3).
- (Retries only) the previous attempt's FAIL feedback from the Review log.

### 2. Read shared context — only what you need

Open the plan file and read these sections only:

1. The assigned task block (`### Task <id>: <name>` and everything under it).
2. `## Context` (one-paragraph framing).
3. `## Discoveries` (entire section — it's the shared knowledge log).
4. On retry: the latest Review log entry under your task. This is the
   reviewer's actionable feedback — read it carefully.

Do **NOT** read:

- Other task blocks (you don't need them; coupling between tasks is
  expressed via `Depends on:` and Discoveries, not implicit reads).
- Other phases (irrelevant to this attempt).
- Previous attempts' Review logs beyond the latest (the latest contains the
  current feedback; older logs are noise).

### 3. Plan the edit before touching files

Write yourself a short mental plan:

- What files am I going to edit?
- What's the smallest change that makes the AC pass?
- Are there sibling examples in Discoveries I should mirror?

If anything is unclear (an unfamiliar API, an unknown sibling pattern,
"how is this done elsewhere"), **dispatch the researcher** per
`../researching/SKILL.md`. Then append the researcher's findings to
`## Discoveries` before continuing.

### 4. Mark `In progress`

Update the task's `**Status:**` line in the plan file:

```
**Status:** In progress
```

### 5. Make minimal edits

- **Touch the minimum number of files.** Each extra file is review surface
  for the reviewer and a chance for an unrelated regression.
- **No drive-by refactors.** If you see something else worth fixing,
  append a Discovery line about it; don't edit it.
- **Match local conventions.** Sibling files (from Discoveries) dictate
  formatting, naming, error handling, log style. Don't introduce a new
  pattern for a one-off task.
- **No new dependencies** unless the task explicitly authorises them.
- **No fallbacks, no try/except-then-swallow, no silent retries** as a
  way to make AC pass. If an AC fails because of an underlying bug, that's
  a real problem — surface it via the artefact list, not hide it.

### 6. Self-check `[Fast]` AC

Run every `[Fast]` AC for this task yourself before handing off. The
reviewer will run them again with fresh judgement, but failing them
yourself means you're handing off broken work.

- Run **`Must`-priority** `[Fast]` AC for sure — they're what the
  reviewer will FAIL on.
- Run **`Should`-priority** `[Fast]` AC too — a `Should` failure
  doesn't FAIL the task, but the orchestrator surfaces WARNs at the
  phase checkpoint, so you should know about them now.
- **`Could`-priority** AC are informational; you may skip self-check.

Record exit codes / outputs as you go — you'll include them in the
artefact list.

Do **NOT** run `[Full]` AC yourself — they're the reviewer's job at
the finalising attempt. Running them now wastes time. Do **NOT** run
`[Journey]` AC — they only exist in phase Definition of Done blocks
and are dispatched to the tester by the reviewer.

### 7. Append durable findings to `## Discoveries`

Anything you learned while implementing that future agents (including the
reviewer this attempt) shouldn't have to re-discover goes in
`## Discoveries`:

```markdown
- [implementer · 2026-06-10] `Foo.bar()` is called from `cli.py` and `web/api.py` (both use the default-arg path); changing its signature requires updating both.
- [implementer · 2026-06-10] `pytest` requires `PYTHONPATH=src` from repo root; otherwise imports fail with `ModuleNotFoundError`.
```

Rules of thumb for "is this Discovery-worthy?":

- **Yes** if a future agent would otherwise re-search for it.
- **Yes** if it contradicts an assumption you started with.
- **No** if it's specific to this task's diff (that's just the diff).
- **No** if it's an opinion. Discoveries are facts.

### 8. Mark `Awaiting review`

Update the task's `**Status:**` line:

```
**Status:** Awaiting review
```

Do **NOT** write to the Review log. Do **NOT** mark the task `Done`. Those
belong to the reviewer and orchestrator respectively.

### 9. Return an artefact list

Reply to the orchestrator with a compact structured artefact list — this
is your only output:

```markdown
**Implementer artefacts — Task <id> attempt <N>:**

- **Files touched:**
  - `path/to/file1.py` (+12 / -3 lines)
  - `path/to/file2.md` (new file, 24 lines)
- **Commands run (self-check):**
  - `pytest tests/test_foo.py::test_bar` → exit 0
  - `ruff check src/foo.py` → exit 0
- **[Fast] AC self-check:**
  - AC #1 [Must]   [Fast]: PASS
  - AC #2 [Should] [Fast]: WARN (non-blocking, exit 1: "<one-line reason>")
- **Discoveries appended:** 2 (see `## Discoveries`).
- **Open notes for reviewer:** <one short line if anything's worth flagging — or "none">.

Status set to: `Awaiting review`.
```

If you couldn't make a `Must`-priority `[Fast]` AC pass yourself,
still hand off — but flag it clearly:

```markdown
- **[Fast] AC self-check:**
  - AC #1 [Must] [Fast]: PASS
  - AC #2 [Must] [Fast]: FAIL — `pytest ... ::test_bar` exited 1: <one-line error>
```

The reviewer will independently confirm and emit a FAIL verdict; the
orchestrator handles the retry.

## Engineering discipline rules

These apply on every attempt, not just retries.

### No try/except / fallback / skip / cast / retry / timeout-bump as a fix

Before any of these:

```python
try:
    ...
except SomeError:
    fallback()
```

Ask yourself five why's. Why does `SomeError` happen here? If the answer
is "I don't know" or "to make the AC pass", you're hiding the bug. Real
fix or honest FAIL — never a swallow.

### No banned phrases in your output

Avoid: "I would suggest", "should work", "may need", "appears to",
"likely", "left as future work", "for now". These hide uncertainty that
the reviewer needs to see. If you're uncertain, say so concretely:
"I'm not sure whether `Foo.bar()` is the right API; researcher confirmed
two call sites but I haven't run them."

### No within-surface punts

If the task is to fix the parser and the parser also has a bug, fix it
(it's within the task surface). If the task is to fix the parser and the
*tokenizer* has a bug, that's cross-surface — flag in Open notes, don't
silently expand scope.

### Persistence budget

Three attempts per implementation cycle is your budget. If two attempts
hit the same wall, the orchestrator will escalate via adaptive retry. Don't
silently try a fourth approach — return an honest FAIL.

## Pitfalls

- **Reading the whole plan file.** Wastes context. Read only what step 2
  lists.
- **Touching files outside the task description.** Counts as scope creep.
  If the only way to make the AC pass is to touch out-of-scope files,
  flag it in Open notes — the reviewer will likely emit `PLAN_WRONG`.
- **Skipping the self-check** because "this is obviously right." It's not.
  Run them. Cheap.
- **Forgetting `## Discoveries` updates.** Every retry that doesn't append
  to Discoveries makes the next retry start from the same blind spot.
- **Writing to the Review log.** That's the reviewer's surface only.

## Checklist (every attempt, before returning)

- [ ] Read only assigned task + Context + Discoveries (+ latest Review log on retry).
- [ ] Dispatched researcher for anything broad or unfamiliar.
- [ ] Edited the minimum number of files.
- [ ] Ran all `Must` and `Should` `[Fast]` AC and recorded exit codes.
- [ ] Did NOT run `[Full]` AC (reviewer's job).
- [ ] Did NOT run `[Journey]` AC (tester's job, dispatched via reviewer).
- [ ] Appended durable findings to `## Discoveries`.
- [ ] Set Status to `Awaiting review` (did NOT set Done).
- [ ] Did NOT write to Review log.
- [ ] Did NOT contact the user directly.
- [ ] Returned a structured artefact list.

## References

- `../plan-file-format/SKILL.md` — Status vocabulary, AC tier semantics,
  Discoveries format.
- `../researching/SKILL.md` — when and how to dispatch the researcher.
- `../reviewing-acceptance-criteria/SKILL.md` — what the reviewer will
  check (so you know what to self-check).
- `../amending-plans/SKILL.md` — the `PLAN_WRONG` triggers that apply if
  you discover the task itself is mis-specified.

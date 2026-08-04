---
name: refactoring-safely
description: Use this skill when changing the shape of existing code — including a refactor done to make a task tractable — it enforces the separate-steps rule (never mix structural and behavioural change), the green-before-and-green-after protocol, characterization tests for untested legacy code, safe seam-creation techniques, and the scope discipline that keeps a refactor from swallowing the task.
---

# Refactoring Safely

**Refactoring is changing structure without changing behaviour.** If
behaviour changes, it is not a refactor — it is a rewrite wearing a
refactor's name, and it will be reviewed and trusted as though it were
safe. That mislabelling is where the damage comes from.

## When to use

Whenever you reshape existing code: extracting a function, moving code
between modules, renaming across call sites, introducing an interface, or
untangling something so the real task becomes tractable.

## The rule that prevents most damage

**Never mix a refactor and a behavioural change in the same step.**

Do them as separate steps, each with its own green test run:

```
1. refactor        -> tests green (unchanged tests, unchanged assertions)
2. change behaviour -> tests updated, green
```

Why this matters concretely: when a mixed step goes red, you cannot tell
whether you broke the structure or the behaviour, so you debug both at
once — and when it goes *green* while being subtly wrong, nobody looks,
because "it was just a refactor". Separate steps make each one reviewable
and each failure attributable.

Commit them separately if the repo uses commits. A diff that is 400 lines
of movement plus 5 lines of logic is unreviewable; split, and the 5 lines
get the attention they deserve.

## The protocol

1. **Green before.** Run the suite first. If it is already red, you have
   no baseline — fix or quarantine the failure, or report it, before
   refactoring. Refactoring on a red suite is working blind.
2. **Know what is covered.** If the code you are reshaping has no tests,
   you have no safety net. Write characterization tests first (below).
3. **Small moves.** One extraction, one rename, one move at a time.
   Re-run after each. A refactor that goes red after ten changes costs
   ten times more to diagnose than one that goes red after one.
4. **Prefer automated refactorings** — IDE/tool rename and extract — over
   hand-editing. Tools do not typo.
5. **Green after, with the same tests.** This is the proof. If you had to
   change an assertion to keep it green, you changed behaviour. Stop and
   reclassify the work.

## Characterization tests for untested code

When there are no tests and you must reshape the code, first pin down
what it *currently* does:

1. Write tests asserting current behaviour — **including behaviour that
   looks wrong.** You are recording reality, not endorsing it.
2. If you cannot predict the output, run the code, observe it, and assert
   the observed value. That is legitimate here, and only here — the goal
   is a tripwire, not a specification.
3. Note any behaviour you believe is a bug. **Do not fix it in the
   refactor.** Report it; fix it as a separate, deliberate change with
   its own test.
4. Now refactor, with the characterization tests as your net.

This is the one context where "assert whatever it returns today" is
correct. In new code it is an anti-pattern — see
`../testing-changed-code/SKILL.md`.

## Creating a seam safely

To make untestable code testable — the usual reason a task needs a
refactor at all:

1. Identify the volatile dependency (clock, network, DB, filesystem,
   randomness).
2. Extract it behind a narrow interface owned by the consumer, per
   `../solid-design/SKILL.md`.
3. Keep the existing constructor or call signature working by defaulting
   to the real implementation. Existing callers must not change.
4. Inject a fake in tests.

Steps 1-3 are pure structure. Behaviour changes come after, separately.

## Parallel change, for contracts you cannot break atomically

When a signature, schema, or format has callers you cannot update in one
step:

1. **Expand** — add the new form alongside the old. Both work.
2. **Migrate** — move callers over, one at a time, each verified.
3. **Contract** — remove the old form once nothing uses it. Grep to
   confirm, do not assume.

Slower, and the only safe way across a boundary you do not fully own.

## Scope discipline

A refactor is justified when it is **necessary for the task**, or when it
is a small, obvious cleanup **in code you are already changing**.

It is not justified because the code offends you. The dangerous failure
mode is the refactor that swallows the task: the user asked for a bug fix
and received a 900-line restructuring they did not ask for, cannot
review, and must now trust.

- Confine the refactor to what the task needs.
- If the necessary refactor is large, **take it back to the gate** — per
  `../triaging-and-planning/SKILL.md` — and let the user decide whether
  to pay for it now.
- Improvements you spot but do not need: collect them, report them, do
  not act on them uninvited.

## Checklist

- [ ] Test suite green *before* the refactor started, with the result
      cited.
- [ ] The code being reshaped has real coverage, or characterization
      tests were written first.
- [ ] Structural and behavioural changes are in separate steps, each with
      its own green run.
- [ ] No test assertion was changed to keep the refactor green.
- [ ] Moves were small and verified incrementally.
- [ ] Public contracts preserved, or changed via expand/migrate/contract
      with all callers found by grep.
- [ ] Bugs discovered during the refactor were reported, not silently
      fixed inside it.
- [ ] Refactor scope is limited to what the task required; anything
      larger went back to the gate.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Skills: https://code.claude.com/docs/en/skills

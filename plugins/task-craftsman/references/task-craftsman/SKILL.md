---
name: task-craftsman
description: Use this skill as the entry point for the task-craftsman agent — it defines the end-to-end workflow (understand, triage, gate, implement, test, self-review, report) and the Definition of Done a task must meet before the agent may claim completion. Read it at the start of every task, and read it again before reporting done.
---

# Task Craftsman

You take **one task** from intake to done at a senior developer's standard.
This skill is the spine; the other reference skills are the muscle.

## When to use

Always, at the start of a task, and again before you report it complete.

## The loop

```
understand -> triage -> [gate, if non-trivial] -> implement -> test -> self-review -> report
```

The loop is not strictly linear. Implementing teaches you things. When it
teaches you that the plan was wrong, **stop and say so** — go back to the
gate with what you learned rather than quietly building something the user
did not approve.

## Understand (before any edit)

You cannot write code that belongs in a codebase you have not read.

1. **The task.** What is the observable change in behaviour? If you cannot
   state it in one sentence, you do not understand it yet.
2. **The landing zone.** The target files, their callers, their existing
   tests.
3. **The nearest precedent.** Find the closest thing this codebase already
   does and copy its shape. This is the single highest-value habit — it
   makes your code look native instead of imported.
4. **The mechanics.** How do you build, lint, and test? Find the real
   commands (`package.json` scripts, `Makefile`, `pyproject.toml`, CI
   config). Run the suite once **before** you change anything, so you know
   which failures are yours and which were already there.

A pre-existing red suite is a finding you report at the gate, not a thing
you silently inherit or silently fix.

## Gate

Non-trivial work stops for approval exactly once, before product code is
written. See `../triaging-and-planning/SKILL.md` for the triage rule and
the required plan contents.

## Implement

Small steps, each one defensible. Doctrine lives in
`../solid-design/SKILL.md` and `../clean-code/SKILL.md`; structural change
to existing code follows `../refactoring-safely/SKILL.md`.

The rule that prevents most disasters: **never mix a refactor with a
behavioural change in the same step.** Reshape with tests green, then
change behaviour, then make tests green again. When something breaks you
will know which of the two did it.

## Test

Per `../testing-changed-code/SKILL.md`. The bar is coverage of *what you
changed*, not a global percentage.

## Self-review

Read your own diff top to bottom as the reviewer would, against
`../complete-code/SKILL.md`. You will find something. You always do.

## Definition of Done

Every box must be honestly ticked. If one cannot be, the task is not done
and you say which one and why.

- [ ] The task's stated behaviour is implemented, not approximated.
- [ ] Every changed or added behaviour has a test that fails if you revert
      the change.
- [ ] The full test suite runs green — command and exit code cited.
- [ ] The linter / formatter / type-checker runs clean — command and exit
      code cited.
- [ ] No `TODO`, stub, dead code, commented-out block, or debug print
      remains in the diff.
- [ ] Errors are handled deliberately; nothing is silently swallowed.
- [ ] The diff contains nothing unrelated to the task.
- [ ] Names, structure, and style match the surrounding codebase.
- [ ] Public API changes are documented in whatever form this repo uses.
- [ ] The report states what changed, why, what was verified with which
      command, and what was left out of scope.

## Report

Facts, in this order: what changed and why; decisions and trade-offs;
tests added and what each protects; verification commands with exit codes;
out-of-scope items and problems noticed but not fixed.

## Banned phrases

"Should work", "appears to", "likely fine", "for now", "left as future
work", "this is probably covered", "tests pass" (without a command and
exit code). Each one substitutes confidence for evidence. Run the check
and cite it, or name the gap explicitly.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Subagents: https://code.claude.com/docs/en/sub-agents
- Skills: https://code.claude.com/docs/en/skills
- Plugins: https://code.claude.com/docs/en/plugins

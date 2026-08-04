---
name: testing-changed-code
description: Use this skill whenever writing tests for a task — it defines the coverage bar (every changed behaviour has a test that fails if the change is reverted), what to test at which level, how to write assertions that actually catch regressions, the mutation-thinking self-check, and the rules against weakening tests or testing implementation details.
---

# Testing Changed Code

The bar is not a coverage percentage. It is this:

> **For every behaviour you added or changed, there is a test that fails
> if you revert the change.**

A test that passes both before and after your change tests nothing about
your change. Coverage metrics do not catch this; only asking the question
does.

## When to use

On every task that changes behaviour, which is nearly all of them.

## Conform first

Find the existing tests and copy their shape: framework, file location,
naming, fixture and factory helpers, setup/teardown style, how they fake
I/O. A test written in a foreign style is friction for every future
reader, however good it is in isolation.

Never introduce a second test framework or a second mocking library
because you prefer it.

## What to test, at which level

Choose the **cheapest level that can actually fail** for the behaviour in
question.

- **Unit** — pure logic, branches, boundaries, error mapping. Fast, most
  of your tests. If a unit test needs heavy mocking to exist, that is a
  design signal (see `../solid-design/SKILL.md`), not a reason for more
  mocks.
- **Integration** — the seams you changed: real DB, real HTTP handler,
  real serialization. This is where wiring bugs live, and unit tests
  systematically cannot see them.
- **End-to-end** — the one critical path a user takes through the change.
  Expensive and flaky; keep them few and meaningful.

Test **through the public interface**. Tests bound to private helpers
break on every refactor and stop anyone from improving the code — they
convert your test suite from an asset into a tax.

## Coverage for a change

For each changed behaviour, cover:

1. **Happy path** — the behaviour the task asked for, asserted on its
   real output.
2. **Boundaries** — first, last, zero, one, empty, max, exactly-at-limit.
   Off-by-one is the most common bug in existence and the cheapest to
   catch here.
3. **Error paths** — each way it can fail, asserting the *specific* error
   and its message or type, not merely "it threw".
4. **The rejected input** — malformed, absent, wrong type, unauthorized.
5. **A regression test for any bug this task fixes.** Write it first,
   watch it fail for the right reason, then fix. A bug fix without a
   failing-first test is an unverified claim.

## Assertions that catch regressions

- **Assert on values, not on shapes.** `expect(total).toBe(1250)` beats
  `expect(total).toBeDefined()`. A truthiness assertion passes for almost
  every wrong answer.
- **Assert the whole relevant result** where practical, so an unexpected
  extra field or dropped field is caught.
- **Assert on observable behaviour and side effects** — what was written,
  what was sent, what was returned — not on how many times an internal
  method was called. Call-count assertions on internals test your
  implementation, not your program.
- **One reason to fail per test.** When it goes red, the name should tell
  you what broke without opening the body.
- **Name tests by behaviour**: `refunds_are_rejected_after_30_days`, not
  `test_refund_2`.

## Determinism

Flaky tests are worse than no tests — they train everyone to ignore red.

- No real time: inject the clock. Never assert on `now()`.
- No real network, no real randomness: inject or seed them.
- No dependence on test execution order or on state left by another test.
- No `sleep` to wait for async work: await the actual signal.
- Clean up what you create.

## The self-check: mutation thinking

Before you call the tests done, for each changed function ask:

> If I inverted this condition, changed this `<` to `<=`, returned a
> hard-coded value, or deleted this line — would a test go red?

If no, you have coverage of *execution* but not of *behaviour*. That is
the exact gap a coverage percentage hides. Write the missing assertion.

## Running them

Run the **full suite**, not just your new file — your change may have
broken something elsewhere, and that is precisely what the suite is for.
Capture the exact command and its exit code; both go in your report.

Run the linter and type-checker too. Cite those as well.

If the suite was already red before your change, say so explicitly and
distinguish pre-existing failures from yours. Never let an inherited
failure be mistaken for one you caused, or vice versa.

## Prohibitions

- **Never weaken a test to make it pass.** Loosening an assertion,
  deleting a case, or adding a skip to reach green is falsifying the
  result. A red test means the product code or your understanding is
  wrong — fix the real thing.
- **Never assert something you did not verify.** Do not write an expected
  value by copying whatever the code currently returns without checking
  that it is *correct*. That locks in the bug.
- **Never claim green without running it.** Cite the command and exit
  code, always.
- **Do not delete or skip a failing existing test** because it is
  inconvenient. If it is genuinely obsolete because of an approved
  behaviour change, say so explicitly in your report and explain why.

## Checklist

- [ ] Framework, location, naming, and fixtures match existing tests.
- [ ] Every changed behaviour has a test that fails if the change is
      reverted.
- [ ] Happy path, boundaries, error paths, and rejected input covered.
- [ ] Every bug fixed has a regression test that was seen to fail first.
- [ ] Assertions check concrete values and observable side effects, not
      truthiness or internal call counts.
- [ ] Tests are deterministic: clock, randomness, and network injected.
- [ ] Mutation self-check applied to each changed function.
- [ ] Full suite plus linter and type-checker run; commands and exit codes
      captured.
- [ ] Pre-existing failures identified and reported separately.
- [ ] No test weakened, skipped, or deleted to reach green.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Skills: https://code.claude.com/docs/en/skills

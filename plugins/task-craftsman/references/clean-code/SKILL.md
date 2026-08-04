---
name: clean-code
description: Use this skill whenever writing or editing code — it covers naming, function size and shape, comments that earn their place, error handling, duplication versus coupling, and the codebase-conformance rule that overrides personal style preferences. Apply it while writing, not as a separate cleanup pass.
---

# Clean Code

Code is read far more often than it is written. Optimise for the reader
who arrives in six months with no context — often you.

Apply this **while writing**. A cleanup pass at the end is a pass you will
skip when the task runs long.

## When to use

Every time you write or edit code.

## Rule zero: conform to the codebase

The surrounding code's conventions beat every preference below. If the
repo uses `snake_case`, so do you. If it returns result objects instead of
throwing, so do you. If its tests use a style you dislike, use it anyway.

**Consistency is worth more than any individual improvement.** A file
written in two styles is harder to read than a file written entirely in
the worse one. If a convention is actively harmful, raise it — do not
silently deviate.

## Naming

Names are the primary documentation. Most "needs a comment" moments are
really "needs a better name".

- **Reveal intent.** `elapsedDays` beats `d`. `isEligibleForRefund` beats
  `check`.
- **Say what, not how.** `activeUsers`, not `userArrayFiltered`.
- **Length tracks scope.** A loop index may be `i`; a module-level export
  may not.
- **Booleans read as predicates**: `isActive`, `hasPermission`,
  `canRetry`.
- **Functions are verbs; values are nouns.** A function named `data` or a
  variable named `process` is a bug in waiting.
- **One word per concept.** Do not mix `fetch`, `get`, and `retrieve` for
  the same operation.
- **No disinformation.** `userList` that is a map is worse than `users`.
- **Encode units and currency**: `timeoutMs`, `priceCents`. Unit
  ambiguity is a real and recurring source of production bugs.

## Functions

- **One level of abstraction per function.** Mixing high-level policy with
  byte-fiddling in one body forces the reader to context-switch mid-read.
- **Small enough to hold in your head.** If you need a comment to mark
  sections inside a function, those sections are the functions you should
  extract.
- **Few parameters.** Past three, group them into a named object. A
  boolean parameter is a smell — `render(true)` is unreadable at the call
  site; prefer two named functions or an enum.
- **No output parameters.** Return values.
- **Command/query separation.** A function either does something or
  answers something. One that does both surprises its callers.
- **Guard clauses over nesting.** Handle the exceptional case and return
  early; keep the happy path at the left margin. Deep nesting is the most
  reliable readability killer there is.
- **No side effects the name does not promise.** `validateUser` must not
  create a session.

## Comments

A comment is a small failure — it means the code could not say it itself.
Some are still necessary.

**Earn their place:** *why* a non-obvious decision was made; a link to a
spec, RFC, ticket, or bug; a warning about a real consequence; a note on
why the obvious approach does not work here; genuinely required legal or
API-doc text.

**Delete on sight:** restating the code (`// increment i`); commented-out
code (the VCS has it); changelog comments (the VCS has that too); banner
blocks separating sections that should be functions; stale comments that
now contradict the code.

**A wrong comment is worse than no comment** — readers trust it, and it
lies. When you change code, update or delete its comments in the same edit.

## Error handling

- **Never swallow.** An empty `catch` destroys the information needed to
  diagnose the failure. If you truly intend to ignore an error, say why in
  a comment — that is a comment that earns its place.
- **Catch narrowly.** Catch what you can actually handle; let the rest
  propagate.
- **Preserve the cause.** Wrap with context, keep the original as the
  cause. Never replace a stack trace with a string.
- **Messages state what failed and with what input** — enough to diagnose
  without a debugger. Never leak secrets or PII into them.
- **Fail fast** on programmer error; **handle gracefully** on expected
  operational error. Know which one you are looking at.
- **No error-code returns mixed with exceptions** in one codebase. Follow
  the local convention.

## Duplication

DRY is about **knowledge**, not characters. Two fragments that look alike
but change for different reasons are *coincidental* duplication —
merging them couples two independent things and the next change will have
to tear them apart, usually via a boolean parameter bolted onto the
"shared" function.

- Duplicated **business rule or constant**: extract, always.
- Duplicated **shape**, different reason to change: leave it. Wait for a
  third occurrence before deciding it is a real pattern.

**Prefer a little duplication to the wrong abstraction.** Duplication is
visible and cheap to fix; a wrong abstraction hides and spreads.

## Structure

- Keep related things close: a function's helpers near it, a module's
  tests where this repo puts tests.
- Order top-down — the caller above the callee — so a file reads like
  prose.
- Minimise mutable state and shared state. Prefer pure functions where
  practical; they are trivially testable.
- Immutable by default; make mutation explicit and local.
- Do not reach through objects (`a.b().c().d()`); ask for what you need.
- **No magic numbers or strings.** Name them.
- Keep the public surface minimal — export only what callers need.

## Checklist

- [ ] Style, naming, and idioms match the surrounding code.
- [ ] Every name reveals intent; no abbreviations that need decoding.
- [ ] Units and currencies encoded in names where ambiguous.
- [ ] No function mixes abstraction levels or needs internal section
      comments.
- [ ] Guard clauses used; happy path is not buried in nesting.
- [ ] No boolean or output parameters.
- [ ] Every comment explains *why*, or is deleted.
- [ ] No commented-out code, dead code, or debug prints.
- [ ] No swallowed errors; causes preserved; messages diagnosable and free
      of secrets.
- [ ] Duplication of knowledge extracted; coincidental duplication left
      alone.
- [ ] No magic numbers or strings.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Skills: https://code.claude.com/docs/en/skills

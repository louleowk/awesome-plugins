---
name: complete-code
description: Use this skill during self-review, before declaring a task done — it defines what "complete" means beyond "it compiles and the happy path works", covering unfinished-work smells, edge cases and error paths, observability, documentation, security and data safety, and the honest-reporting rule for anything left undone.
---

# Complete Code

Complete means **finished**, not "works on the input I tried". Incomplete
code passes review because reviewers check what is there, not what is
missing. This skill is about what is missing.

## When to use

During self-review, before you report a task done. Read your own diff
top to bottom against this.

## No unfinished work in delivered code

Every one of these is a defect, not a note:

- `TODO`, `FIXME`, `XXX`, `HACK` added by this task.
- A function that returns a placeholder value so the caller compiles.
- A branch that silently does nothing where it should do something.
- Commented-out code left "in case we need it".
- Debug prints, temporary logging, hard-coded test values, a stubbed URL.
- An empty `catch`.
- A test that asserts nothing, or is skipped without a stated reason.

The rule: **implement it, or state plainly that it is out of scope.** A
`TODO` shipped in a diff is a decision hidden from the reviewer. An
out-of-scope item named in your report is a decision the user gets to
make. The second is honest; the first is not.

## Edge cases and error paths

The happy path is the part you cannot forget. Walk the diff and ask, for
each new or changed behaviour:

- **Empty**: empty string, empty list, empty result set, zero.
- **Absent**: null / undefined / `None`, missing key, missing config,
  missing file.
- **Boundary**: first, last, off-by-one, min, max, exactly-at-limit.
- **Too big**: oversized input, very long string, pagination beyond the
  end, unbounded loop or allocation.
- **Wrong type or malformed input**, especially at trust boundaries.
- **Failure of every call you make**: what happens when the network call
  times out, the DB rejects, the file is unreadable, the parse fails?
- **Duplicate or repeated invocation**: is this idempotent? Should it be?
- **Concurrency**, if this code can run twice at once: shared state,
  race on read-modify-write, partial writes.
- **Ordering**: does this assume a sort order the source does not
  guarantee?

You do not need to *handle* every one — some are genuinely impossible
here. You do need to have **considered** each and made a deliberate
choice. An unconsidered edge case is the one that pages someone.

## Observability

Code that fails silently in production is incomplete.

- Failures are logged with enough context to diagnose: what operation,
  what identifiers, what the error was.
- Log levels are used honestly — an error the system recovered from is a
  warning, not an error.
- No secrets, tokens, passwords, or PII in logs or error messages.
- Follow this codebase's existing logging/metrics conventions; do not
  introduce a second mechanism.

## Documentation

- Public API changes reflected wherever this repo documents them —
  docstrings, type signatures, README, OpenAPI spec, changelog.
- New config keys or env vars documented with type, default, and whether
  they are required.
- New commands or scripts documented where the others are.
- No documentation contradicts the code after your change. Grep for the
  old name.

## Configuration and dependencies

- No hard-coded environment-specific values — URLs, paths, credentials,
  ports.
- New dependencies are justified, pinned per this repo's convention, and
  actually needed. Adding a package for something the standard library
  does is a cost with no benefit.
- Anything you added to config has a sane default or fails loudly at
  startup when missing. Failing at startup beats failing at 3am.

## Security and data safety

Not optional, and not only for "security tasks":

- Input from outside the system is validated at the boundary.
- Queries are parameterised; no string-built SQL, no shell interpolation
  of user input.
- Output is encoded for its destination (HTML, shell, SQL, log).
- Authorization is checked where the resource is accessed, not only in the
  UI.
- Secrets come from config, never from source.
- Destructive operations (delete, overwrite, migrate) are guarded and
  reversible, or the irreversibility is explicitly flagged to the user.

## Backwards compatibility

- Changed signature, route, schema, or serialized format: who else calls
  it? Grep and check. Update them or version the change.
- Data migrations work on existing production-shaped data, not just an
  empty database, and their rollback path is known.
- Removed public API is deprecated first if this repo has consumers you
  do not control.

## The honesty rule

If something on this list cannot be ticked, **the task is not silently
done.** Say which item, why, and what you recommend. An honest partial
result lets the user decide; a confident false "done" removes that choice
and is discovered later at higher cost.

## Checklist

- [ ] No TODO, stub, placeholder return, dead code, commented-out block,
      or debug print in the diff.
- [ ] Empty / absent / boundary / oversized / malformed inputs each
      considered and deliberately handled or deliberately excluded.
- [ ] Every external call's failure mode handled.
- [ ] Idempotency, concurrency, and ordering assumptions checked.
- [ ] Failures logged with diagnosable context; no secrets or PII in logs.
- [ ] Docs, config, and changelog updated; nothing now contradicts the
      code.
- [ ] No hard-coded environment values; new config documented and
      defaulted or fail-fast.
- [ ] Input validated, queries parameterised, output encoded,
      authorization enforced at the resource.
- [ ] Callers of any changed contract found and updated.
- [ ] Anything not done is named explicitly in the report.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Skills: https://code.claude.com/docs/en/skills

---
name: triaging-and-planning
description: Use this skill at task intake to decide whether the work is trivial (implement immediately, no approval gate) or non-trivial (design and plan first, then stop for user approval), and to author the plan when a gate is required. It defines the triage signals, the tie-breaker, and the mandatory contents of a plan.
---

# Triaging and Planning

The craftsman gates on judgement, not on ceremony. A one-line fix should
not cost the user a design review; a new abstraction should never be
built without one.

## When to use

At intake on every task, before any product-code edit.

## The triage

Classify the task, then act.

### Trivial — no gate, implement now

All of these are true:

- The change is confined to **one file**, or to a mechanical repetition of
  the same edit across a few files.
- It **introduces no new abstraction** — no new type, interface, module,
  service, or dependency.
- It **changes no public contract** — no signature, route, schema, config
  key, or serialized format that anything outside the file depends on.
- The **approach is obvious** and there is no meaningful alternative worth
  weighing.
- The **existing tests tell you whether you got it right**, or the test to
  add is equally obvious.

Typical: fixing an off-by-one, correcting a message string, adding a
missing null guard, tightening a type, adding a test for existing
behaviour, a rename confined to one module.

### Non-trivial — design, plan, and gate

**Any one** of these is enough:

- The change spans **multiple modules** or crosses a layer boundary.
- It introduces or reshapes an **abstraction** — a new interface, class,
  module, or seam.
- It changes a **public contract**: API signature, HTTP route, DB schema,
  event payload, config, or CLI surface.
- It adds a **dependency** or a new tool.
- There are **two or more defensible approaches** with a real trade-off.
- It touches **security, authentication, authorization, money,
  concurrency, or data migration**. These always gate, regardless of size.
- The task as written is **ambiguous** — you would have to guess intent.
- It requires a **refactor of existing code** to become tractable.
- You estimate **more than roughly an hour** of focused work.

### The tie-breaker

When you are genuinely undecided, **it is non-trivial.** Asking costs one
message. Building the wrong design costs the task, plus the user's trust.

Two corollaries worth internalising:

- **Ambiguity is always non-trivial.** A task you have to guess at is not
  small, however few lines it takes. Guessing intent is the most expensive
  mistake available to you.
- **Size is the weakest signal.** A three-line change to an auth check is
  non-trivial. A two-hundred-line mechanical rename is not.

## The plan (non-trivial only)

Short and concrete. A page, not a document. Vagueness in a plan is
deferred cost — every "as needed" is a decision you pushed onto your
future self mid-implementation, where it will be made worse and unnoticed.

Required sections:

1. **Goal** — the observable change in behaviour, in one or two sentences.
2. **Approach** — what you will do and *why this one*.
3. **Alternative considered** — at least one, with the trade-off that
   decided it. If there is genuinely no alternative, say that; do not
   fabricate a strawman.
4. **Changes** — real file paths and real signatures. Not "the relevant
   service" but `src/billing/InvoiceService.ts — add
   applyCredit(invoiceId, amount): Promise<Invoice>`. Mark each as
   new / modified / deleted.
5. **Test strategy** — what you will test, at which level, and what proves
   the goal is met.
6. **Out of scope** — what you are deliberately not doing. This is where
   you prevent the "while you were in there..." argument later.
7. **Risks and open questions** — anything that could invalidate the plan,
   and any question whose answer would change it.

## Asking questions

Ask only questions whose answer changes the design. Ask them **all at
once**, at the gate. Batch them; do not drip-feed.

If the answer would not change what you build, do not ask — decide, state
the decision in the plan, and move on. Asking the user to make decisions
that are yours to make is not diligence, it is abdication.

## After approval

Restate any amendment the user made, in your own words, before starting.
Then implement the plan you agreed to.

If implementation proves the plan wrong, **stop and return to the gate**
with what you learned. Do not silently build something else. A plan that
turned out to be wrong is a normal event; a plan that was silently
abandoned is a broken contract.

## Checklist

- [ ] Task classified trivial or non-trivial against the signals above.
- [ ] Undecided cases resolved as non-trivial.
- [ ] Ambiguous tasks treated as non-trivial regardless of size.
- [ ] For non-trivial: plan written with all seven sections, using real
      paths and signatures.
- [ ] All design-changing questions asked in one batch at the gate.
- [ ] No product code written before approval.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Skills: https://code.claude.com/docs/en/skills
- Subagents: https://code.claude.com/docs/en/sub-agents

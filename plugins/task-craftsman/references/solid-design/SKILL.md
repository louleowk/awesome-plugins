---
name: solid-design
description: Use this skill when a change introduces or reshapes a type, class, module, interface, or dependency — it explains how to apply the five SOLID principles as diagnostic tools for real code smells rather than as mandatory structure, and it defines the anti-over-engineering counterweight that stops SOLID from producing needless indirection.
---

# SOLID Design

SOLID is a set of **diagnostics**, not a target shape. Each principle names
a specific pain — a change that ripples further than it should, a
subclass that lies about its contract, a client dragged into a dependency
it never uses. Apply a principle when you can name the pain it cures.

Applying SOLID with no smell present produces indirection with no payer:
interfaces with one implementation, factories that construct one type,
layers that forward calls unchanged. That is not clean design; it is cost
without benefit, and it is the most common way SOLID is misused.

## When to use

When the change adds or reshapes a type, module, interface, or dependency
edge. Not for a change confined inside one existing function.

## Single Responsibility

**A module should have one reason to change.** "Reason to change" means a
stakeholder or a force — pricing rules, wire format, storage engine — not
"does one thing".

The smell: a class you keep editing for unrelated reasons. An
`OrderService` touched by the tax team, the email team, and the persistence
team has three reasons to change.

The fix: split along the axes of change, not along nouns. Splitting
`Order` into `OrderData` and `OrderLogic` usually creates two things that
change together — that is worse, not better.

The counterweight: a class doing three tightly-coupled things that always
change together is *cohesive*. Leave it alone.

## Open/Closed

**Open for extension, closed for modification.** In practice: adding a new
variant should not require editing a switch that lives in five files.

The smell: the same `switch`/`if` on a type tag repeated across the
codebase, and adding a case means finding all of them.

The fix: polymorphism, a strategy map, or a registry — so a new variant is
a new file plus one registration.

The counterweight: **one** switch in **one** place is fine. Do not build a
plugin architecture to avoid an if-statement. Wait for the third
occurrence; two is a coincidence, three is a pattern.

## Liskov Substitution

**A subtype must be usable anywhere its supertype is, without the caller
knowing.** This is the principle you break by accident and pay for later.

The smells:
- An override that throws `NotSupported`.
- An override that strengthens a precondition (rejects input the base
  accepted) or weakens a postcondition (returns less than the base
  promised).
- A caller doing `if (x instanceof Special)` to work around a subtype.
- The classic: `Square extends Rectangle`, where `setWidth` silently
  changes the height.

The fix: prefer composition. If the "is-a" relationship does not hold
behaviourally, it is not inheritance — model the difference explicitly
instead of hiding it behind a broken promise.

## Interface Segregation

**No client should depend on methods it does not use.** A fat interface
forces every implementer to stub methods it does not support — and every
stub is a Liskov violation waiting to happen.

The smell: implementations full of empty methods or `NotSupported` throws;
a test double that must fake fifteen methods to exercise one.

The fix: split by consumer. Define the narrow interface the *client* needs,
named for what the client wants (`OrderReader`), not for what the
implementation is.

The counterweight: do not split an interface whose methods are always used
together by every client.

## Dependency Inversion

**Depend on abstractions; let the high-level policy own the abstraction.**
The interface belongs to the consumer's module, not the implementation's.

The smell: business logic importing a database driver, an HTTP client, a
clock, or the filesystem directly — which is also why it is untestable
without heavy mocking.

The fix: inject the dependency behind an interface the policy defines.
Note the strongest practical signal: **if a unit test needs an elaborate
mock or a live resource, you have a dependency-inversion problem, not a
testing problem.**

The counterweight: not every dependency needs inverting. Standard library
types, value objects, and stable pure functions are fine to depend on
directly. Invert what is **volatile** (I/O, time, randomness, network,
third-party services), not what is stable.

## Deciding

Before adding any abstraction, answer:

1. **What smell does this cure?** Name it in one concrete sentence about
   this code. No name, no abstraction.
2. **Who is the second caller?** An interface with one implementation and
   no imminent second one is speculative. Note the exception: a seam
   introduced purely to make volatile I/O testable has a real second
   implementation — the test double. That is a legitimate payer.
3. **What does it cost?** Every indirection costs a reader one jump.
   Is the smell worse than the jump?

Prefer the simplest structure that removes the smell. Simple concrete code
is easy to abstract later; premature abstraction is expensive to unwind
because callers grow to depend on it.

## Checklist

- [ ] Each abstraction introduced cures a named, present smell.
- [ ] No interface has exactly one implementation without a stated reason
      (a test seam for volatile I/O counts).
- [ ] No subtype throws `NotSupported`, strengthens a precondition, or
      weakens a postcondition.
- [ ] No caller type-checks a subtype to work around its behaviour.
- [ ] No implementer is forced to stub methods it does not support.
- [ ] Volatile dependencies (I/O, time, randomness, network) are injected;
      stable ones are not gratuitously wrapped.
- [ ] The unit tests need no elaborate mocks and no live resources.
- [ ] Removing any layer you added would make the code worse, not simpler.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Skills: https://code.claude.com/docs/en/skills

---
name: designing
description: Use this skill when the designer agent is triaging whether an autonomous-builder goal needs a design doc and (when yes) authoring `.plans/<slug>-design.md`. Defines the SKIP / MINI / FULL triage rubric, the section templates for mini and full designs, the banned-content rules, and the reply contract the orchestrator validates against.
---

# Designing

The designer's job is to keep the autonomous-builder loop honest about
*when* a design step adds value, and to produce a focused design artefact
when it does. This skill is the canonical rubric — read it every dispatch.

## When to use

- Designer agent (`agents/designer.md`) is invoked by the orchestrator
  immediately after intake and before the planner.
- The orchestrator does NOT skip the designer for "small" goals; the
  designer itself is the agent that judges scope. Triage is cheap (a
  few file reads + the rubric below).

## The triage rubric

Walk the rubric **top-down**. SKIP gates first; if all SKIP gates pass,
the decision is SKIP. Otherwise check FULL gates; if any FULL gate
fires, the decision is FULL. Otherwise MINI.

### SKIP gates (all must pass)

A goal SKIPs the design step iff **all** of these are true:

- **One file or a tiny set of mechanical edits.** Single source file, or
  ≤3 files where the edit is the same shape repeated (rename, dependency
  bump, config tweak, formatting, doc-only change).
- **No new public interface.** No new exported function/type/route/CLI
  flag/event consumed by code outside the changed module. Adjusting
  internals counts as no-new-interface; adding a public function does not.
- **One obvious approach.** You can name how to do it in one sentence
  without saying "or we could…". If you have an "or we could", that's an
  alternative — go to MINI.
- **Sibling pattern exists.** A similar change has been done before in
  the same repo and you can cite the file:line. New patterns go to MINI
  or FULL.
- **Reversible without migration.** A `git revert` undoes it cleanly. No
  schema change, no data migration, no consumer-facing breakage, no
  feature flag.

If **any** SKIP gate fails, fall through to the FULL gates.

### FULL gates (any one fires)

A goal needs a FULL design iff **any** of these is true:

- **Cross-package or cross-service.** The change spans more than one
  top-level package, plugin, or service.
- **New public API or contract.** A new HTTP endpoint, gRPC method, CLI
  command surface, library export, plugin manifest contract, or event
  schema visible to other modules / teams / clients.
- **New or changed data model.** A new persistent schema, or a migration
  of an existing one. Includes file-format changes that downstream tools
  parse.
- **≥2 credible alternatives with material trade-offs.** Not "two ways to
  spell the same thing" — two genuinely different shapes (e.g. queue vs.
  webhook, polling vs. push, sync vs. async pipeline).
- **Hard to reverse.** Schema migration, deprecation cycle, breaking
  change with consumers, public release, or anything that requires
  coordinated rollout / rollback steps.
- **Cross-cutting concerns are first-class.** Security boundary change,
  privacy / PII handling, observability budget (new metrics or alarms
  load-bearing for an SLO), latency / throughput target, cost ceiling.

If no FULL gate fires but any SKIP gate failed, the decision is MINI.

### MINI is the default for "real but bounded"

MINI catches the middle: multi-file changes within one module, public-ish
internal interfaces (types others import within the same package), 1–2
alternatives worth comparing, reversible without a migration. Most
autonomous-builder goals that need design at all land here.

## Section templates

The designer writes `.plans/<slug>-design.md` to one of these templates.
If the workspace has the `amazon-doc-writer` plugin installed, its
`writing-mini-technical-design` and `writing-technical-design` SKILLs are
the enriched versions of these templates — prefer them when present.

### MINI template (≤2 pages, ~800–1,200 words)

```markdown
# Mini Design: <Change Name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** Draft

## Summary

<2–4 sentences. What is changing, why, what the outcome is. A reader who
stops here should understand the proposal.>

## Context

<1–2 short paragraphs. Current state, what hurts, what triggered this.
Cite file:line where relevant.>

## Goals and Non-Goals

**Goals**
- <2–4 measurable goals>

**Non-Goals**
- <explicit out-of-scope items>

## Proposed Change

<Narrative description. Cover whichever of these apply — if not applicable,
say so explicitly:
- behaviour change (user-visible or API-visible)
- data / schema change
- deployment / rollback plan
- observability change>

## Alternatives Considered

- **<Alt 1>** — <one sentence: what it is, why rejected, key trade-off.>
- **<Alt 2 (optional)>** — <one sentence.>

## Risks

- **<Risk>** — <mitigation>

## Rollout

<3–6 sentences. Stages, success signal, rollback trigger.>

## Open Questions

- <unresolved items — these will be surfaced to the user before planning if any block planning>

## Sources

- `<relative path>:<line>` — <what it provided>
- `<URL>` — <what it provided>
```

### FULL template (~6 pages body, plus Appendix)

```markdown
# Technical Design: <Capability / System Name>

**Slug:** <slug>
**Date:** <YYYY-MM-DD>
**Status:** Draft

## 1. Context and Problem

<2–4 paragraphs.>

## 2. Goals and Non-Goals

**Goals**
- <numbered, measurable>

**Non-Goals**
- <explicit out-of-scope>

## 3. Requirements

### Functional
- <what the system must do>

### Non-functional
- <latency, throughput, availability, cost, security, operability — with target numbers>

## 4. Proposed Design

<Lead with one-sentence summary, then the key insight that makes it work.>

### 4.1 High-level architecture
### 4.2 Key components
### 4.3 Data model and storage
### 4.4 APIs and contracts
### 4.5 Critical flows
### 4.6 Failure modes and recovery
### 4.7 Security and privacy
### 4.8 Observability
### 4.9 Deployment and rollout

(Skip subsections that are genuinely N/A, but say so explicitly — don't omit silently.)

## 5. Alternatives Considered

For each rejected alternative (≥2):

### 5.x <Alternative name>
<1–2 paragraphs: what it is, why considered, why rejected, key trade-off.>

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |

## 7. FAQ

> Hard questions a senior reviewer would ask.

## 8. Open Questions

- <unresolved items>

## 9. Appendix

<Detailed schemas, benchmarks, rejected-design walkthroughs.>

## Sources

- `<relative path>:<line>` — <what it provided>
- `<URL>` — <what it provided>
```

## Banned content (designer self-rejects)

The designer rejects (rewrites or removes) these in self-review:

**Banned tokens** (these belong in the plan, not the design):

- `Phase 1:`, `Phase 2:`, etc.
- `Task ` (any task numbering)
- `[Must]`, `[Should]`, `[Could]`
- `[Fast]`, `[Full]`, `[Journey]`
- `Acceptance criteria:`
- `Definition of Done:`

**Banned phrasings** (these paper over missing decisions):

- "we'll figure it out"
- "we'll iterate later"
- "the obvious approach is" (without naming the alternatives)
- "TBD" / "TODO" anywhere except in `## Open Questions`
- "appears to", "should work", "likely"
- "left as future work", "for now"
- "I would suggest", "you might want to"

If a section can't be written without one of these phrasings, the
underlying decision isn't made. Make the decision, or move the
unresolved item to `## Open Questions` explicitly.

## Reply contract (the validation block)

Every designer reply ends with the structured block defined in
`agents/designer.md` (Decision, Rationale, Artefact, Discovery seed,
Findings to harvest, Validation). The orchestrator validates:

- `Decision` is exactly one of `SKIP` / `MINI` / `FULL`.
- `Rubric trigger cited` is a verbatim string from this skill's rubric
  (one of the SKIP gates or FULL gates above, or "MINI default").
- `Artefact line count` ≥ 30 for MINI, ≥ 100 for FULL, 0 for SKIP.
- `Sibling citations` ≥ 2 for MINI/FULL.
- `Alternatives Considered` ≥ 1 for MINI, ≥ 2 for FULL, `n/a` for SKIP.
- `Banned tokens scanned: … none present` line is present.

If any of these fails, the orchestrator rejects the reply and
re-dispatches the designer with the failure as feedback.

## Designer ↔ planner hand-off

The designer's `## Findings to harvest` section is the planner's input
for `## Discoveries`. The orchestrator passes the findings to the
planner along with the goal text. The planner appends each finding as a
line tagged `[planner · <date> · seeded from designer]` (mirroring the
existing repo-memory seeding pattern in `planning-tasks/SKILL.md`
step 0).

For SKIP, the single-line Discovery seed is appended verbatim by the
planner with the `[designer · …] design-skipped: …` tag preserved — so
the next reflector can audit whether SKIPs were correct calls.

For MINI/FULL, the planner reads `.plans/<slug>-design.md` to inform
phase shape and Context, but does NOT copy design-doc body verbatim
into the plan. The plan and the design doc remain separate artefacts.

## Anti-patterns

- **Triage avoidance.** Returning "let me know if you want a design"
  instead of picking SKIP / MINI / FULL.
- **Implementation manual.** A "design" that's really a procedural
  walkthrough with no trade-offs. Per Ubl: would have been better to
  write the program directly. This is the SKIP signal.
- **Alternatives theatre.** Listing two trivially-different alternatives
  ("we could call it `parseFoo` or `parse_foo`") to satisfy the count.
  Alternatives must differ in shape or trade-off, not in spelling.
- **Goals without Non-Goals.** Always state both. Non-Goals are where
  mini designs most often go off the rails.
- **Pre-writing the plan.** Phase / Task / AC tokens in the design body.
  The plan file is the planner's artefact; the design doc is yours.
- **Skipping discovery.** Triaging "MINI" without reading any sibling.
  At least one sibling citation is mandatory for MINI/FULL.

## Checklist (designer self-review before returning)

- [ ] Triage applied top-down: SKIP gates checked first.
- [ ] Decision is one of SKIP / MINI / FULL — never absent.
- [ ] Rationale quotes ≥1 rubric trigger verbatim.
- [ ] For SKIP: Discovery seed is one line, dated today, cites SKIP gate.
- [ ] For MINI: design doc has Goals **and** Non-Goals, ≥1 Alternative,
      Rollout, Sources, ≤2 pages.
- [ ] For FULL: design doc has Non-functional targets, ≥2 Alternatives,
      Risks table, FAQ, Open Questions, Sources, body ~6 pages.
- [ ] No banned tokens (`Phase`, `Task `, `[Must]`, `[Fast]`, `[Full]`,
      `[Journey]`, `Acceptance criteria:`, `Definition of Done:`) in body.
- [ ] No banned phrasings ("we'll figure it out", "obvious approach",
      "TBD" outside Open Questions, etc.).
- [ ] `## Findings to harvest` lists all new file:line / URL facts the
      planner should seed into `## Discoveries`.
- [ ] Validation block populated; orchestrator can parse every field.

---
name: writing-technical-design
description: Use this skill when authoring an Amazon-style technical design document (a "6-pager" engineering design doc). It provides the full section template — context, goals/non-goals, requirements, proposed design, alternatives, risks, milestones, FAQ — and the quality bar. Load alongside the `amazon-writing-style` skill.
---

# Writing a Technical Design (6-pager)

An Amazon technical design is a narrative engineering document used to align
on, and get review for, a non-trivial technical proposal. It is typically read
silently at the start of a design review and discussed afterwards.

## When to use

- The user wants to propose, document, or review a non-trivial technical
  solution: a new service, a major refactor, a cross-team integration, a
  protocol/format change, etc.
- The user says "technical design", "design doc", "6-pager", "engineering
  design review", "RFC".

## Length budget

- ~6 pages of body (≈ 2,500–3,500 words), excluding appendix.
- FAQ is included in the 6 pages.
- Long schemas, ADRs, benchmark tables, and rejected designs go in the
  **Appendix**, which has no length limit but should be skim-friendly.

## Section template

```markdown
# Technical Design: <Capability / System Name>

**Author(s):** <names>
**Reviewers:** <names / roles>
**Date:** <YYYY-MM-DD>
**Status:** Draft | In Review | Approved | Superseded
**Audience:** <e.g. team, org, design review>

## 1. Context and Problem

<2–4 paragraphs. What system / customer / situation are we in today? What is
the problem and who feels it? Why now?>

## 2. Goals and Non-Goals

**Goals**
- <numbered, measurable goals>

**Non-Goals**
- <explicit things this design will NOT do>

## 3. Requirements

### Functional
- <what the system must do>

### Non-functional
- <latency, throughput, availability, durability, cost, security, compliance,
  operability — with target numbers where possible>

## 4. Proposed Design

<Lead paragraph: one-sentence summary of the design, then the key insight that
makes it work.>

### 4.1 High-level architecture
<Narrative description. Include or link a diagram. Identify components,
ownership boundaries, and data flow.>

### 4.2 Key components
<For each component: purpose, responsibilities, interfaces, dependencies.>

### 4.3 Data model and storage
<Schemas, partitioning, retention, consistency model, growth estimates.>

### 4.4 APIs and contracts
<External and internal interfaces. Versioning. Backwards-compatibility story.>

### 4.5 Critical flows
<Walk through the 2–4 most important request/data flows end-to-end.>

### 4.6 Failure modes and recovery
<What fails, how it is detected, how it is recovered. Blast radius. SLOs.>

### 4.7 Security and privacy
<AuthN/Z, data classification, PII handling, threat model summary.>

### 4.8 Observability
<Metrics, logs, traces, dashboards, alarms tied to SLOs.>

### 4.9 Deployment and rollout
<Environments, regions, feature flags, migration plan, rollback plan.>

## 5. Alternatives Considered

For each rejected alternative:

### 5.x <Alternative name>
<1–2 paragraphs: what it is, why it was considered, why it was rejected.
Include the key trade-off in one sentence.>

## 6. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| … | L/M/H | L/M/H | … | … |

## 7. Milestones and Plan

| Milestone | Scope | Target date | Exit criteria |
| --- | --- | --- | --- |
| M1 | … | YYYY-MM-DD | … |

<Include staffing assumptions and dependencies on other teams.>

## 8. FAQ

> Hard questions the design review will ask. Answer in prose.

**Q: Why not <obvious alternative>?**
A: …

**Q: How does this perform at <stated scale target>?**
A: …

**Q: What is the rollback story if <key risk> materializes?**
A: …

**Q: What is the operational cost (oncall, infra $) of this design?**
A: …

**Q: What changes for clients / dependent teams, and on what timeline?**
A: …

## 9. Open Questions

- <unresolved items and owner>

## 10. Appendix

- Detailed schemas, benchmark data, rejected-design walkthroughs, prior-art
  links.

## Sources

- `<relative path>` — <what it provided>
```

## How to apply

1. **Inventory sources.** Read every spec, ticket, prior design, runbook, and
   code path the user pointed at. Note: requirements, current architecture,
   data volumes, SLOs, prior decisions.
2. **Draft Goals + Non-Goals first.** This anchors the rest. Be explicit
   about what is out of scope.
3. **Pin the non-functional numbers** (latency, throughput, availability,
   cost) early. The design is judged against these.
4. **Write the Proposed Design in narrative**, not as a bulleted spec. Lead
   each subsection with its main claim, then justify it.
5. **Always include Alternatives Considered.** A design with no alternatives
   listed is not credible. Two or three is typical.
6. **FAQ is mandatory.** Pre-answer the toughest questions a senior engineer
   would ask. Include cost, rollback, scale, and the "why not X" for the most
   obvious alternative.
7. **Keep main body to ~6 pages.** Push detail to the Appendix.
8. Apply the `amazon-writing-style` self-review checklist.

## Common failure modes to avoid

- Starts with the solution. Always start with context + problem.
- Goals are unmeasurable ("improve reliability"). Use targets.
- No Non-Goals. Always state what you are *not* doing.
- Alternatives section is a single sentence dismissal. Each rejected
  alternative deserves a real treatment.
- FAQ answers easy questions only. Put the hard ones in.
- Diagrams without narrative. Every diagram needs prose around it.

## Checklist

- [ ] Goals and Non-Goals are explicit and measurable.
- [ ] Non-functional requirements have target numbers.
- [ ] Proposed design covers data model, APIs, critical flows, failure modes,
      security, observability, rollout.
- [ ] At least 2 Alternatives Considered with real trade-off analysis.
- [ ] Risks table with mitigations and owners.
- [ ] Milestones with exit criteria.
- [ ] FAQ covers cost, rollback, scale, and "why not <obvious alternative>".
- [ ] Body ≤ ~6 pages; detail pushed to Appendix.
- [ ] Sources listed; open questions called out.
- [ ] `amazon-writing-style` self-review checklist passes.

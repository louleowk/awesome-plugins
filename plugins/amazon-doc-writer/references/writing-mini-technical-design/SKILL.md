---
name: writing-mini-technical-design
description: Use this skill when authoring a short Amazon-style technical design — a 1–2 page "mini design" or design brief for a scoped change, small feature, or focused decision. Provides the trimmed section template and length budget. Load alongside the `amazon-writing-style` skill.
---

# Writing a Mini Technical Design

A mini design is the short form of the technical design doc. It is used when
the change is real enough to need written alignment, but small enough that a
full 6-pager would be overkill.

## When to use

- A scoped change to one service, a small new component, a focused refactor,
  a config/protocol tweak, an API addition.
- The user says "mini design", "1-pager", "2-pager", "design brief",
  "tech spec", "short design".

If the change touches multiple teams, introduces a new service, or has
material rollback/scale risk, use `writing-technical-design` (6-pager)
instead.

## Length budget

- **Hard ceiling: 2 pages** (≈ 800–1,200 words). Push everything else to an
  appendix or link out.
- FAQ is optional but recommended (3–5 questions).

## Section template

```markdown
# Mini Design: <Change Name>

**Author(s):** <names>
**Reviewers:** <names>
**Date:** <YYYY-MM-DD>
**Status:** Draft | In Review | Approved

## Summary

<2–4 sentences. What is changing, why, and what the outcome is. A reader who
stops here should understand the proposal.>

## Context

<1–2 short paragraphs. Current state, what hurts, what triggered this.>

## Goals and Non-Goals

**Goals**
- <2–4 measurable goals>

**Non-Goals**
- <explicit out-of-scope items>

## Proposed Change

<Narrative description of the change. Include the key interfaces, data, or
flow that change. One diagram max, only if it adds clarity. Call out:
- behavior change (user-visible or API-visible)
- data / schema change
- deployment / rollback plan
- observability change (new metrics, alarms)>

## Alternatives Considered

- **<Alt 1>** — <one sentence on what it is and why rejected.>
- **<Alt 2>** — <one sentence.>

## Risks

- **<Risk>** — <mitigation, owner>

## Rollout Plan

<3–6 sentences. Flag, stages, success signal, rollback trigger.>

## FAQ (optional)

**Q: <question>**
A: <prose>

## Open Questions

- <unresolved items>

## Sources

- `<relative path>` — <what it provided>
```

## How to apply

1. **Confirm scope is mini-sized.** If the change crosses service or team
   boundaries, has nontrivial migration, or its rollback is unclear, switch to
   the full `writing-technical-design` template.
2. **Lead with the Summary.** Many readers will only read it.
3. **Be explicit about Non-Goals** even in the short form — it's where mini
   designs most often go off the rails.
4. **Cover behavior, data, deploy/rollback, observability** in the Proposed
   Change. Skip the section if truly N/A, but say so.
5. **List at least one Alternative.** Even in a mini design.
6. **Stay under 2 pages.** Cut, don't shrink the font.
7. Apply the `amazon-writing-style` self-review checklist.

## Checklist

- [ ] Total length ≤ 2 pages.
- [ ] Summary stands alone and states the outcome.
- [ ] Goals and Non-Goals both present.
- [ ] Proposed Change addresses behavior, data, deploy/rollback, observability
      (or explicitly notes N/A).
- [ ] At least one Alternative Considered listed.
- [ ] Rollback plan and success signal stated.
- [ ] Sources listed; open questions called out.
- [ ] `amazon-writing-style` self-review checklist passes.

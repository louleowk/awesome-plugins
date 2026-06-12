---
name: writing-op1-narrative
description: Use this skill when authoring an Amazon OP1 (or OP2) annual operating plan narrative. Provides the section template — state of the business, goals, inputs/outputs, headcount, dependencies, risks — plus the multi-tab "Goals" structure and the bar for prior-year accountability. Load alongside the `amazon-writing-style` skill.
---

# Writing an OP1 / OP2 Narrative

OP1 and OP2 are Amazon's annual operating-plan cycles. The OP1 narrative is
the written companion to the team's goals tree and headcount ask, submitted
in the fall and refined in OP2 in the new year. It tells leadership: how the
business is doing, what we will commit to next year, what inputs we need to
hit those commitments, and what we will *not* do.

## When to use

- The user asks for an "OP1", "OP2", "annual plan", "operating plan
  narrative", "yearly goals doc", or "planning narrative".
- The deliverable is a written companion to a goals/headcount submission, not
  the goals spreadsheet itself.

## Length budget

- ~6 pages of narrative body.
- Detailed goal tables, headcount roll-ups, and per-input/output spreadsheets
  go in the Appendix.

## Section template

```markdown
# OP1 Narrative: <Team or Org Name> — <Plan Year>

**Author(s):** <names>
**Date:** <YYYY-MM-DD>
**Status:** Draft | In Review | Final
**Audience:** <e.g. parent org leadership>
**Plan year:** <YYYY>

## 1. State of the Business

<2–3 paragraphs. How did we do against last year's plan? Hit the headline
numbers up front — input metrics, output metrics, customer wins, customer
misses. Be honest about misses; this is the credibility floor for everything
below.>

### 1.1 Prior-year scorecard

| Last year goal | Target | Actual | Status | Comment |
| --- | --- | --- | --- | --- |
| <goal> | <#> | <#> | Hit / Partial / Miss | <one line> |

## 2. Strategic Context

<1–2 paragraphs. What changed in the customer, the market, or the broader
org's strategy that affects this plan? What tenets guide our choices?>

## 3. Goals for <Plan Year>

<Open with the headline: 1–2 sentences naming the year's top goal(s).>

### 3.1 Top-line outputs

<The 3–5 customer- or business-visible output metrics we are committing to.
Each: target number, units, baseline, and how it will be measured.>

### 3.2 Controllable inputs

<The input metrics we own that drive the outputs. For each: target, baseline,
the output it drives, and the team(s) accountable.>

### 3.3 Goal tree (summary)

<Narrative summary of the L1/L2/L3 goals. Full tree in Appendix.>

## 4. Initiatives

<For each major initiative we will fund:
- **What:** one sentence.
- **Why now:** what input/output it moves.
- **Headcount + cost:** rough numbers.
- **Year-end success criteria.**
Aim for 3–7 initiatives; if the list is longer, you are not prioritizing.>

## 5. What We Will NOT Do

<Explicit non-goals for the year. This is where OP1 narratives most often
underperform — be specific about what is being deferred or killed and why.
Name the initiatives, not categories.>

## 6. Headcount and Resourcing

<Summary of the headcount ask:
- Current headcount, end-of-year headcount, deltas by function.
- Top hires by role and target start quarter.
- Non-headcount cost asks (infra, vendor, contractor).
Tie each ask back to a specific initiative or goal in §4.>

## 7. Dependencies

<What we need from other teams to hit the plan. For each: team, ask,
criticality, and what we will do if it doesn't land.>

## 8. Risks

| Risk | Likelihood | Impact on plan | Mitigation | Owner |
| --- | --- | --- | --- | --- |

## 9. FAQ

> The questions leadership will ask in the read.

**Q: Why is <top goal> the right top goal vs <obvious alternative>?**
A: …

**Q: What is the input/output relationship behind <key metric>?**
A: …

**Q: What gets dropped if we get <N> fewer heads than asked?**
A: …

**Q: What is the rollback if <key initiative> isn't working by mid-year?**
A: …

**Q: How is this plan different from last year's, and what did we learn from
last year's misses?**
A: …

## 10. Open Questions

- <unresolved items>

## Appendix

- A. Full goal tree (L1/L2/L3)
- B. Per-initiative one-pagers
- C. Headcount detail by team and quarter
- D. Detailed input/output model

## Sources

- `<relative path>` — <what it provided>
```

## How to apply

1. **Anchor on prior-year performance first.** Leadership reads §1 with last
   year's plan open beside it. Misses must be named honestly with a one-line
   explanation, otherwise the rest of the doc loses credibility.
2. **Separate inputs from outputs.** Inputs are what the team controls;
   outputs are what customers/business see. State the causal model: "moving
   input X to N is expected to move output Y to M because…".
3. **Top goal first.** §3 should open with 1–2 sentences naming the year's
   top commitment, before any subsection.
4. **NOT-doing list is mandatory.** A plan without an explicit non-goals
   section is unfundable. Name the deferred initiatives specifically.
5. **Headcount ties to initiatives.** Each additional head should map to a
   §4 initiative; if it doesn't, justify or drop the ask.
6. **FAQ pre-empts the "what if you get less" question.** Always include
   the "what gets dropped if headcount is cut by N" answer.
7. Apply the `amazon-writing-style` self-review checklist.

## Common failure modes to avoid

- Prior-year scorecard is missing or softens misses. Be honest.
- Goals are output metrics only, with no input metrics. The team can't act
  on outputs directly.
- No non-goals listed. Always include them.
- Headcount asks are unanchored to specific initiatives.
- Dependencies section is missing or hand-wavy ("we'll align with platform
  team"). Name the team, the ask, the date, and the fallback.
- FAQ avoids the headcount-cut and rollback questions.

## Checklist

- [ ] Prior-year scorecard included with honest Hit/Partial/Miss labels.
- [ ] Top-line outputs and controllable inputs are clearly separated with
      targets, baselines, and a stated causal model.
- [ ] 3–7 funded initiatives with HC, cost, and year-end success criteria.
- [ ] Explicit "What we will NOT do" section with named initiatives.
- [ ] Headcount asks tied to specific initiatives.
- [ ] Dependencies list names team + ask + criticality + fallback.
- [ ] FAQ covers headcount-cut scenarios and mid-year rollback triggers.
- [ ] Sources listed; open questions called out.
- [ ] `amazon-writing-style` self-review checklist passes.
```

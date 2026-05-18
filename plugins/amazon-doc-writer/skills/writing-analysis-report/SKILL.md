---
name: writing-analysis-report
description: Use this skill when authoring an Amazon-style analysis report or deep-dive — investigating data, a system behavior, an incident pattern, a build-vs-buy question, or a market/competitor study, and reporting findings with evidence and recommendations. Load alongside the `amazon-writing-style` skill.
---

# Writing an Analysis Report

An analysis report answers a specific question with evidence. Unlike a design
doc (which proposes a solution) or a PR/FAQ (which pitches a product), an
analysis report ends in **findings + recommendations**, not a built thing.

## When to use

- The user asks for an "analysis", "deep dive", "investigation", "study",
  "report", "post-mortem write-up" (the narrative document, not the incident
  timeline itself), "build vs buy analysis", or "data analysis".
- The deliverable is a written conclusion grounded in data or source material.

## Length budget

- Body: ~4–8 pages. Variable, because evidence sections can be longer.
- Lead with a 1-page Executive Summary that stands on its own.
- Raw data, query listings, methodology details, and supplementary charts go
  in the Appendix.

## Section template

```markdown
# Analysis: <Question being answered>

**Author(s):** <names>
**Date:** <YYYY-MM-DD>
**Status:** Draft | Final
**Audience:** <e.g. leadership, team, partner team>

## Executive Summary

<1 page max. State:
1. The question being answered (one sentence).
2. The headline finding (one or two sentences).
3. The 2–4 supporting findings (each one sentence).
4. The recommended action(s) and the decision being requested.
A reader who stops here should know the answer and what to do.>

## Background

<Why we are doing this analysis now. What decision or context it informs.
Prior work, if any.>

## Question and Scope

- **Primary question:** <the one we are answering>
- **Secondary questions:** <bounded list>
- **In scope:** <…>
- **Out of scope:** <…>

## Methodology

<How the analysis was conducted: data sources used, time window, sample size,
queries or models, assumptions, known limitations. Reproducibility matters —
another engineer should be able to redo this from this section.>

## Findings

<One subsection per finding. Each subsection:
- Leads with the finding as a one-sentence claim.
- Supports it with data (table, chart reference, computed numbers with units
  and source).
- Notes the confidence level and any caveats.>

### Finding 1: <claim>
<evidence>

### Finding 2: <claim>
<evidence>

…

## Implications

<What these findings mean for the decision at hand. Tie each implication back
to a specific finding. Avoid restating findings.>

## Recommendations

<Numbered, action-oriented, each with an owner and a suggested timeline.>

1. **<Recommendation>** — <rationale, owner, timeline>
2. …

## Risks and Caveats

- **Data quality:** <what could be wrong>
- **Assumptions:** <which assumptions, if violated, would change the
  recommendation>
- **External factors:** <…>

## Alternatives Considered (if recommending an action)

- **<Alt>** — <why not chosen>

## Open Questions

- <items that still need investigation>

## Appendix

- A. Detailed methodology / queries
- B. Raw data extracts
- C. Supplementary charts and tables

## Sources

- `<relative path>` — <what it provided>
```

## How to apply

1. **Pin the question.** Write the primary question as one sentence before
   anything else. If you can't, ask the user to sharpen the ask.
2. **Inventory and read the source files.** Note which files are data
   (numbers), which are context (specs/docs), and which are prior analysis.
3. **Methodology before findings.** Write the Methodology section before the
   Findings so you don't quietly bend method to fit the answer.
4. **Findings are claims, not summaries.** Each finding starts with a
   one-sentence claim, then the evidence. If you can't state a claim, you
   don't have a finding — you have raw data; move it to the Appendix.
5. **Quantify with units and sources.** Every number must trace back to a
   source file, query, or computation in the Methodology / Appendix.
6. **State confidence and caveats.** Honest uncertainty is a feature, not a
   weakness.
7. **End with Recommendations**, each with an owner and a timeline, tied to
   the findings above.
8. **Executive Summary last.** Write it after the body so it accurately
   reflects what's there. It must stand alone.
9. Apply the `amazon-writing-style` self-review checklist.

## Common failure modes to avoid

- Findings that are actually summaries of source documents — restate as
  claims or drop them.
- Charts in the body with no narrative interpretation.
- Recommendations not tied to a specific finding.
- Methodology section is missing — readers can't tell if the analysis is
  trustworthy.
- Executive Summary buries the headline finding.

## Checklist

- [ ] Primary question stated in one sentence.
- [ ] Executive Summary stands alone and states the headline finding +
      recommendation.
- [ ] Methodology section is reproducible (sources, window, queries,
      assumptions, limitations).
- [ ] Each finding is a one-sentence claim followed by evidence with units
      and sources.
- [ ] Confidence and caveats stated for each finding.
- [ ] Recommendations are actionable, owned, and tied to findings.
- [ ] Risks/assumptions that would flip the recommendation are listed.
- [ ] Sources and open questions listed.
- [ ] `amazon-writing-style` self-review checklist passes.

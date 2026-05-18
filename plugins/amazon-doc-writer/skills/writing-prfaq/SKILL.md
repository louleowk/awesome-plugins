---
name: writing-prfaq
description: Use this skill when authoring an Amazon PR/FAQ (press release + frequently asked questions) document. It provides the section template, length budget, and the specific kinds of questions the External and Internal FAQs must answer. Load alongside the `amazon-writing-style` skill.
---

# Writing a PR/FAQ

A PR/FAQ is Amazon's working-backwards launch document. It starts with a mock
**press release** written as if the product/feature were already shipped, then
a **FAQ** that addresses the questions customers, leadership, and the team will
ask. It exists to force clarity on the customer value *before* any code is
written.

## When to use

- The user wants to pitch a new product, feature, or major capability.
- The user says "PR/FAQ", "press release", "working backwards", "launch doc".

## Length budget

- **Press Release:** ~1 page (≈ 350–500 words). One page, no more.
- **External FAQ:** 5–10 questions, ~1–2 pages.
- **Internal FAQ:** 10–20 questions, ~2–3 pages.
- **Total:** ~5–7 pages. Treat as a ceiling.

## Section template

```markdown
# PRFAQ: <Product or Feature Name>

**Author(s):** <names>
**Date:** <YYYY-MM-DD>
**Status:** Draft | In Review | Approved
**Audience:** <e.g. product leadership, launch team>

## Press Release

### <Headline — what the customer can now do>

**<City>, <Date>** — <One-sentence summary of the launch and the customer
benefit.>

<Paragraph 1: the customer problem, in the customer's words.>

<Paragraph 2: the solution — what is launching and how it solves the problem.>

<Paragraph 3: how it works, in plain language. No internal jargon.>

<Paragraph 4: customer quote — a realistic, attributable quote from a target
customer describing the benefit. Mark as `[Illustrative]` if not from a real
interview.>

<Paragraph 5: leadership quote — a short quote from the responsible exec
framing the strategic rationale. Mark as `[Illustrative]` if not real.>

<Paragraph 6: call to action — how/where the customer gets started, pricing
posture, availability.>

## External FAQ

> Questions a customer, journalist, or partner would ask after reading the PR.

**Q: <question>**
A: <direct, prose answer>

…

## Internal FAQ

> The harder questions: economics, build vs buy, dependencies, risk, scope,
> success metrics, what we are explicitly NOT doing.

**Q: Who is the customer, and what evidence do we have that they want this?**
A: …

**Q: What is the size of the opportunity (TAM / addressable users / revenue)?**
A: …

**Q: What does success look like in year 1? What metrics will we report?**
A: …

**Q: What are we explicitly NOT building in v1, and why?**
A: …

**Q: What is the build vs buy vs partner analysis?**
A: …

**Q: What are the top 3 risks and how will we mitigate them?**
A: …

**Q: What is the rough cost and timeline to launch?**
A: …

**Q: What dependencies on other teams / systems exist?**
A: …

**Q: How will we know to kill this if it isn't working?**
A: …

## Open Questions

- <thing the doc cannot answer yet and who owns resolving it>

## Sources

- `<relative path to source file>` — <what it provided>
```

## How to apply

1. **Read the sources first.** You need the customer, the problem, the
   proposed solution, and any data on demand or willingness-to-pay before you
   can write the PR. Take notes on each.
2. **Draft the headline.** It must be a benefit to the customer, not an
   internal capability name.
3. **Draft the PR in 4–6 short paragraphs.** Customer → problem → solution →
   how it works → customer quote → leadership quote → CTA. Keep it to one page.
4. **Generate the External FAQ.** Imagine a customer reading the PR cold. What
   would confuse them? What would they ask next? Answer each in 2–4 sentences.
5. **Generate the Internal FAQ.** Cover the list above at minimum. Add
   questions specific to the sources you read (e.g. data privacy if PII is
   involved, scaling if a hot path is touched, etc.). Answer each in 3–6
   sentences. Do not dodge.
6. **Mark illustrative quotes.** Any quote not sourced from a real customer or
   leader must be tagged `[Illustrative]`.
7. **Apply the `amazon-writing-style` self-review checklist** before
   delivering.

## Common failure modes to avoid

- Press release reads like a feature spec ("introduces a new microservice
  that…"). Rewrite from the customer's perspective.
- Internal FAQ ducks the hardest questions (cost, kill criteria, what's not in
  scope). Put them in and answer them.
- Numbers in the PR are unsourced. Move them to the FAQ with a citation, or
  remove them.
- The PR is longer than one page. Cut.

## Checklist

- [ ] PR is ≤ 1 page and leads with customer + benefit.
- [ ] At least one customer quote and one leadership quote (marked
      `[Illustrative]` if not real).
- [ ] External FAQ has 5–10 questions; Internal FAQ has 10–20.
- [ ] Internal FAQ covers: who is the customer, success metrics, what's NOT in
      v1, build/buy/partner, top risks, cost+timeline, dependencies, kill
      criteria.
- [ ] All numbers cited. Open questions and sources listed.
- [ ] `amazon-writing-style` self-review checklist passes.

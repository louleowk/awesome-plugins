---
name: amazon-writing-style
description: Shared style and quality-bar skill for Amazon-style internal docs. Use this whenever drafting a PR/FAQ, technical design, mini design, analysis report, or any other Amazon narrative document. It defines tone, structure, narrative-prose rules, the "so what" test, weasel-word bans, and the self-review checklist.
---

# Amazon Writing Style

Amazon's internal docs are **written narratives**, not slide decks. They are
read silently at the start of a meeting and then discussed. This skill captures
the conventions every Amazon-style doc must follow.

## When to use

- Drafting any document produced by the `amazon-doc-writer` agent.
- Reviewing or revising an existing draft to bring it up to bar.

## Core principles

1. **Customer first.** Open with the customer and the customer problem, not
   with the team, the technology, or the org chart.
2. **Working backwards.** Describe the desired end state, then explain how to
   get there. Especially for PR/FAQ and design docs.
3. **Narrative prose.** Use full sentences and paragraphs. Bullets are allowed
   only where the structure is genuinely a list (FAQ Q&A, success metrics,
   risks, alternatives considered).
4. **Data over adjectives.** Replace "fast", "scalable", "significant" with
   numbers, units, and a source. If you can't quantify, say so explicitly.
5. **One idea per paragraph.** Lead each paragraph with its point; the rest of
   the paragraph supports it.
6. **Short, declarative sentences.** Prefer active voice. Cut filler.
7. **Address the hardest questions head-on** in an FAQ section. Don't bury risk.

## Structural rules

- **Title** — one line, descriptive, includes the doc type
  (e.g. `PRFAQ: <Product Name>` or `Technical Design: <Capability>`).
- **Metadata block** at the top: author(s), date, status (Draft / In Review /
  Approved), and intended audience.
- **Section headings** are sentence-case and follow the order dictated by the
  doc-type skill. Do not invent new top-level sections without reason.
- **Length budget** is set per doc type (mini ≤ 2 pages, technical design ~6
  pages, PR/FAQ ~1 page PR + ~5 pages FAQ, analysis report variable). Treat
  this as a hard ceiling, not a target.
- **FAQ section** is mandatory for PR/FAQ and technical design. Each Q is a
  real question someone will ask in the read; each A is a direct answer in
  prose, not a deflection.
- **Appendix** holds anything that supports but doesn't belong in the main
  read (long tables, raw data, detailed schemas, alternative designs in full).

## Prose rules

- Lead each section with its key takeaway sentence ("BLUF" — bottom line up
  front).
- Quantify: prefer `"P99 latency is 180 ms (measured 2025-04-12, n=10k)"` over
  `"latency is low"`.
- Cite the source of every non-obvious number inline or under **Sources**.
- Define acronyms on first use. Avoid internal jargon the audience won't share.
- Use absolute dates (`2025-05-18`), not relative ones (`last quarter`).
- Use SI units and round consistently. State the unit (`120 ms`, `3.2 GB/s`).

## Words and phrases to avoid

Replace these with concrete claims:

- "robust", "seamless", "world-class", "best-in-class", "leverages",
  "synergies", "next-generation", "cutting-edge"
- "we believe", "it is felt that", "should be possible"
- "etc." at the end of a list — finish the list or call out what is omitted.
- "various", "several", "many" without a number.

Hedging is acceptable when honest (e.g. "We estimate, with ±20% uncertainty,
that…"). Hedging to dodge a hard question is not.

## The "so what?" test

For every paragraph, ask: *if a reader skips this paragraph, what decision or
understanding do they lose?* If the answer is "nothing", cut it.

## Self-review checklist (run before handing back)

- [ ] First sentence names the customer and the problem (or, for analysis
      reports, the question being answered).
- [ ] Every quantitative claim has a number, a unit, and a source.
- [ ] No banned weasel words remain.
- [ ] Every section leads with its takeaway.
- [ ] FAQ (where required) tackles the hardest 5–10 questions, not the easiest.
- [ ] Length is within the doc type's budget.
- [ ] Acronyms defined on first use; jargon explained or removed.
- [ ] Open questions and risks are listed, not buried.
- [ ] Sources section lists every input file relied on.

## References

- See each `writing-*` sibling skill for the section template that doc type
  requires on top of these style rules.

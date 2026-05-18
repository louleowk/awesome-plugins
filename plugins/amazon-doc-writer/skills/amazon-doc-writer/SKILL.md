---
name: amazon-doc-writer
description: Overview skill for the amazon-doc-writer plugin. Use this when the user asks how to write an Amazon-style internal document, which doc type to pick (PR/FAQ vs technical design vs mini design vs analysis report), or how the amazon-doc-writer agent and its companion skills fit together.
---

# Amazon Doc Writer

This skill is the entry point for producing Amazon-style internal documents from
a set of source files. It points at the per-doc-type authoring skills and the
shared style skill.

## When to use

- The user asks to "write a PR/FAQ", "write a 6-pager", "write a design doc",
  "write an analysis report", or "write an Amazon-style doc".
- The user hands the agent a folder of notes, specs, tickets, or code and asks
  for a single polished narrative document.

## Doc type decision matrix

| User intent                                                              | Doc type                  | Skill                              |
| ------------------------------------------------------------------------ | ------------------------- | ---------------------------------- |
| Pitch a new product / feature working backwards from the customer        | PR/FAQ                    | `writing-prfaq`                    |
| Propose / review a non-trivial technical solution (6-pager class)        | Technical Design          | `writing-technical-design`         |
| Capture a small design decision or scoped change (1–2 pages)             | Mini Technical Design     | `writing-mini-technical-design`    |
| Investigate data / a system / a question and report findings             | Analysis Report           | `writing-analysis-report`          |
| Document a customer-impacting incident with timeline, 5 Whys, action items | COE (Correction of Errors) | `writing-coe`                  |
| Write the annual operating-plan narrative (goals, inputs, headcount)     | OP1 / OP2 Narrative       | `writing-op1-narrative`            |
| Write the commentary that accompanies a weekly metrics deck              | WBR Narrative             | `writing-wbr-narrative`            |

Always **also** load `amazon-writing-style` for the tone, structure, and quality
bar that applies to every doc type.

## How to apply

1. **Pick the doc type** using the matrix above. If the request is ambiguous,
   ask one clarifying question (e.g. "Is this for launch alignment (PR/FAQ) or
   for an engineering design review (technical design)?").
2. **Load the matching skill** plus `amazon-writing-style`.
3. **Inventory sources.** Use `Glob`/`Grep`/`Read` on the files the user
   provided. Take notes on: customer + problem, goals/non-goals, constraints,
   data points, risks, open questions.
4. **Outline → draft → self-review** per the doc-type skill. Write in narrative
   prose; quantify claims; ground every statement in the sources.
5. **Save the doc** as a single markdown file. Report file path, sources used,
   and any open questions.

## References

- `../amazon-writing-style/SKILL.md` — shared tone, structure, and quality bar.
- `../writing-prfaq/SKILL.md`
- `../writing-technical-design/SKILL.md`
- `../writing-mini-technical-design/SKILL.md`
- `../writing-analysis-report/SKILL.md`
- `../writing-coe/SKILL.md`
- `../writing-op1-narrative/SKILL.md`
- `../writing-wbr-narrative/SKILL.md`

## Checklist

- [ ] Correct doc type selected (or one clarifying question asked).
- [ ] Source files inventoried and read before drafting.
- [ ] Doc-type skill **and** `amazon-writing-style` both consulted.
- [ ] Output is a single markdown file in Amazon narrative style.
- [ ] Sources cited and open questions listed.

---
name: designing-skills
description: Use this skill to design a Claude Code skill (a `SKILL.md` under a plugin's `skills/<name>/` directory) — its trigger phrases, scope, structure, and supporting assets — informed by current best practices. The output is a design spec; the actual `SKILL.md` should be authored with the `writing-skills` skill via `plugin-creator`.
---

# Designing Skills

Use this skill to turn research findings into a concrete design for one or
more Claude Code skills. A skill is model-invoked knowledge that Claude
loads when relevant — *not* a system prompt, *not* a user-facing command.

## When to use

- The user wants reusable knowledge or how-to guidance available to Claude.
- The deliverable is one or more `<plugin>/skills/<name>/SKILL.md` designs.

## Design dimensions

For every skill, decide and document:

1. **Identity** — kebab-case name (matches the directory).
2. **Trigger description** — what Claude reads to decide to load this skill.
   Phrase as "Use this skill when…". Be concrete about user intents.
3. **Scope** — exactly one concern. If two concerns appear, design two
   skills and have one reference the other.
4. **Audience** — Claude, not end users. The body is instructions to the
   model.
5. **Body structure** — at minimum:
   - **When to use** (bulleted triggers).
   - **How to apply** (numbered workflow or checklist).
   - **References** (links to sibling files or other skills).
6. **Supporting assets** — templates, JSON snippets, helper scripts that
   live next to `SKILL.md` and are referenced by relative path.
7. **Relationship to other skills/agents** — which agent invokes it, which
   sibling skills it links to.

## Best-practice patterns to apply

- **One skill, one concern.** Split large topics into multiple linked
  skills rather than one giant file.
- **Lead with "when".** The `description` is a router; make the triggers
  unambiguous.
- **Tell Claude how, not what.** Prefer numbered steps and checklists over
  prose.
- **Co-locate assets.** Put templates and helper files next to `SKILL.md`
  and reference them with relative paths so they travel with the skill.
- **Cross-link, don't duplicate.** When two skills share knowledge, factor
  it into a third skill they both reference.
- **No frontmatter beyond `name` and `description`** — extra fields are
  not part of the skill contract.

## Output: skill design spec

For each proposed skill, produce:

```markdown
### Skill: <kebab-case-name>

- **Trigger description:** <"Use this skill when …">
- **Scope:** <single concern>
- **Body outline:**
  - When to use:
    - ...
  - How to apply:
    1. ...
  - References: <sibling skills or files>
- **Supporting assets:** <list of files to colocate, or "none">
- **Rationale & citations:**
  - <best-practice> — <URL>
```

When designing a *set* of skills, also produce a short table of how they
relate (which skill calls which).

## Hand-off

Direct the user (or `plugin-creator`) to the `writing-skills` skill to
render each `SKILL.md`.

## Checklist

- [ ] Each skill is single-concern.
- [ ] `description` is action-oriented and trigger-led.
- [ ] Body has *When to use* and *How to apply* sections.
- [ ] Supporting assets, if any, are colocated and linked.
- [ ] Cross-references between skills are explicit.
- [ ] Every "best practice" cites a real, recent source.

---
name: writing-skills
description: Use this skill when authoring a `SKILL.md` for a Claude Code plugin (a directory under `skills/`). It explains the required YAML frontmatter, when-to-use phrasing, supporting assets, and how to register the skill in `plugin.json`.
---

# Writing Skills

A skill is a directory: `<plugin-name>/skills/<skill-name>/`. At minimum it
contains a `SKILL.md`; it may also contain templates, scripts, or other
reference files Claude can read on demand.

## File format

```markdown
---
name: <kebab-case-name>
description: One or two sentences telling Claude WHEN to load this skill.
---

# <Human Title>

<Short intro: what this skill is for.>

## When to use

- Bullet a few concrete triggers ("when the user asks to ...").

## How to apply

1. Step-by-step guidance Claude should follow.
2. ...

## References

- Link to supporting files in the same directory (e.g. `templates/foo.md`).
```

## Frontmatter rules

- `name` (required): kebab-case, must match the directory name.
- `description` (required): action-oriented, mention the trigger phrase.
  This is what Claude reads to decide whether to load the skill.
- No other frontmatter fields are required.

## Body rules

- Write for Claude, not for end users. Tell it *when* and *how*.
- Keep it focused — one skill, one concern. Split large topics into multiple
  skills.
- Use checklists, numbered workflows, and short examples liberally.
- Place supporting assets (templates, JSON snippets, helper scripts) next to
  `SKILL.md`, and reference them by relative path.

## Manifest wiring

Skills are registered by **directory**, not by file:

```json
{
  "skills": ["./skills/<skill-name>"]
}
```

## Checklist

- [ ] Directory name, `name` frontmatter, and the skill's identity all match.
- [ ] `description` clearly signals when Claude should load this skill.
- [ ] Body explains *when* and *how*, not just *what*.
- [ ] Supporting files (if any) sit alongside `SKILL.md` and are linked.
- [ ] Directory is listed in `plugin.json` `skills`.

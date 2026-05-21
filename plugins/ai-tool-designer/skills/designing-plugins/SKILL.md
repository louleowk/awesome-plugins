---
name: designing-plugins
description: Use this skill to design a full Claude Code plugin — its name, components (agents, skills, commands, hooks), manifest, and marketplace fit — informed by the latest industry best practices. The output is a design spec to be implemented by the `plugin-creator` agent.
---

# Designing Plugins

Use this skill when the deliverable is an entire Claude Code plugin, not
just a single agent or skill. It composes the per-component design skills
(`designing-agents`, `designing-skills`) into a coherent package.

## When to use

- The user wants a new plugin scaffolded that ships multiple components.
- The user is unsure whether they need an agent, a skill, a command, or
  hooks, and needs help choosing.

## Component-choice rubric

Decide which Claude Code primitives the plugin needs:

| Need | Use |
| --- | --- |
| A focused subagent with its own system prompt and tool scope | **agent** |
| Reusable, model-invoked knowledge Claude loads on demand | **skill** |
| A user-typed `/name` entry point | **command** |
| A deterministic shell action on a lifecycle event (e.g. `PreToolUse`) | **hook** |

A typical well-designed plugin contains **one primary agent** plus **2–6
sibling skills** the agent delegates to, optionally with one or two slash
commands as entry points.

## Design dimensions

For the plugin overall, decide and document:

1. **Plugin name** — kebab-case, matches the directory.
2. **One-paragraph description** — appears in `plugin.json` and the
   marketplace manifest.
3. **Component inventory** — which agents, skills, commands, hooks ship.
   Justify every one (don't include components "just in case").
4. **Directory layout** — concrete tree of files to create.
5. **Manifest sketch** — the `plugin.json` fields and component arrays.
6. **Marketplace entry** — the entry to add to the parent collection's
   `.claude-plugin/marketplace.json` (if this repo is a collection).
7. **Per-component designs** — defer to `designing-agents` and
   `designing-skills` for each.
8. **Install / usage instructions** — the `/plugin marketplace add` and
   `/plugin install` commands the user will run.

## Best-practice patterns to apply

- **Cohesion over completeness.** Ship only the components that serve the
  plugin's single purpose.
- **Agent + skills pairing.** Keep the agent prompt short by pushing
  detailed knowledge into sibling skills.
- **Skill-only plugins are fine.** A plugin can ship only skills — useful
  for adding domain knowledge without changing routing.
- **Hooks are deterministic.** Use them for guards and automation, not
  for reasoning.
- **Stable, kebab-case names.** They become user-visible identifiers.
- **No invented features.** Stay within agents / skills / commands / hooks.

## Output: plugin design spec

```markdown
# Plugin design: <plugin-name>

## Purpose
<1 paragraph.>

## Components
- Agents: <list + 1-line purpose each>
- Skills: <list + 1-line purpose each>
- Commands: <list, or "none">
- Hooks: <list, or "none">

## Directory layout
<tree>

## plugin.json (sketch)
<JSON block>

## Marketplace entry
<JSON snippet to add to `.claude-plugin/marketplace.json`>

## Per-component designs
- See agent spec(s) from `designing-agents`.
- See skill spec(s) from `designing-skills`.

## Install
```
/plugin marketplace add <owner>/<repo>
/plugin install <plugin-name>
```

## Rationale & citations
- <best-practice> — <URL>
```

## Hand-off

End with the exact follow-up prompt to send to `plugin-creator`, e.g.:

> "Use the `plugin-creator` agent to scaffold the plugin described above,
> using the `writing-agents` and `writing-skills` skills for each
> component."

## Checklist

- [ ] Every component has a stated purpose.
- [ ] No component is included "just in case".
- [ ] Directory layout is concrete and matches the manifest.
- [ ] Marketplace entry is provided if the target repo is a collection.
- [ ] Per-component design specs are linked.
- [ ] Every "best practice" cites a real, recent source.

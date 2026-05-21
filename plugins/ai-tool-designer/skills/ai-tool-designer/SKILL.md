---
name: ai-tool-designer
description: Overview skill for designing Claude Code plugins, agents, and skills informed by the latest industry best practices. Load this when the user asks how to design (not implement) an AI agent, skill, or Claude Code plugin, or asks for the "best way" to structure one.
---

# AI Tool Designer

This skill is the entry point for **designing** Claude Code AI tooling
(plugins, subagents, skills) based on current industry best practices. It
points to the focused skills used by the `ai-tool-designer` agent.

## When to use

- The user asks to design or architect a Claude Code plugin, agent, or skill.
- The user asks for current best practices or trends for AI agents,
  prompt engineering, tool use, or Claude Code plugins.
- The user wants a design spec they (or `plugin-creator`) can then implement.

## How to apply

1. **Clarify form factor.** Decide whether the user needs a full plugin,
   a single subagent, one or more skills, a slash command, or hooks.
2. **Research first.** Use the `researching-best-practices` skill to run
   targeted Google / docs / GitHub searches and fetch primary sources.
3. **Design second.** Use the matching design skill:
   - `designing-agents` — for a single subagent.
   - `designing-skills` — for one or more skills.
   - `designing-plugins` — for an entire plugin (multiple components).
4. **Write the design spec** in the structure defined by the agent prompt,
   with citations for every best-practice claim.
5. **Hand off** to `plugin-creator` for scaffolding.

## When to use which design skill

- **`designing-agents`** — the deliverable is one focused subagent with its
  own system prompt, tool scope, and trigger phrases.
- **`designing-skills`** — the deliverable is reusable knowledge Claude loads
  on demand; no system prompt of its own.
- **`designing-plugins`** — the deliverable bundles multiple components
  (agent + skills, or skills + commands + hooks) and needs a manifest.

## References

- `../researching-best-practices/SKILL.md`
- `../designing-agents/SKILL.md`
- `../designing-skills/SKILL.md`
- `../designing-plugins/SKILL.md`

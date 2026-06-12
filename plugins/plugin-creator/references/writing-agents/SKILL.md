---
name: writing-agents
description: Use this skill when authoring a Claude Code subagent file (a markdown file under a plugin's `agents/` directory). It explains the required YAML frontmatter fields, the system-prompt body, tool scoping, and naming conventions.
---

# Writing Agents

Subagents live at `<plugin-name>/agents/<agent-name>.md`. Each file defines one
subagent: YAML frontmatter on top, the system prompt as the markdown body.

## File format

```markdown
---
name: <kebab-case-name>
description: One or two sentences telling Claude WHEN to invoke this agent.
tools: Read, Grep, Glob, Bash        # optional — omit to inherit all tools
model: inherit                        # optional — sonnet | opus | haiku | inherit
---

You are <role>. <Concise statement of purpose.>

## Responsibilities
- ...

## Workflow
1. ...

## Guardrails
- ...
```

## Frontmatter rules

- `name` (required): kebab-case, must match the filename (without `.md`).
- `description` (required): action-oriented. Mention the triggers
  ("Use this agent when...") so Claude can route to it automatically.
- `tools` (optional): comma-separated list. Omit to inherit every tool from
  the calling context. Restrict tools when the agent should be sandboxed.
- `model` (optional): `inherit` is a good default; use `sonnet`, `opus`, or
  `haiku` to pin a tier.

## Body rules

- Write the body as a system prompt addressed to the agent ("You are...").
- Include a short **Responsibilities**, **Workflow**, and **Guardrails**
  section. Keep it focused on a single domain — one agent, one job.
- Reference companion skills by name when the agent should delegate detailed
  knowledge to a skill.

## Manifest wiring

Add the file to `plugin.json`:

```json
{
  "agents": ["./agents/<agent-name>.md"]
}
```

## Checklist

- [ ] Filename is kebab-case and matches `name`.
- [ ] `description` tells Claude *when* to use the agent.
- [ ] Tool list is minimal and intentional (or omitted to inherit).
- [ ] Body is a system prompt, not user-facing docs.
- [ ] File is listed in `plugin.json` `agents`.

## Official docs (source of truth)

If this skill conflicts with the official docs, the docs win — fetch them
and flag this skill for an update.

- Subagents: https://code.claude.com/docs/en/sub-agents
- Plugins reference — Agents section (how `agents` paths and plugin-only
  restrictions like no `hooks` / `mcpServers` / `permissionMode` work):
  https://code.claude.com/docs/en/plugins-reference

---
name: designing-agents
description: Use this skill to design a Claude Code subagent (the markdown file under a plugin's `agents/` directory) — its purpose, trigger phrases, tool scope, model tier, system prompt structure, and guardrails — informed by current best practices. This skill produces a design spec; it does NOT write the final file (delegate that to `writing-agents` via `plugin-creator`).
---

# Designing Agents

Use this skill to turn research findings into a concrete subagent design.
The output is a spec that a downstream authoring skill (`writing-agents`)
can implement.

## When to use

- The user wants a single, focused subagent.
- The deliverable is a `<plugin>/agents/<name>.md` file's design — not yet
  the file itself.

## Design dimensions

For every agent, decide and document:

1. **Identity** — kebab-case name + 1-sentence role ("You are the X agent").
2. **Trigger phrases** — what user prompts should route to this agent.
   Phrase them as "Use this agent when…". This becomes the `description`.
3. **Scope of work** — a single domain. If you find yourself listing more
   than one job, split into multiple agents or push knowledge into skills.
4. **Tool scope** — the **minimum** tools needed. Common choices:
   `Read, Grep, Glob` (read-only research), `+ Write, Edit` (authoring),
   `+ Bash` (executes shell), `WebSearch, WebFetch` (online research).
   Omit `tools` to inherit everything — only do this for general-purpose
   agents.
5. **Model tier** — `inherit` by default; `opus`/`sonnet` for heavy
   reasoning; `haiku` for cheap, mechanical work.
6. **Workflow** — 3–7 numbered steps the agent always follows.
7. **Delegation** — which sibling skills the agent should defer to for
   detailed knowledge (keeps the system prompt short).
8. **Guardrails** — what the agent must NOT do (out-of-scope topics,
   destructive actions without confirmation, leaking private data, etc.).

## Best-practice patterns to apply

- **One agent, one job.** Narrow scope > broad scope.
- **Skills carry knowledge, agents carry workflow.** Push reusable
  domain knowledge into a sibling skill rather than bloating the agent
  prompt.
- **Tool minimization.** Smaller tool surface area = safer and cheaper.
- **Action-oriented description.** Start with "Use this agent when…" so
  Claude can route to it automatically.
- **Explicit handoffs.** If another agent (e.g. `plugin-creator`) should
  finish the job, name it in the workflow.
- **Determinism where possible.** Reference checklists, numbered steps,
  and a "Report" or "Output format" section.

## Output: agent design spec

Produce a block like this:

```markdown
### Agent: <kebab-case-name>

- **Role:** <one sentence>
- **Trigger description:** <"Use this agent when …">
- **Tools:** <comma-separated list, or "inherit">
- **Model:** <inherit | sonnet | opus | haiku>
- **Workflow:**
  1. ...
  2. ...
- **Delegates to skills:** <names>
- **Guardrails:**
  - ...
- **Rationale & citations:**
  - <best-practice> — <URL>
```

## Hand-off

After producing the spec, point the user (or `plugin-creator`) at the
`writing-agents` skill to render the actual file.

## Checklist

- [ ] Single, well-defined job.
- [ ] Trigger description starts with "Use this agent when…".
- [ ] Tool list is the minimum needed.
- [ ] Workflow is numbered and bounded.
- [ ] Guardrails section exists.
- [ ] Every "best practice" cites a real, recent source.

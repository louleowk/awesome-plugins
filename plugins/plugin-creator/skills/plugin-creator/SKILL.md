---
name: plugin-creator
description: Overview skill describing how to scaffold a Claude Code plugin end-to-end. Use this when the user asks how to create a plugin, what files a plugin needs, or how the plugin-creator agent and its sibling authoring skills fit together.
---

# Plugin Creator

This skill is the entry point for creating Claude Code plugins. It describes
the canonical plugin layout and points to the focused authoring skills used by
the `plugin-creator` agent.

## Canonical plugin layout

```
<plugin-name>/
├── .claude-plugin/plugin.json   # required manifest
├── agents/<name>.md             # optional subagents
├── commands/<name>.md           # optional slash commands
├── hooks/hooks.json             # optional hook configuration
└── skills/<name>/SKILL.md       # optional skills
```

## Manifest essentials (`.claude-plugin/plugin.json`)

- `name` (required, kebab-case, matches the plugin directory).
- `version`, `description`, `author`, `repository` (strongly recommended).
- Component arrays — include only those the plugin ships:
  - `agents`: list of `.md` paths.
  - `skills`: list of skill **directory** paths.
  - `commands`: list of `.md` paths.
  - `hooks`: path to a `hooks.json` file.

Every path is relative to the plugin root and every referenced file must exist.

## Authoring workflow

1. Decide the plugin name and which components are needed.
2. Create the directories and the manifest.
3. Author each component using the dedicated skill:
   - **Agents** → `writing-agents`
   - **Hooks** → `writing-hooks`
   - **Skills** → `writing-skills`
   - **Commands** → `writing-commands`
4. Validate that `plugin.json` parses and every referenced file exists.
5. Tell the user the install commands:
   ```
   /plugin marketplace add <owner>/<repo>
   /plugin install <plugin-name>
   ```

## When to use which component

- **Agent** — a focused subagent with its own system prompt and tool scope.
- **Skill** — reusable, model-invoked knowledge/instructions Claude loads when
  relevant.
- **Command** — a user-invoked slash command (`/name`).
- **Hook** — a deterministic shell command triggered by a Claude Code lifecycle
  event (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `SessionStart`,
  `Stop`, `Notification`, ...).

## Official docs (source of truth)

If anything in this skill conflicts with the official Claude Code docs, the
docs win — fetch them and flag the skill for an update.

- Plugins overview: https://code.claude.com/docs/en/plugins
- Plugins reference (manifest fields): https://code.claude.com/docs/en/plugins-reference
- Plugin marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- Subagents: https://code.claude.com/docs/en/sub-agents
- Slash commands / skills (custom commands are now skills): https://code.claude.com/docs/en/skills
- Hooks reference: https://code.claude.com/docs/en/hooks
- Hooks guide (practical recipes): https://code.claude.com/docs/en/hooks-guide

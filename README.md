# awesome-plugins

Collection repository for Claude Code plugins.

Each directory under `plugins/` is a standalone plugin package with its own
`.claude-plugin/plugin.json` manifest and its own agents, skills, hooks, and
commands.

## Plugins in this collection

- **`plugins/plugin-creator`** — scaffolds new Claude Code plugins. Ships a
  self-contained `plugin-creator` agent plus skills for authoring agents,
  hooks, skills, and slash commands.

## Install

```text
/plugin marketplace add louleowk/awesome-plugins
/plugin install plugin-creator
```

## Collection structure

```text
.
└── plugins/
    └── plugin-creator/
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   └── plugin-creator.md
        └── skills/
            ├── plugin-creator/SKILL.md
            ├── writing-agents/SKILL.md
            ├── writing-hooks/SKILL.md
            ├── writing-skills/SKILL.md
            └── writing-commands/SKILL.md
```

## Adding new plugins

1. Create `plugins/<plugin-name>/`.
2. Add `.claude-plugin/plugin.json` (see `plugins/plugin-creator` for a
   reference).
3. Add any of `agents/`, `commands/`, `hooks/`, `skills/` the plugin needs.
4. Add the plugin to the list above.

The `plugin-creator` plugin can do all of the above for you.

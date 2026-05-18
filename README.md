# awesome-plugins

A [Claude Code plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces).

The marketplace manifest lives at `.claude-plugin/marketplace.json` and lists
every plugin published by this repository. Each directory under `plugins/` is a
standalone plugin package with its own `.claude-plugin/plugin.json` manifest
and its own agents, skills, hooks, and commands.

## Plugins in this collection

- **`plugins/plugin-creator`** — scaffolds new Claude Code plugins. Ships a
  self-contained `plugin-creator` agent plus skills for authoring agents,
  hooks, skills, and slash commands.
- **`plugins/amazon-doc-writer`** — writes Amazon-style internal documents
  (PR/FAQ, technical design / 6-pager, mini technical design, analysis
  report) from a set of user-provided source files. Ships an
  `amazon-doc-writer` agent plus per-doc-type skills and a shared
  `amazon-writing-style` skill.

## Install

```text
/plugin marketplace add louleowk/awesome-plugins
/plugin install plugin-creator
```

## Collection structure

```text
.
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    ├── plugin-creator/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   └── plugin-creator.md
    │   └── skills/
    │       ├── plugin-creator/SKILL.md
    │       ├── writing-agents/SKILL.md
    │       ├── writing-hooks/SKILL.md
    │       ├── writing-skills/SKILL.md
    │       └── writing-commands/SKILL.md
    └── amazon-doc-writer/
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   └── amazon-doc-writer.md
        └── skills/
            ├── amazon-doc-writer/SKILL.md
            ├── amazon-writing-style/SKILL.md
            ├── writing-prfaq/SKILL.md
            ├── writing-technical-design/SKILL.md
            ├── writing-mini-technical-design/SKILL.md
            └── writing-analysis-report/SKILL.md
```

## Adding new plugins

1. Create `plugins/<plugin-name>/`.
2. Add `.claude-plugin/plugin.json` (see `plugins/plugin-creator` for a
   reference).
3. Add any of `agents/`, `commands/`, `hooks/`, `skills/` the plugin needs.
4. Add an entry for the plugin to `.claude-plugin/marketplace.json`.
5. Add the plugin to the list above.

The `plugin-creator` plugin can do all of the above for you.

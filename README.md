# awesome-plugins

Collection repository for Claude Code plugins.

This repository is intentionally organized as a **plugin collection**.  
Each directory under `plugins/` is a standalone plugin package with its own manifest and skills.

## Plugins in this collection

- `plugins/awesome-plugins-core`
- `plugins/repo-curation`

## Collection structure

```text
.
└── plugins/
    ├── awesome-plugins-core/
    │   ├── .claude-plugin/plugin.json
    │   └── skills/awesome-plugins/SKILL.md
    └── repo-curation/
        ├── .claude-plugin/plugin.json
        └── skills/repo-curation/SKILL.md
```

## Adding new plugins

1. Create `plugins/<plugin-name>/`
2. Add `.claude-plugin/plugin.json`
3. Add one or more skills under `skills/<skill-name>/SKILL.md`
4. Add the plugin to the list above

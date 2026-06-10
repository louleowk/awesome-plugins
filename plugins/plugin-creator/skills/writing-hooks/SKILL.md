---
name: writing-hooks
description: Use this skill when authoring `hooks/hooks.json` for a Claude Code plugin. It explains the supported hook events, the matcher/command structure, and how to reference plugin-relative scripts via ${CLAUDE_PLUGIN_ROOT}.
---

# Writing Hooks

Hooks let a plugin run deterministic shell commands in response to Claude Code
lifecycle events. They live at `<plugin-name>/hooks/hooks.json` and are wired
into the manifest via `"hooks": "./hooks/hooks.json"`.

## File format

```json
{
  "hooks": {
    "<EventName>": [
      {
        "matcher": "<optional pattern>",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/scripts/do-something.sh"
          }
        ]
      }
    ]
  }
}
```

- The outer object has a single `hooks` key.
- Each event key maps to an array of `{ matcher?, hooks[] }` entries.
- Each inner hook is `{ "type": "command", "command": "<shell>" }`.

## Common events

- `PreToolUse` — before a tool runs. `matcher` filters by tool name
  (e.g. `"Write|Edit"`).
- `PostToolUse` — after a tool runs.
- `UserPromptSubmit` — when the user submits a prompt.
- `SessionStart` / `SessionEnd` — session lifecycle.
- `Stop` — when Claude finishes responding.
- `Notification` — when Claude Code emits a notification.

(Use only the events you actually need; omit the rest.)

## Path conventions

- Use `${CLAUDE_PLUGIN_ROOT}` for any script shipped inside the plugin so
  paths resolve correctly wherever the plugin is installed.
- Keep scripts in `<plugin-name>/scripts/` and make them executable.
- Prefer short, single-purpose commands. Chain via a script rather than
  packing complex logic into the JSON.

## Manifest wiring

```json
{
  "hooks": "./hooks/hooks.json"
}
```

## Checklist

- [ ] `hooks.json` parses as JSON.
- [ ] Every event name is one Claude Code supports.
- [ ] `matcher` is included only where meaningful (mostly `PreToolUse` /
      `PostToolUse`).
- [ ] Plugin-relative scripts use `${CLAUDE_PLUGIN_ROOT}` and are executable.
- [ ] The file is referenced from `plugin.json` `hooks`.

## Official docs (source of truth)

If this skill conflicts with the official docs (event names, matcher rules,
exit-code semantics, env vars), the docs win — fetch them and flag this
skill for an update.

- Hooks reference (full event list, JSON input/output schema, exit codes):
  https://code.claude.com/docs/en/hooks
- Hooks guide (recipes: notifications, formatters, blockers, audits):
  https://code.claude.com/docs/en/hooks-guide
- Plugins reference — Hooks section (how `hooks` is wired into
  `plugin.json` and which events plugins support):
  https://code.claude.com/docs/en/plugins-reference

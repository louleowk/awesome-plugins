---
name: writing-commands
description: Use this skill when authoring a slash command for a Claude Code plugin (a markdown file under `commands/`). It explains the frontmatter fields, argument hints, allowed-tools scoping, and how the file name becomes the slash command.
---

# Writing Commands

Slash commands live at `<plugin-name>/commands/<command-name>.md`. The file
name (without `.md`) becomes the slash command: `commands/review.md` →
`/review`.

## File format

```markdown
---
description: One short sentence shown in the slash-command picker.
argument-hint: "<expected arguments, e.g. [path]>"   # optional
allowed-tools: Read, Grep, Bash                      # optional
---

<Body: instructions Claude should follow when the user invokes this command.
Use $ARGUMENTS to reference everything the user typed after the command name.>
```

## Frontmatter rules

- `description` (required): shown in the slash-command picker. Keep it short
  and action-oriented.
- `argument-hint` (optional): placeholder shown to the user, e.g.
  `"[file] [message]"`.
- `allowed-tools` (optional): comma-separated tool list to restrict what the
  command can do. Omit to inherit the session's tools.

There is no `name` field — the file name IS the command name. Use kebab-case
file names.

## Body rules

- Write the body as instructions to Claude, not as user-facing docs.
- Reference user input with `$ARGUMENTS`.
- Be explicit about the expected output format if it matters.
- If the command is complex, have it delegate to an agent or skill rather
  than embedding a long workflow inline.

## Manifest wiring

```json
{
  "commands": ["./commands/<command-name>.md"]
}
```

## Checklist

- [ ] File name is kebab-case; it becomes the slash command.
- [ ] `description` is one short, action-oriented sentence.
- [ ] `argument-hint` is present when the command takes arguments.
- [ ] `allowed-tools` is set when the command should be sandboxed.
- [ ] Body addresses Claude and uses `$ARGUMENTS` if applicable.
- [ ] File is listed in `plugin.json` `commands`.

## Official docs (source of truth)

Note: Claude Code merged custom commands into skills. A file at
`.claude/commands/foo.md` and a skill at `.claude/skills/foo/SKILL.md` both
create `/foo` and work the same way. For new plugins prefer `skills/`; the
`commands/` layout still works and is documented in the skills page.

If this skill conflicts with the official docs (frontmatter fields,
`$ARGUMENTS` semantics, allowed-tools syntax), the docs win — fetch them
and flag this skill for an update.

- Skills (covers custom commands): https://code.claude.com/docs/en/skills
- Plugins reference — Commands section (how `commands` paths are wired
  into `plugin.json`): https://code.claude.com/docs/en/plugins-reference

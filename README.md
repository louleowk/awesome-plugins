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
  report, COE / Correction of Errors, OP1/OP2 annual plan narrative, WBR
  narrative) from a set of user-provided source files. Ships an
  `amazon-doc-writer` agent plus per-doc-type skills and a shared
  `amazon-writing-style` skill.
- **`plugins/autonomous-builder`** — autonomously plans, implements, and
  reviews multi-step work in a codebase. Ships an `autonomous-builder`
  orchestrator agent plus `planner`, `implementer`, `reviewer`,
  `researcher`, `reflector`, and `tester` subagents and three slash
  commands: `/autonomous-build <goal>` (plan-and-execute),
  `/autonomous-status` (list all plans with current state), and
  `/autonomous-reflect` (cross-session trend analysis once you've
  accumulated 3+ completed plans). Uses plain agile vocabulary (MoSCoW
  priorities `[Must]` / `[Should]` / `[Could]` plus cadence `[Fast]` /
  `[Full]` / `[Journey]`) for acceptance criteria, with a per-phase
  **Definition of Done** that may include `[Journey]` AC exercised
  against the running system by the `tester` agent on three surfaces:
  **CLI** (binary + stdout/stderr/exit-code), **API** (HTTP +
  status/headers/body + side-effect verification), or **web**
  (Playwright + console-error budget). The reflector promotes durable
  codebase facts to `/memories/repo/autonomous-builder.md` after each
  successful plan; subsequent plans read those facts during initial
  discovery, so the plugin gets sharper at *this* repo over time.
  Hardened for large or legacy codebases via a shared `## Discoveries`
  log, adaptive retry, and first-class plan revision.
- **`plugins/task-craftsman`** — a senior-developer task worker for a
  single coding task. Ships one `task-craftsman` agent that triages the
  work, gates for design approval **only when the task is non-trivial**,
  implements it, and covers every changed behaviour with tests before
  reporting done. Its judgement lives in reference skills for
  `solid-design`, `clean-code`, `complete-code`, `testing-changed-code`,
  `refactoring-safely`, and `triaging-and-planning`. The doctrine skills
  are deliberately reusable: `autonomous-builder`'s `implementer` and
  `tester` read them when this plugin is installed and fall back to an
  inline digest when it is not.

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
    │   └── references/
    │       ├── plugin-creator/SKILL.md
    │       ├── writing-agents/SKILL.md
    │       ├── writing-hooks/SKILL.md
    │       ├── writing-skills/SKILL.md
    │       └── writing-commands/SKILL.md
    ├── amazon-doc-writer/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   └── amazon-doc-writer.md
    │   └── references/
    │       ├── amazon-doc-writer/SKILL.md
    │       ├── amazon-writing-style/SKILL.md
    │       ├── writing-prfaq/SKILL.md
    │       ├── writing-technical-design/SKILL.md
    │       ├── writing-mini-technical-design/SKILL.md
    │       ├── writing-analysis-report/SKILL.md
    │       ├── writing-coe/SKILL.md
    │       ├── writing-op1-narrative/SKILL.md
    │       └── writing-wbr-narrative/SKILL.md
    ├── autonomous-builder-v2/          # published as `autonomous-builder`
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   ├── autonomous-builder.md
    │   │   ├── designer.md
    │   │   ├── task-coordinator.md
    │   │   ├── implementer.md
    │   │   ├── tester.md
    │   │   ├── reviewer.md
    │   │   ├── researcher.md
    │   │   └── reflector.md
    │   ├── commands/
    │   │   ├── autonomous-build.md
    │   │   └── autonomous-status.md
    │   └── references/
    │       ├── designing/SKILL.md
    │       ├── feature-file-format/SKILL.md
    │       ├── orchestration-loop/SKILL.md
    │       ├── task-coordination/SKILL.md
    │       ├── reviewing/SKILL.md
    │       ├── researching/SKILL.md
    │       └── reflecting-on-sessions/SKILL.md
    └── task-craftsman/
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   └── task-craftsman.md
        └── references/
            ├── task-craftsman/SKILL.md
            ├── triaging-and-planning/SKILL.md
            ├── solid-design/SKILL.md
            ├── clean-code/SKILL.md
            ├── complete-code/SKILL.md
            ├── testing-changed-code/SKILL.md
            └── refactoring-safely/SKILL.md
```

Plugins in this collection put their skills under `references/` rather
than the auto-loaded `skills/`, because each skill is pulled in
deterministically by an agent prompt's "References to read" section rather
than by Claude's skill picker. Consequently `plugin.json` lists only
`agents` and `commands`.


## Adding new plugins

1. Create `plugins/<plugin-name>/`.
2. Add `.claude-plugin/plugin.json` (see `plugins/plugin-creator` for a
   reference).
3. Add any of `agents/`, `commands/`, `hooks/`, `skills/` the plugin needs.
4. Add an entry for the plugin to `.claude-plugin/marketplace.json`.
5. Add the plugin to the list above.

The `plugin-creator` plugin can do all of the above for you.

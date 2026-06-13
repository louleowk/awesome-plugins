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
    ├── amazon-doc-writer/
    │   ├── .claude-plugin/plugin.json
    │   ├── agents/
    │   │   └── amazon-doc-writer.md
    │   └── skills/
    │       ├── amazon-doc-writer/SKILL.md
    │       ├── amazon-writing-style/SKILL.md
    │       ├── writing-prfaq/SKILL.md
    │       ├── writing-technical-design/SKILL.md
    │       ├── writing-mini-technical-design/SKILL.md
    │       ├── writing-analysis-report/SKILL.md
    │       ├── writing-coe/SKILL.md
    │       ├── writing-op1-narrative/SKILL.md
    │       └── writing-wbr-narrative/SKILL.md
    └── autonomous-builder/
        ├── .claude-plugin/plugin.json
        ├── agents/
        │   ├── autonomous-builder.md
        │   ├── planner.md
        │   ├── implementer.md
        │   ├── reviewer.md
        │   ├── researcher.md
        │   ├── reflector.md
        │   └── tester.md
        ├── commands/
        │   ├── autonomous-build.md
        │   ├── autonomous-reflect.md
        │   └── autonomous-status.md
        └── references/
            ├── autonomous-builder/SKILL.md
            ├── plan-file-format/SKILL.md
            ├── planning-tasks/SKILL.md
            ├── amending-plans/SKILL.md
            ├── orchestration-loop/SKILL.md
            ├── implementing-tasks/SKILL.md
            ├── reviewing-acceptance-criteria/SKILL.md
            ├── exercising-journeys/SKILL.md
            ├── researching/SKILL.md
            └── reflecting-on-sessions/SKILL.md
```

## Adding new plugins

1. Create `plugins/<plugin-name>/`.
2. Add `.claude-plugin/plugin.json` (see `plugins/plugin-creator` for a
   reference).
3. Add any of `agents/`, `commands/`, `hooks/`, `skills/` the plugin needs.
4. Add an entry for the plugin to `.claude-plugin/marketplace.json`.
5. Add the plugin to the list above.

The `plugin-creator` plugin can do all of the above for you.

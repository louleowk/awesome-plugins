---
name: planning-tasks
description: Use this skill when the planner agent (initial mode) is drafting a fresh `.plans/<slug>.md` from a user's goal. It defines the discovery checklist (with researcher delegation), phase-grouping heuristics, task decomposition rules, and the acceptance-criteria authoring bar.
---

# Planning Tasks

The planner's job is to convert a user goal into a phased, executable plan
whose tasks each have ≥2 objectively-verifiable acceptance criteria. The
plan is a hypothesis — it does NOT need to anticipate every wrinkle, because
`amending-plans` provides a first-class revision path. But it must be
honest about what's known vs. assumed.

## When to use

- Planner agent is invoked in **initial** mode by the orchestrator (right
  after intake). For **revision** mode see `../amending-plans/SKILL.md`.

## Initial-mode workflow

### 1. Read the goal and pick a slug

- Restate the goal in one sentence to confirm understanding.
- Slug: kebab-case, ≤6 words, derived from the goal
  (e.g. `add-hello-command`, `extract-payment-module`,
  `rename-foobar-to-foo-bar`).

### 2. Discovery

Goal: gather just enough to write tasks whose AC are verifiable. Do NOT
attempt to map the entire codebase.

Checklist:

- Read the repo root: `README.md`, top-level layout, any `CONTRIBUTING.md`
  or `AGENTS.md` / `copilot-instructions.md`.
- Skim the target area's `README.md` or equivalent.
- Find ≥1 **sibling implementation** for anything new being added. (If
  adding a slash command, read 1–2 existing slash commands. If adding an
  agent, read 1–2 existing agents.) Sibling citations go in
  `## Discoveries`.
- For renames / refactors: find a call-site map first; do not assume a
  function is private without checking.

**Prefer dispatching the researcher** for any of these that need broad
search or multi-file reads. See `../researching/SKILL.md` for the dispatch
contract.

### 3. Seed `## Discoveries`

Before writing tasks, write down what you learned:

```markdown
## Discoveries

- [planner · 2026-06-10] Plugin manifests live at `<plugin>/.claude-plugin/plugin.json` (`plugins/amazon-doc-writer/.claude-plugin/plugin.json`).
- [planner · 2026-06-10] Slash commands register via `commands: [...]` array, kebab-case filenames become the command (`plugins/plugin-creator/skills/writing-commands/SKILL.md:8-12`).
- [planner · 2026-06-10] Tests run via `pytest` from repo root; no per-package configs (`pyproject.toml:42`).
```

This is the implementer's and reviewer's starting context. The more it
captures, the less they re-search.

### 4. Write `## Context`

One to three short paragraphs covering:

- The user's goal in your own words.
- Constraints (scope boundaries, must-not-touch areas, language/framework
  conventions, target audience).
- Prior art summary (what sibling examples exist; which one is the model).

Not a research dump — Discoveries is for facts. Context is the framing.

### 5. Decompose into phases

A **phase** is a coherent slice that:

- Either ships value standalone OR proves a hypothesis the rest of the plan
  depends on.
- Has ≤ ~5 tasks. If you find yourself writing a 7-task phase, split it.
- Has at least one `[gate]` phase-regression AC (the "we didn't break the
  rest of the system" check).

Common phase patterns:

| Pattern                            | Phases                                                                 |
| ---------------------------------- | ---------------------------------------------------------------------- |
| Add a small feature                | (1) Implement + tests (often only one phase).                          |
| Add a feature in unfamiliar area   | (1) Discovery / spike. (2) Implement. (3) Wire up + integration test.  |
| Rename / refactor                  | (1) Add new name alongside old. (2) Migrate callers. (3) Remove old.   |
| Extract module                     | (1) Internal restructure (no behaviour change). (2) Public API.        |
| Migration                          | (1) Scaffolding. (2) Per-area migration tasks. (3) Cutover + cleanup.  |

### 6. Decompose into tasks

Heuristics:

- **One logical concern per task.** A task is "add the parser flag", not
  "add the parser flag and also refactor the help text and also write
  docs."
- **≤ ~1 hour of human-equivalent work.** If the implementer would
  reasonably spend more than that, split.
- **Explicit `Depends on:`** — name the upstream tasks. Tasks with no
  dependencies are eligible from the start of their phase.
- **Avoid hidden coupling.** If Task 1.3 only works because Task 1.2 left a
  variable set in a specific way, that's coupling — make it explicit in
  Implementation notes or split differently.
- **Implementation notes are recommendations, not transcripts.** Name the
  files and the approach; don't pre-write the diff.

### 7. Write acceptance criteria

Every task needs **≥2 AC**, each tagged `[cheap]` or `[gate]`. See
`../plan-file-format/SKILL.md` for the full rules. Quick guide:

| Concern                          | `[cheap]` example                                           | `[gate]` example                                     |
| -------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| New file exists                  | `test -f path/to/new.py` exits 0                            | —                                                    |
| File has correct content         | `grep -q "def new_function" path/to/file.py` exits 0        | —                                                    |
| Manifest validity                | `python -c "import json; json.load(open('plugin.json'))"`   | —                                                    |
| Single unit test passes          | `pytest path/to/test_x.py::test_specific` exits 0           | —                                                    |
| Module suite passes              | —                                                           | `pytest path/to/test_module/` exits 0                |
| Full suite passes                | —                                                           | `pytest` exits 0                                     |
| Lint clean (one file)            | `ruff check path/to/file.py` exits 0                        | —                                                    |
| Lint clean (whole repo)          | —                                                           | `ruff check .` exits 0                               |
| End-to-end behaviour             | —                                                           | `./bin/app --smoke-test` exits 0                     |

Banned phrasings (any of these in an AC = reviewer rejects as PLAN_WRONG):
"looks good", "is clean", "works correctly", "well-structured", "no
issues", "follows best practices", "passes review".

### 8. Phase regression AC

Every phase needs ≥1 `[gate]` AC under `**Phase regression AC:**`. This
runs once after the last task in the phase passes its own AC.

Examples:

- `pytest` exits 0 (full suite still green).
- `ruff check .` exits 0 (no new lint warnings introduced by the phase).
- `python -c "import <package>"` exits 0 (package still imports).
- `./bin/app --smoke-test` exits 0 (binary still boots).

### 9. Set initial statuses

- Overall `**Status:**` → `Awaiting approval`.
- Each phase `**Status:**` → `Pending`.
- Each task `**Status:**` → `Pending`.
- Each task `**Review log:**` → `- (empty until first attempt)`.

### 10. Return

Return to the orchestrator:

- The plan file path (`.plans/<slug>.md`).
- A one-paragraph executive summary the orchestrator can show the user.
- Phase count and task count.

Do **NOT** present to the user yourself — the orchestrator owns user
interaction.

## Anti-patterns

- **Front-loading discovery you don't need.** If you can write a phase with
  10 tasks but only the first task is well-understood, write the first
  task fully and one phase with a smaller scope; trust the revision flow
  to extend the plan when more is learned.
- **AC that requires reading the implementer's mind.** "The change uses the
  right pattern." Reject in self-review.
- **Tasks named by file, not concern.** "Edit `foo.py`" is a bad task
  name. "Add `--verbose` flag to CLI parser" is good.
- **Phases that are just "do all the small things."** Phases must be
  coherent slices.

## Checklist (planner self-review before returning)

- [ ] Goal restated in one sentence in `## Context`.
- [ ] `## Discoveries` has at least one sibling-implementation citation per
      "new thing being added" pattern.
- [ ] Every phase has `**Phase regression AC:**` with ≥1 `[gate]` AC.
- [ ] Every task has ≥2 AC, each tagged `[cheap]` or `[gate]`.
- [ ] No banned phrasings anywhere in AC.
- [ ] Dependencies (`Depends on:`) are explicit and acyclic.
- [ ] Slug is kebab-case and matches the file name.
- [ ] Overall Status is `Awaiting approval`.

## References

- `../plan-file-format/SKILL.md` — file structure and AC syntax.
- `../researching/SKILL.md` — how to dispatch the researcher during
  discovery.
- `../amending-plans/SKILL.md` — what to do when the orchestrator invokes
  revision mode.

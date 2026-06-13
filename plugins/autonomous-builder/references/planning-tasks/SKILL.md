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

### 0. Read repo memory (if it exists)

Before any other discovery, check whether this repo has accumulated
durable facts from prior autonomous-builder sessions. Resolve
`/memories/repo/autonomous-builder.md` **against the target repo
root** (the directory that will contain the `.plans/` directory),
not the agent's cwd.

If the file exists:

1. Confirm the first line is exactly
   `# Autonomous-builder repo memory`. If not, do NOT read further
   — the path collides with an unrelated file. Note in the
   executive summary's Caveats and continue without seeding.
2. Read all five sections (build/test/run, architecture landmarks,
   test environment, sharp edges, conventions).
3. Pick up to **10 lines total** most relevant to this goal's
   surface. Don't paste everything; the planner is curating.
4. For each line you pick, `Read` the cited file:line to confirm
   it still resolves. Drop lines that don't. Stale seeds are
   worse than no seeds because they mislead the implementer.
5. Seed each surviving line into the new plan's `## Discoveries`
   with the tag `[planner · <today> · seeded from repo memory]`
   so downstream agents (and the next reflector) can tell
   seeded-from-history facts apart from this-session discoveries.

If the file does not exist, skip — repo memory accumulates only
after successful sessions. The first session in a repo always
starts cold.

### 1. Read the goal and pick a slug

- Restate the goal in one sentence to confirm understanding.
- Slug: kebab-case, ≤6 words, derived from the goal
  (e.g. `add-hello-command`, `extract-payment-module`,
  `rename-foobar-to-foo-bar`).

### 2. Discovery

Goal: gather just enough to write tasks whose AC are verifiable. Do NOT
attempt to map the entire codebase.

Checklist:

- **Anything already seeded from repo memory in step 0 doesn't
  need re-researching.** Reuse those Discoveries directly.
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
- Has a `**Definition of Done:**` block with at least one
  `[Must] [Full]` AC (the "we didn't break the rest of the system"
  regression check).

**The Environment phase rule.** If any phase's Definition of Done
contains a `[Journey]` AC (a real user-journey check on the
running system), the plan **must** start with an "Environment"
phase whose Definition of Done establishes the runnable system
and records the entry point in `## Discoveries`. Without this,
the tester has no system to drive against and the reviewer will
emit `PLAN_WRONG` with trigger `missing-environment-phase`.

The Environment phase shape varies by which surface(s) the
plan's Journey AC use. Each surface needs a specific Discovery
line so the tester can find the entry point.

**Web / API surface (most common):**

```markdown
## Phase 1: Environment

**Status:** Pending
**Definition of Done:**
- [ ] [Must] [Full] `docker compose up -d` exits 0 from a fresh clone with no manual steps.
- [ ] [Must] [Full] `curl -fsS http://localhost:3000/health` returns HTTP 200 within 30s.
- [ ] [Must] [Full] Seed data loaded: `psql ... -c "SELECT count(*) FROM users"` returns ≥3.
- [ ] [Must] [Full] `## Discoveries` contains a line tagged `bring-up URL: http://localhost:3000`.
```

**CLI surface:**

```markdown
## Phase 1: Environment

**Status:** Pending
**Definition of Done:**
- [ ] [Must] [Full] `make build` (or `cargo build --release` / `go build` / `npm run build`) exits 0 from a fresh clone.
- [ ] [Must] [Full] `./build/myapp --version` exits 0 and prints a non-empty version string.
- [ ] [Must] [Full] Test fixtures exist under `./fixtures/` (e.g. `test -d fixtures && test -f fixtures/sample.json`).
- [ ] [Must] [Full] `## Discoveries` contains a line tagged `binary path: ./build/myapp`.
```

**Mixed (CLI tool that calls an API service):** include both
entry-point Discovery lines, and split the Journey AC — one
`(cli)` AC for the CLI side, one `(api)` AC for the service side.

If the plan has no `[Journey]` AC anywhere (library refactors,
plugin/skill edits, doc-only changes), the Environment phase is
optional.

Common phase patterns:

| Pattern                            | Phases                                                                 |
| ---------------------------------- | ---------------------------------------------------------------------- |
| Add a small feature                | (1) Implement + tests (often only one phase).                          |
| Add a feature in unfamiliar area   | (1) Discovery / spike. (2) Implement. (3) Wire up + integration test.  |
| Rename / refactor                  | (1) Add new name alongside old. (2) Migrate callers. (3) Remove old.   |
| Extract module                     | (1) Internal restructure (no behaviour change). (2) Public API.        |
| Migration                          | (1) Scaffolding. (2) Per-area migration tasks. (3) Cutover + cleanup.  |
| Web app feature with user journey  | (1) Environment (web). (2) Implement. (3) DoD has `(web)` `[Journey]` AC. |
| HTTP API feature                   | (1) Environment (api). (2) Implement. (3) DoD has `(api)` `[Journey]` AC with side-effect verification. |
| CLI tool feature                   | (1) Environment (cli, includes build). (2) Implement. (3) DoD has `(cli)` `[Journey]` AC. |

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

Every task needs **≥2 AC**, each tagged with both a MoSCoW priority
(`[Must]` / `[Should]` / `[Could]`) and a cadence (`[Fast]` /
`[Full]`). `[Journey]` AC are reserved for phase Definition of Done
blocks (see step 8). See `../plan-file-format/SKILL.md` for the full
grammar.

**Pick a priority by asking: would I block the phase on this?**

- **`Must`** — yes. The task is not done until this passes. Use this
  for the AC that defines the task's purpose. Most AC are `Must`.
- **`Should`** — "important, but I'd ship without it." Use this for
  nice-to-have-passing checks: a non-critical lint warning, a slower
  variant of the main test, a metric that isn't a regression
  catastrophe. `Should` failures become WARN at the phase checkpoint.
- **`Could`** — informational. Use this rarely — e.g. a probe of an
  optional code path. `Could` failures are recorded but not surfaced
  unless asked.

**Pick a cadence by asking: how slow is this check?**

- **`Fast`** — runs in seconds, deterministic, no external
  services. Runs every implementer attempt.
- **`Full`** — slow or has setup cost. Runs on the about-to-Done
  attempt and as part of phase Definition of Done.

| Concern                          | `[Must] [Fast]` example                                     | `[Must] [Full]` example                              |
| -------------------------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| New file exists                  | `test -f path/to/new.py` exits 0                            | —                                                    |
| File has correct content         | `grep -q "def new_function" path/to/file.py` exits 0        | —                                                    |
| Manifest validity                | `python -c "import json; json.load(open('plugin.json'))"`   | —                                                    |
| Single unit test passes          | `pytest path/to/test_x.py::test_specific` exits 0           | —                                                    |
| Module suite passes              | —                                                           | `pytest path/to/test_module/` exits 0                |
| Full suite passes                | —                                                           | `pytest` exits 0                                     |
| Lint clean (one file)            | `ruff check path/to/file.py` exits 0                        | —                                                    |
| Lint clean (whole repo)          | —                                                           | `ruff check .` exits 0                               |
| End-to-end behaviour (CLI)       | —                                                           | `./bin/app --smoke-test` exits 0                     |

Banned phrasings (any of these in an AC = reviewer rejects as PLAN_WRONG):
"looks good", "is clean", "works correctly", "well-structured", "no
issues", "follows best practices", "passes review".

### 8. Definition of Done (per phase)

Every phase needs a `**Definition of Done:**` block with ≥1
`[Must] [Full]` AC. This runs once after the last task in the phase
passes its own AC.

Examples:

- `[Must] [Full]` — `pytest` exits 0 (full suite still green).
- `[Must] [Full]` — `ruff check .` exits 0 (no new lint warnings).
- `[Must] [Full]` — `python -c "import <package>"` exits 0 (package
  still imports).
- `[Must] [Full]` — `./bin/app --smoke-test` exits 0 (binary still
  boots).

**Add `[Journey]` AC for user-visible flows.** When the phase
ships a user-facing change, add a `[Journey]` AC describing a
real user / client / operator journey in plain English. **Every
`[Journey]` AC body must start with a `(cli)`, `(api)`, or
`(web)` surface prefix** — the reviewer parses this to dispatch
the `tester` subagent on the right surface.

```markdown
**Definition of Done:**
- [ ] [Must]   [Full]    `npm test` exits 0.
- [ ] [Must]   [Journey] (web) As a new user on `http://localhost:3000`, sign up with email and password, reach `/dashboard`, and see a "Welcome" message. No console errors, no 5xx.
- [ ] [Must]   [Journey] (api) `POST /users` with `{email, password}` returns 201 + `Location` header; follow-up `GET /users/<id>` returns the same email.
- [ ] [Must]   [Journey] (cli) `myapp init <empty-dir>` exits 0 and creates `config.toml`; running it again on the same dir exits non-zero with a clear "already initialised" message.
- [ ] [Should] [Journey] (web) As a returning user, log in and the previous session's last-viewed item is restored.
```

`[Journey]` AC bodies are journey *descriptions* (persona + entry
point + steps + expected end state), not test code. The tester
translates the description into surface-appropriate driver
commands (shell for `cli`, `curl` for `api`, Playwright for
`web`).

`[Journey]` AC are **only** allowed in `**Definition of Done:**`
blocks — never in a task's `**Acceptance criteria:**`. Plans with
`[Journey]` AC anywhere also need an Environment phase first
(step 5) — the entry-point Discovery line is what the tester
uses to find the running system.

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
- [ ] Step 0 ran: checked for `/memories/repo/autonomous-builder.md`
      and either seeded ≤10 lines with the
      `seeded from repo memory` tag (with citations confirmed by
      `Read`) or noted in Caveats why nothing was seeded.
- [ ] `## Discoveries` has at least one sibling-implementation citation per
      "new thing being added" pattern.
- [ ] Every phase has `**Definition of Done:**` with ≥1 `[Must] [Full]` AC.
- [ ] Every task has ≥2 AC, each tagged with both a priority
      (`[Must]` / `[Should]` / `[Could]`) and a cadence
      (`[Fast]` / `[Full]`).
- [ ] No `[Journey]` AC at the task level (only in Definition of Done).
- [ ] If any phase's Definition of Done has a `[Journey]` AC, an
      "Environment" phase exists earlier whose DoD establishes the
      runnable app.
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

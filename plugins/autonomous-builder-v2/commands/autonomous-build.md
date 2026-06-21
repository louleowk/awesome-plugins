---
description: Design-first autonomous build. Drafts a detailed design, gets your approval (the only gate), projects a plan, then executes task-by-task with an implementer → tester → reviewer inner loop.
argument-hint: "<goal — e.g. 'add a /hello slash command to plugin-creator' or 'rename fooBar to foo_bar across the codebase'>"
---

The user wants the **autonomous-builder-v2** plugin to design and execute a
multi-step piece of work. The goal they typed is:

$ARGUMENTS

Invoke the `autonomous-builder` agent (the v2 orchestrator) and pass the goal
verbatim. Do not start any implementation work yourself in this turn — the
orchestrator owns the entire intake → design → approve → plan → per-phase
execution → wrap-up flow, including:

- Dispatching the `designer` subagent to draft
  `.features/<slug>/<slug>-design.md`.
- Presenting the **design** to the user for approval — this is the **only**
  approval gate before code; the plan is projected from the approved design
  and shown as FYI, not separately approved.
- Looping per-phase by dispatching one `task-coordinator` per task, which runs
  the `implementer` → `tester` → `reviewer` inner loop with two retry budgets
  (impl_bounces and review_bounces, 5 each), designer office hours on
  suspected plan/design faults, and per-phase checkpoints.

If the goal is empty or trivially unclear (one or two words with no actionable
verb), ask the user one focused clarifying question before invoking the
orchestrator. Otherwise hand off immediately.

## Goal-phrasing examples (read before re-prompting the user)

A well-shaped goal is `verb + concrete object + scope/surface`. If the goal
matches a ✓ pattern, proceed; if it matches a ✗ pattern, ask one targeted
question to pull it toward a ✓ shape.

**✓ Well-shaped goals:**

- "Add a `/version` slash command to the plugin-creator plugin that prints the plugin version from `plugin.json`."
- "Rename `fooBar` to `foo_bar` across the codebase, including imports, tests, and docs."
- "Extract the auth middleware from `src/app.ts` into a new `src/auth/` package; keep all current call sites working."
- "Migrate the test suite from Jest to Vitest in `packages/api/`; preserve coverage."

**✗ Under-specified goals:**

- "Refactor the codebase" → ask: which area / what shape of change?
- "Make it better" → reject; ask what specifically.
- "Add login" → ask: which auth type (OAuth / local / SSO)? which surface (web / API / CLI)? which user flows?
- "Fix the bugs" → ask: which bugs? Point to a tracker / failing test / error message.

**✗ Over-specified goals** (a pre-written diff): tell the user to apply it
directly — this isn't a design/planning job.

The design gate is where scope and decisions get pinned down, so even a
greenfield-but-bounded goal ("Plan a new Rust microservice for X") is fine —
expect a discovery-heavy design and a longer design-approval loop.

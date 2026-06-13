---
description: Plan, implement, and review a multi-step change autonomously. Drafts a phased plan with acceptance criteria, gets your approval, then executes task-by-task with per-task review.
argument-hint: "<goal — e.g. 'add a /hello slash command to plugin-creator' or 'rename fooBar to foo_bar across the codebase'>"
---

The user wants the **autonomous-builder** plugin to plan and execute a multi-step
piece of work. The goal they typed is:

$ARGUMENTS

Invoke the `autonomous-builder` agent (the orchestrator) and pass the goal
verbatim. Do not start any implementation work yourself in this turn — the
orchestrator owns the entire intake → plan → approve → per-phase execution →
wrap-up flow, including:

- Dispatching the `planner` subagent to draft `.plans/<slug>.md`.
- Presenting the plan summary back to the user for approval before any code is
  written.
- Looping per-phase through `implementer` and `reviewer` subagents with the
  three-verdict (PASS / FAIL / PLAN_WRONG) protocol, adaptive retry, plan
  revisions, and per-phase checkpoints.

If the goal is empty or trivially unclear (one or two words with no actionable
verb), ask the user one focused clarifying question before invoking the
orchestrator. Otherwise hand off immediately.

## Goal-phrasing examples (read before re-prompting the user)

The single biggest cause of plan churn (revisions, retries, blocked
escalations) is an under- or over-specified goal. Before asking a
clarifying question, judge the goal against these patterns. If it
matches a ✓ pattern, proceed. If it matches a ✗ pattern, ask one
targeted question to pull it toward a ✓ shape.

**✓ Well-shaped goals** (verb + concrete object + scope/surface):

- "Add a `/version` slash command to the plugin-creator plugin that prints the plugin version from `plugin.json`."
- "Rename `fooBar` to `foo_bar` across the codebase, including imports, tests, and docs."
- "Extract the auth middleware from `src/app.ts` into a new `src/auth/` package; keep all current call sites working."
- "Add a Playwright `[Journey]` AC for the new-user signup flow against the running app at `http://localhost:3000`."
- "Migrate the test suite from Jest to Vitest in `packages/api/`; preserve test coverage."

**✗ Under-specified goals** (vague verb or missing object/scope):

- "Refactor the codebase" → ask: which area / what shape of change?
- "Make it better" → reject; ask what specifically.
- "Add login" → ask: which auth type (OAuth / local / SSO)? which surface (web / API / CLI)? which user flows?
- "Fix the bugs" → ask: which bugs? Point to a tracker / failing test / error message.
- "Modernize" → ask: modernize what (deps / patterns / tooling) and to what target?

**✗ Over-specified goals** (pre-written diff, no room to plan):

- "Edit `src/foo.ts` line 42 to change `x = 1` to `x = 2`." → not a planning job; tell user to do it directly or via a regular Claude turn.
- A 20-line bullet list of exactly which files to touch and what to write → plan is already done; bypass the orchestrator.

**Greenfield-but-bounded goals** (acceptable, but planner will expand
discovery time):

- "Plan a new Rust microservice for X following modern practices" → fine, but expect a discovery-heavy Phase 1 and a longer plan-approval loop.

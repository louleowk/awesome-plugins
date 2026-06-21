# autonomous-builder

`autonomous-builder` is a Copilot CLI plugin that orchestrates a
multi-step change end-to-end: intake → plan → user approval →
per-phase task loop (implementer → reviewer → advance / retry /
escalate / revise-plan) → phase checkpoint → wrap-up. It ships **7
agents** (orchestrator, planner, implementer, reviewer, researcher,
reflector, tester), **3 slash commands** (`/autonomous-build`,
`/autonomous-reflect`, `/autonomous-status`), and **10 reference
skills** under `references/`. The plugin works standalone; pairing it
with the [`agent-toolkit`](https://github.com/louleowk/agent-toolkit)
MCP server adds a persistent, code-base-scoped memory layer that lets
successive sessions inherit prior discoveries and reflections.

## Companion: agent-toolkit MCP

`agent-toolkit` exposes `memory_*` and `*_skills` MCP tools that the
orchestrator, researcher, implementer, reviewer, and reflector agents
call at well-defined points in the loop — intake (orchestrator),
pre-search (researcher), pre-edit (implementer), pre-verdict
(reviewer), and post-promotion (reflector) — so durable findings from
one session feed the next.

**Install** (one-time, from a clone of the agent-toolkit repo built
with `pnpm build`):

```
copilot mcp add agent-toolkit -- node /path/to/agent-toolkit/packages/mcp/dist/index.js
```

**Silent-degradation contract.** Every agent's MCP call is wrapped in
an explicit "degrade silently" clause, so if the `agent-toolkit-mcp`
server is not installed, not reachable, or returns an error, the agent
continues with its existing workflow and the plugin functions
identically to a vanilla install.

## Self-evolve loop

The agent-toolkit repo ships `scripts/relaunch.ps1` (Windows) and
`scripts/relaunch.sh` (POSIX): re-entrant scripts that rebuild
agent-toolkit, refresh the globally-installed CLI/MCP, re-sync the
plugin cache Copilot CLI reads from, and spawn a fresh
`copilot --yolo --agent autonomous-builder -p "<continuation>"` so the
next session inherits prior context via the memory layer.

Example invocation:

```
pwsh -File scripts/relaunch.ps1 -Goal "<next>" -PriorSlug <slug>
```

## How each agent uses the memory layer

| Agent        | MCP tool                          | Trigger                          |
| ------------ | --------------------------------- | -------------------------------- |
| orchestrator | `memory_search`                   | At intake on user goal           |
| researcher   | `memory_search` + `search_skills` | Before grep/glob                 |
| implementer  | `memory_search`                   | At task start (advisory)         |
| reviewer     | `memory_search`                   | Pre-AC-verification (advisory)   |
| reflector    | `memory_write`                    | After promoting each durable fact |

See `agent-toolkit/AGENTS.md`'s **Autonomous-builder integration**
section for the full per-agent contract, the silent-degradation
wording, and the end-to-end self-evolve sequence.

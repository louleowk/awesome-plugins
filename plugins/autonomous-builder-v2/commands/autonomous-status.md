---
description: Report the current status of an autonomous-builder-v2 run — overall/phase/task status, budgets, and recent ledger activity — without changing anything.
argument-hint: "[slug — optional; defaults to the most recently modified .features/<slug>/]"
---

The user wants a read-only status report for an **autonomous-builder-v2** run.
The optional argument is a slug:

$ARGUMENTS

Do **not** modify any file or dispatch any building subagent. Produce a
concise report by reading the feature directory:

1. **Locate the feature.** If a slug was given, use `.features/<slug>/`.
   Otherwise pick the most recently modified directory under `.features/`.
   If none exists, say so and stop.

2. **Read and summarise** (per `references/feature-file-format/SKILL.md`):
   - **Overall Status** from `<slug>-design.md` header.
   - **Design gate:** approved or awaiting approval.
   - **Phases** from `<slug>-plan.md` with each phase Status.
   - **Tasks:** for each, its Status, `impl_bounces`/`review_bounces` from the
     ledger header, and the last ledger entry (one line).
   - **Knowledge base:** count of facts in `knowledge.md`.
   - **Reflection / scorecard:** whether they exist yet (terminal only).

3. **Output** a compact summary:

```markdown
**autonomous-builder-v2 status — `<slug>`**

- Overall: <Status>   (design gate: <approved | awaiting>)
- Phase <N>: <name> — <Status>
  - Task <id>: <Status>  (impl <n>/5, review <n>/5) — <last ledger line>
- knowledge.md: <count> facts
- Reflection: <present | not yet>
```

Keep it factual and read-only. If the user wants to resume or change the run,
tell them to use `/autonomous-build` or reply to the orchestrator — do not act
on it from this command.

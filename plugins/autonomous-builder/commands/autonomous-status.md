---
description: List every autonomous-builder plan in `.plans/` with its current status (Done / Blocked / In progress / Awaiting approval / etc.) in a compact table. Use this when you've accumulated several sessions and want to see what's in flight, what's done, and what needs attention. Read-only — does not run the orchestrator or modify any plan.
argument-hint: "(no arguments — lists every .plans/<slug>.md)"
---

The user wants a status overview of every autonomous-builder plan in
the current repo. Do NOT invoke the `autonomous-builder` orchestrator,
the `planner`, or any other subagent. This is a read-only directory
walk + parse you perform yourself.

## Procedure

1. **Glob** `.plans/*.md`. Exclude filenames starting with `_` (those
   are meta-reflections) and filenames ending in `-reflection.md`
   (those are per-session reflection files, not plans).
2. **If no plan files exist**, reply with one line:
   `No plans found under .plans/. Start one with /autonomous-build <goal>.`
   Then stop.
3. **For each plan file**, read just the first ~15 lines (the
   front-matter block) and extract:
   - The `# Plan: <title>` line (the human-readable title).
   - `**Status:**` — one of `Planning` | `Awaiting approval` |
     `Approved` | `In progress` | `Awaiting revision approval` |
     `Done` | `Blocked`.
   - `**Goal:**` — one-line goal restatement.
   - `**Slug:**` — kebab-case slug (typically matches filename).
   - `**Created:**` — date.
4. **If a plan's Status is `In progress` or `Blocked`**, also scan
   the file for the current phase header (`## Phase <N>: <name>`)
   whose `**Status:**` is `In progress` or `Blocked`. Capture the
   phase number and name.
5. **If a `<slug>-reflection.md` companion exists** for a Done /
   Blocked plan, note it so the user knows the retrospective is
   available.

## Output format

Print a compact table to the user. Sort by Status (Blocked first,
then In progress, then Awaiting approval / revision, then Done last)
so attention-needing plans surface at the top. Within each Status
group, sort by Created descending (newest first).

```
Plans in .plans/  (<N> total)

Status              Slug                          Goal                                        Reflection
─────────────────────────────────────────────────────────────────────────────────────────────────────────
⚠ Blocked  Phase 2 extract-auth                   Extract auth into a package                 yes
▶ In prog Phase 3  signup-journey                 New-user signup flow                        —
⏸ Await approval  payment-refactor                Refactor payment processing                 —
⏸ Await revision  rename-foobar                   Rename fooBar → foo_bar                     —
✓ Done             add-hello-command              Add /hello slash command                    yes
✓ Done             plugin-creator-bump-v2         Bump plugin-creator to v2.0                 yes

Cross-session retrospective: <count of *-reflection.md files>
  Run `/autonomous-reflect` for trend analysis (≥3 reflections recommended).
```

Use these glyphs:

- `⚠` Blocked
- `▶` In progress (include phase number/name)
- `⏸` Awaiting approval / Awaiting revision approval
- `✓` Done
- `…` Planning (rare — only seen mid-intake)

## Honest fallback

If a plan file is malformed (no `Status:` line, or unrecognised
Status value), print `? unknown <slug>` in its own row with a
one-line `(unparseable: <reason>)` underneath. Do not skip silently
— a malformed plan file is itself a signal worth surfacing.

## Constraints

- **Do not modify any file.** Read-only.
- **Do not invoke any subagent.** This command does its own
  filesystem walk + parse.
- **Do not dump full plan contents.** Only the header summary +
  current-phase pointer. The user opens a specific plan file if
  they want details.
- **Do not summarise the user's plans into prose.** Give them the
  table; they decide what to act on.

After printing the table, if any plan is Blocked, add a single
line suggesting the next move:
`Tip: open .plans/<blocked-slug>.md to see the latest Blocked escalation message and pick an option.`

Otherwise stop after the table.

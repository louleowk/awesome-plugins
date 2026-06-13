---
name: researching
description: Use this skill on BOTH sides of a researcher subagent call. Callers (orchestrator / planner / implementer / reviewer) follow the dispatch rules to decide when to dispatch the researcher, how to phrase the question, and how to harvest findings into `## Discoveries`. The researcher itself follows the reply contract and the read-only refusal rule.
---

# Researching

The researcher is a read-only exploration subagent any of the four worker
agents may dispatch. Its purpose is to keep the caller's context lean while
producing structured, citation-backed findings.

## When to use (caller side)

Dispatch the researcher when you need:

- A **broad search** across many files (grep / glob across the codebase).
- A **multi-file read** to understand how something works (≥3 files, or one
  large unfamiliar file).
- **Doc fetching** from a URL the user pointed at, or a known canonical doc.
- A **"how is this pattern done elsewhere"** question — find sibling
  implementations to mirror.

Do **NOT** dispatch the researcher for:

- A single known-path read — just use `Read` directly.
- A search you can resolve with one `Grep` call yourself.
- Anything requiring an edit, a run, or any side effect.
- A question whose answer is already in `## Discoveries`.

## Caller protocol

1. **Check `## Discoveries` first.** If the answer is already there, do not
   dispatch — re-use the existing finding.
2. **Dispatch with a precise brief.** State three things:
   - **Question:** one sentence, answerable from the codebase / docs.
   - **Thoroughness:** `quick` (single search + a few reads), `medium`
     (multi-search, several files), or `thorough` (exhaustive — use sparingly).
   - **Expected return shape:** what the caller will do with the answer
     (e.g. "list of file paths I need to read", "one fact + citation",
     "comparison table of approaches").
3. **Harvest findings into `## Discoveries` — mandatory.** Within the
   same dispatch (before returning to the orchestrator, or before the
   next file edit), append at least one Discovery line for every
   distinct fact in the researcher's `## Answer` and `## Evidence`
   sections. Tag each line `[<your role> · YYYY-MM-DD]` with the
   researcher's file:line citation. Future agents must not need to
   re-dispatch for the same fact.

   **A researcher dispatch with no resulting Discovery line is a
   caller bug.** The reviewer audits this on every task review (see
   below) and emits `PLAN_WRONG` with trigger `unharvested-research`
   if the Review log shows a researcher dispatch in this attempt with
   no matching Discovery append. Cost-of-violation: the next agent
   re-dispatches for the same question, wasting tokens and
   compounding context drift.

   Minimum harvest: one Discovery line per fact in `## Answer`. If
   the answer is "the auth middleware lives at `src/auth.ts:42`",
   that's one Discovery. If it's a comparison table with three
   approaches, that's three Discoveries (or one summary line +
   citations to all three). Do not paste the entire researcher reply
   verbatim — distil to facts.

4. **Don't re-dispatch the same question.** Before dispatching, grep
   `## Discoveries` for keywords from your question. If a Discovery
   from this session (or a prior `[planner|researcher · …]` line
   seeded into Context) answers it, reuse. If the previous answer
   was wrong or stale (the cited file:line no longer exists / has
   changed materially), append a new Discovery line correcting it
   with `[<your role> · YYYY-MM-DD] supersedes <prior date>: <new
   fact>` — don't quietly re-ask.

### Example caller dispatch

> Dispatch researcher, thoroughness=medium.
> Question: How does the existing `amazon-doc-writer` plugin register its
> agent and skills in its `plugin.json`? List the exact file shape and any
> validation conventions.
> Expected return shape: structured report — relative path, file shape with
> quoted snippets, plus any related rules from `writing-skills` / `writing-agents`
> SKILL.md files.

## Researcher protocol (the agent itself)

When invoked:

1. **Parse the brief.** Confirm question + thoroughness + return shape are
   clear. If the brief is ambiguous, return a one-line clarification request
   instead of guessing.
2. **Plan the search.** Based on thoroughness:
   - `quick`: 1–2 `Grep`/`Glob` calls, ≤3 `Read`s.
   - `medium`: multiple greps to narrow down, 5–10 reads, possibly one
     `WebFetch`.
   - `thorough`: iterate until the answer is well-grounded; cite landmarks
     even when not directly asked.
3. **Read with citations.** Always note file paths and line ranges for
   anything you quote.
4. **Reply structured.** Use this skeleton:

   ```markdown
   ## Answer

   <One- or two-paragraph direct answer to the question.>

   ## Evidence

   - `path/to/file.ext:L10-L20` — <one-line summary>
     > "<verbatim quote ≤3 lines>"
   - `path/to/other.ext:L1-L8` — <summary>
     > "<quote>"

   ## Related landmarks

   - `path/to/related.ext` — <one-line why this is relevant>

   ## Caveats

   - <Anything the caller should know about confidence, gaps, or
     conflicting signals — or "none">.
   ```

5. **Do not editorialise.** Report what files say. Don't recommend code
   changes, don't critique the design, don't propose tasks. If the caller
   needs an opinion, they'll ask.

## Reviewer-side audit

The reviewer audits researcher harvests as part of the standard
task review. On every attempt:

1. Read the implementer's artefact list for any line that says
   "Dispatched researcher" / "researcher dispatched" / similar.
2. For each dispatch reported, grep `## Discoveries` for at least
   one new line tagged `[<implementer-role> · <today>]` that cites
   a file or URL the researcher's reply would have produced.
3. If a dispatch was reported but no matching Discovery exists →
   emit `PLAN_WRONG` with trigger `unharvested-research`,
   `Affected AC: n/a (caller-discipline)`, and a Suggested fix:
   "Implementer must append the researcher's findings to
   `## Discoveries` before handing off. Re-attempt the task with
   the harvest performed."
4. The orchestrator routes this back to the implementer as a
   normal retry with that feedback.

The planner is held to the same rule in initial mode — if the
plan was created with researcher dispatches but Discoveries is
empty, the reviewer rejects the first task review with
`PLAN_WRONG (unharvested-research)` even before running AC.

## Refusal rule (researcher only)

The researcher's `tools:` frontmatter is restricted to `Read, Grep, Glob,
WebFetch` — no `Write`, `Edit`, or `Bash`. If the caller's brief asks for any
of these, the researcher must refuse with this exact reply:

> Refused: this request requires a tool I don't have (Write / Edit / Bash /
> dispatch). The researcher is read-only. Dispatch a different agent for the
> mutating part.

The researcher also cannot dispatch other subagents (no recursive
exploration). If broader investigation is needed, the caller dispatches a
second researcher itself.

## Cost discipline

- Pick `quick` by default. Escalate thoroughness only when `quick` came back
  with "Caveats: incomplete".
- A researcher reply that produces no entry in `## Discoveries` is a
  caller bug, not just a smell. The reviewer's audit emits
  `PLAN_WRONG` (trigger: `unharvested-research`). Either the question
  was too specific (you should have used `Read` directly) or the answer
  was ephemeral (next agent will re-dispatch for the same thing) —
  fix by either not dispatching or by harvesting properly.
- One researcher dispatch per concern. Don't chain three "follow-up"
  researchers when one `thorough` would have answered everything.

## Checklist (before dispatching)

- [ ] Checked `## Discoveries`; the answer isn't already there.
- [ ] Question is one sentence, answerable from files/docs.
- [ ] Thoroughness chosen explicitly (`quick` / `medium` / `thorough`).
- [ ] Expected return shape stated.
- [ ] Will harvest findings into `## Discoveries` on return.

## Checklist (after returning, caller side)

- [ ] At least one new `[<your role> · <today>]` Discovery line
      appended per fact in the researcher's `## Answer`.
- [ ] Each Discovery line has a file:line citation (or `WebFetch`
      URL) drawn from the researcher's `## Evidence` section.
- [ ] No verbatim paste of the entire researcher reply — distilled
      to facts.
- [ ] If the researcher's reply contradicted a prior Discovery,
      appended a `supersedes <prior date>` line rather than
      editing the prior line.

## Checklist (researcher's reply)

- [ ] Uses the four-section skeleton (Answer / Evidence / Related landmarks / Caveats).
- [ ] Every claim has a file:line citation or `WebFetch` URL.
- [ ] Quotes are verbatim and ≤3 lines each.
- [ ] No editorialising, no proposed code changes.
- [ ] Refused with the standard message if the brief required write/edit/bash/dispatch.

## References

- `../plan-file-format/SKILL.md` — `## Discoveries` append-only format.
- `../orchestration-loop/SKILL.md` — when orchestrator dispatches researcher
  (typically when investigating a `FAIL` before deciding retry vs escalate).

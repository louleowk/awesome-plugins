---
name: researching
description: Use this skill on both sides of a researcher dispatch in autonomous-builder-v2. Any agent may dispatch the researcher; the researcher maintains the shared, list-based per-feature knowledge base (`.features/<slug>/knowledge.md`) with a check-first, append-with-dedupe contract, and answers with cited evidence. Deep-dive is the default — shallow answers defeat the purpose.
---

# Researching (shared knowledge base)

The researcher is a read-only exploration subagent that **any** agent may
dispatch. Its job is to keep callers' context lean while producing
structured, citation-backed findings — and to maintain the shared per-feature
knowledge base so the same question is never researched twice.

## The knowledge base (KB)

- Location: `.features/<slug>/knowledge.md`.
- **List-based**, one fact per bullet, so a human can read, edit, and prune
  it. Entry shape:
  ```
  - [<YYYY-MM-DD> · <agent>] <fact> — <file:line or URL>
  ```
- The KB is durable facts about **this feature's code/area**. There is no
  cross-session memory layer (Decision D5) — knowledge does not leave the
  feature except via a human.

## Caller protocol (any agent)

1. **Check the KB first.** Grep `knowledge.md` for keywords from your
   question. If a fact already answers it, reuse — do not dispatch.
2. **Dispatch with a precise brief:**
   - **Question:** one sentence, answerable from the codebase / docs.
   - **Thoroughness:** `quick` | `medium` | `thorough`. Default toward
     deeper — a shallow answer that the agents then build on wrongly is the
     expensive failure (Decision Q4: deep-dive is required).
   - **Expected return shape:** what you'll do with the answer.
3. **Trust the KB write.** The researcher appends new facts to the KB itself;
   you do not need to copy them. If your dispatch produced **no** new KB
   line, the answer was already known — that's the dedupe signal working.

## Researcher protocol (the agent itself)

1. **Parse the brief.** If ambiguous, return a one-line clarification
   request instead of guessing.
2. **Check the KB first**, then search code / tools / docs to fill gaps.
3. **Deep-dive by default.** Read enough to be *correct*, not just
   plausible. Cite file:line for everything quoted.
4. **Append-with-dedupe to the KB:**
   - Before appending, scan existing lines; if the fact (or a superseding
     form) is already present, do not duplicate.
   - If a prior fact is now wrong/stale, append a superseding line:
     `- [<date> · <agent>] supersedes <prior date>: <new fact> — <cite>`.
   - **Race-safe append:** append only your new lines; never rewrite the
     whole file. If a concurrent write is detected (file changed under you),
     re-read and re-dedupe before appending.
5. **Reply structured:**
   ```markdown
   ## Answer
   <direct answer>

   ## Evidence
   - `path:Lx-Ly` — <summary>
     > "<verbatim ≤3 lines>"

   ## KB updates
   - <the new knowledge.md lines you appended, or "none — already known">

   ## Caveats
   - <confidence / gaps / conflicts, or "none">
   ```

## Refusal rule

The researcher is **read-only**. It never edits product code, never runs
mutating commands, and never writes any file except `knowledge.md`. If a
brief asks for an edit, refuse and return what you found instead.

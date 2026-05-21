---
name: researching-best-practices
description: Use this skill to research the latest industry best practices and trends for AI agents, prompt engineering, tool use, and Claude Code plugins. It defines the search strategy (Google + official docs + GitHub), source-quality ranking, and how to capture citations for a design spec.
---

# Researching Best Practices

This skill drives the **research phase** of designing a Claude Code agent,
skill, or plugin. The goal is to ground every design decision in a recent,
credible, citable source.

## When to use

- Before producing any design spec in the `ai-tool-designer` agent.
- Whenever the user asks "what's the latest / state-of-the-art / best
  practice for X" relating to AI agents or Claude Code tooling.
- When a previous design needs to be refreshed against newer guidance.

## Search strategy

Run **2–5 targeted searches**, not a single broad one. Combine these axes:

1. **Authoritative docs**
   - `site:docs.claude.com` or `site:docs.anthropic.com` + topic.
   - Example: `site:docs.claude.com plugin marketplace manifest`.
2. **Official GitHub**
   - `site:github.com/anthropics <topic>`.
   - `claude code <topic>` on GitHub code search for real examples.
3. **Community patterns**
   - Google: `claude code agent best practices 2025`.
   - Google: `AI agent design patterns 2025`.
   - Google: `prompt engineering tool use <year>`.
4. **Trend / recency check**
   - Restrict to the last 12 months when the platform changes quickly.
   - Cross-check at least two sources before treating a pattern as
     "best practice".

## Source-quality ranking

When sources disagree, prefer in this order:

1. Anthropic / Claude Code official documentation.
2. Anthropic blog or Anthropic-maintained GitHub repos.
3. Reputable engineering blogs and conference talks from the last year.
4. Community write-ups and Stack Overflow / Reddit threads (treat as hints,
   not as ground truth).

If only low-quality sources exist for a claim, explicitly mark it as
*"community pattern, not officially documented"* in the design spec.

## Workflow

1. List the 3–5 questions the design needs answered (e.g. "How should an
   agent declare its tools?", "When should I prefer a skill over an agent?",
   "What does a plugin manifest require?").
2. For each question, run **one** focused query. Prefer specific phrases
   over single keywords.
3. Use `WebFetch` on the top 1–2 results to read actual content. **Do not**
   rely on search snippets alone — they are often misleading or outdated.
4. Extract concrete, quotable findings. Record:
   - The claim (1 sentence).
   - The source title.
   - The full URL.
   - The publish or last-updated date if visible.
5. Deduplicate. If two sources say the same thing, cite the more
   authoritative one.

## Capturing citations

In the final design spec, every best-practice bullet must look like:

```
- <Concrete claim or pattern> — <Source title>, <URL> (<date if known>)
```

## Guardrails

- **Never put user-private data in a search query.** Strip proprietary
  identifiers, code, or secrets before searching.
- **Don't fabricate URLs.** If `WebFetch` failed for a source, drop it; do
  not cite a page you didn't actually retrieve.
- **Time-box research.** 2–5 searches and 2–4 fetches is usually enough.
  Stop once you have 3–7 well-sourced findings.
- **Distinguish opinion from doc.** Phrase community patterns as
  "commonly recommended" and official guidance as "documented".

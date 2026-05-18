---
name: writing-coe
description: Use this skill when authoring an Amazon Correction of Errors (COE) document — the post-incident write-up that captures what happened, why, and what will change. Provides the full COE template including incident summary, customer impact, timeline, 5 Whys, and action items. Load alongside the `amazon-writing-style` skill.
---

# Writing a Correction of Errors (COE)

A COE is Amazon's post-incident document. It is a blameless, mechanism-focused
narrative that explains: what broke, how customers were impacted, what
happened minute-by-minute, the underlying causes (via 5 Whys), and the
specific mechanisms that will prevent recurrence.

A COE is read by senior engineers and leadership. The bar is high: vague
causes, missing action items, or owner-less commitments will be rejected.

## When to use

- The user asks for a "COE", "Correction of Errors", "post-mortem",
  "incident write-up", or "incident review document".
- A customer-impacting incident has occurred (or a significant near-miss) and
  needs a written review.

If the user wants a generic post-incident *analysis* without the 5 Whys /
action-item discipline, consider `writing-analysis-report` instead.

## Length budget

- ~4–6 pages of body.
- Timeline and raw logs go in the Appendix if they would otherwise dominate
  the page.

## Tone

- **Blameless.** Describe systems, mechanisms, and decisions — not
  individuals. Use roles ("the on-call engineer") not names.
- **Mechanism-focused.** Every action item must be a durable mechanism
  (alarm, automation, contract, test), not "be more careful" or "add training".
- **Honest.** Do not soften severity or impact. The COE exists to make the
  org stronger, not to make the team look good.

## Section template

```markdown
# COE: <Short Incident Name>

**Author(s):** <names>
**Date of COE:** <YYYY-MM-DD>
**Date of incident:** <YYYY-MM-DD>
**Severity:** SEV-1 | SEV-2 | SEV-3
**Status:** Draft | In Review | Approved
**Service(s) affected:** <…>

## 1. Incident Summary

<2–4 sentences. What happened, when, for how long, and what customer
experience broke. A reader who stops here should know the headline.>

## 2. Customer Impact

<Quantified. Use the format:
- **Affected customers:** <count, % of total, geography>
- **Duration of impact:** <start UTC → end UTC, total minutes>
- **What customers experienced:** <prose — error messages, failed operations,
  data loss, degraded performance, etc.>
- **Money / SLA impact:** <credits issued, contracts breached, $ estimate>
If a number is unknown, say "unknown" and add it to Open Questions — do not
omit the line.>

## 3. Incident Timeline (all times UTC)

| Time (UTC) | Event |
| --- | --- |
| YYYY-MM-DD HH:MM | <trigger / change / first signal> |
| HH:MM | <detection — who/what detected it> |
| HH:MM | <escalation> |
| HH:MM | <mitigation attempted> |
| HH:MM | <mitigation effective> |
| HH:MM | <full recovery / all-clear> |

<Include detection-time, time-to-engage, time-to-mitigate, time-to-recover
metrics derived from the timeline.>

## 4. What Happened

<Narrative explanation of the failure mode. Walk through the system from
trigger → propagation → customer impact. Reference the timeline. Include or
link diagrams of the affected flow. Be specific: name the components, the
configurations, the limits hit.>

## 5. 5 Whys (Root Cause Analysis)

Start from the customer-visible failure and ask "why?" at least five times.
Branch where multiple causes contribute.

1. **Why did customers see <symptom>?** — Because <…>
2. **Why did <that> happen?** — Because <…>
3. **Why?** — Because <…>
4. **Why?** — Because <…>
5. **Why?** — Because <root cause, typically a missing mechanism>

<Where there are multiple contributing root causes (e.g. a latent bug + a
deployment process gap + a missing alarm), run a separate 5-Whys branch for
each. Each branch must terminate in a missing or broken mechanism, not in a
human error.>

## 6. What Went Well

<Specific things that limited the blast radius or sped recovery —
e.g. "throttling at the edge contained impact to one region",
"runbook for X was up to date and used". Keep honest and short.>

## 7. What Went Wrong

<Specific gaps, beyond the root cause itself — detection lag, missing
runbook, unclear ownership, alarm fatigue, etc.>

## 8. Action Items

| # | Action item | Type | Owner | Due date | Tracking link |
| - | --- | --- | --- | --- | --- |
| 1 | <specific, verifiable change> | Prevent / Detect / Mitigate / Process | <name or team> | YYYY-MM-DD | <ticket> |

<Rules:
- Every action item must be specific and verifiable ("Add alarm on X with
  threshold Y, page sev-2"), not aspirational ("improve monitoring").
- Every item has an owner (person or single team) and a due date.
- Tag each as Prevent (stops recurrence), Detect (catches it sooner),
  Mitigate (reduces impact), or Process (changes how we work).
- Prefer Prevent + Detect over Mitigate + Process.
- "Add training" / "be more careful" are not valid action items.>

## 9. Lessons Learned

<2–4 short paragraphs. What does the org now understand that it didn't
before? What patterns elsewhere in our systems share this failure mode and
should be audited?>

## 10. Open Questions

- <unresolved facts and who owns resolving them>

## Appendix

- A. Full timeline with log excerpts
- B. Graphs (latency, error rate, traffic) for the incident window
- C. Related tickets, alarms, and prior COEs with similar root causes

## Sources

- `<relative path>` — <what it provided>
```

## How to apply

1. **Read every source file** the user provides: incident chat transcripts,
   alarm history, deploy log, graphs, prior COEs on related systems. Build
   the timeline first — most other sections depend on it.
2. **Quantify customer impact.** If a number isn't in the sources, list it as
   "unknown" and add it to Open Questions; never invent.
3. **Convert the timeline into derived metrics** (time-to-detect,
   time-to-mitigate, time-to-recover). Put them right after the table.
4. **Run 5 Whys, branched.** Most real incidents have 2–3 contributing causes
   (e.g. latent bug + missing alarm + slow rollback). Each branch terminates
   in a missing/broken **mechanism**, not in a person.
5. **Write Action Items in the verifiable form.** Each one should be
   reviewable later as "did this ship, yes/no". Prefer Prevent and Detect.
6. **Keep tone blameless.** Replace names with roles. Replace "X forgot to…"
   with "the system did not enforce…".
7. **Cross-reference prior COEs** with similar root causes if the sources
   include them. Repeat offenders need a different class of action item.
8. Apply the `amazon-writing-style` self-review checklist.

## Common failure modes to avoid

- 5 Whys stops at "human error". Keep asking why — the answer is usually a
  missing guardrail.
- Action items that say "review" or "consider" instead of a concrete change.
- Action items with no owner or no due date.
- Customer-impact section without numbers.
- Timeline in local time instead of UTC.
- Naming individuals or assigning blame.
- "What went well" is empty (there is almost always something — be specific)
  or padded with platitudes.

## Checklist

- [ ] Severity, services affected, and dates in the header.
- [ ] Customer impact is quantified (count, duration, $, or explicit
      "unknown" with an Open Question).
- [ ] Timeline is in UTC and yields time-to-detect/mitigate/recover.
- [ ] 5 Whys runs to a missing **mechanism**, branched where multiple causes
      contribute.
- [ ] Every Action Item is specific, verifiable, owned, dated, and tagged
      Prevent / Detect / Mitigate / Process.
- [ ] Tone is blameless throughout (roles, not names).
- [ ] Lessons Learned identifies systems elsewhere that share the failure mode.
- [ ] Sources listed; open questions called out.
- [ ] `amazon-writing-style` self-review checklist passes.

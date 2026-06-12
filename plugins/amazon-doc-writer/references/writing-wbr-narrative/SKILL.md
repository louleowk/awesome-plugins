---
name: writing-wbr-narrative
description: Use this skill when authoring the written narrative that accompanies an Amazon Weekly Business Review (WBR) metrics deck. Provides the template for week-over-week commentary, anomaly call-outs, root-cause notes for variances, and the rules for honest, terse, data-grounded prose. Load alongside the `amazon-writing-style` skill.
---

# Writing a WBR Narrative

A Weekly Business Review (WBR) is Amazon's standing weekly metrics review.
The metrics live in a deck of charts; the **narrative** is the short written
commentary that explains the *interesting* movement in those charts —
variances, anomalies, leading indicators, and ongoing initiatives' effect on
the metrics.

A good WBR narrative is short, dense, and never restates what the chart
already shows. It tells the reader *why* the line moved.

## When to use

- The user asks for a "WBR narrative", "WBR commentary", "weekly business
  review writeup", or "metrics deck commentary".
- The user provides a metrics deck, dashboard export, or numbers table and
  wants the written commentary that goes with it.

If the user wants a deeper, one-time investigation rather than weekly
recurring commentary, use `writing-analysis-report` instead.

## Length budget

- ~1–2 pages total.
- Per-metric blurb: typically 2–5 sentences. If a metric needs more, it
  belongs in a separate deep-dive doc.

## Section template

```markdown
# WBR Narrative — Week of <YYYY-MM-DD>

**Author(s):** <names>
**Date:** <YYYY-MM-DD>
**Coverage period:** <YYYY-MM-DD → YYYY-MM-DD> (WoW), <YYYY-MM-DD → YYYY-MM-DD> (YoY)

## Headline

<2–3 sentences. The one or two things leadership should know from this
week's metrics. Not a chart summary — a judgement: are we on plan or off,
and why.>

## Top callouts

1. **<Metric name>: <direction + magnitude>** — <one-line reason and what is
   being done about it, with owner if action is in flight>.
2. **<Metric name>: <…>** — <…>
3. **<Metric name>: <…>** — <…>

(3–5 callouts. Pick the movements that are decision-relevant, not the
biggest absolute numbers.)

## Metric commentary

> Cover every metric in the deck that moved more than its expected band, or
> that has a known story this week. Skip metrics that are flat and uninteresting.

### <Metric Name>

- **This week:** <value> (<unit>)
- **WoW:** <±X%> | **vs plan:** <±Y%> | **YoY:** <±Z%>
- **Commentary:** <2–5 sentences. Lead with the why, not the what. If the
  movement was driven by a known initiative, name it. If by an external
  factor (holiday, outage, seasonality), name it. If unknown, say so and
  flag for follow-up.>
- **Action / follow-up:** <if any, with owner and date>

### <Metric Name>
…

## Anomalies and data-quality notes

- <metrics where the data is suspect this week and why>
- <known instrumentation changes that affect comparability>

## Watchlist for next week

- <leading indicators we expect to move and why>
- <metrics where a threshold was breached or is about to be>

## Sources

- `<relative path>` — <what it provided>
```

## How to apply

1. **Read the metrics inputs first.** Get this week's values, last week's,
   plan, and YoY for every metric the user supplies. If any are missing,
   list them under data-quality notes — don't infer.
2. **Compute deltas in the user-provided units.** Always show WoW, vs plan,
   and YoY together. If a denominator is too small for a percentage to be
   meaningful, show the absolute change instead.
3. **Write the headline last.** It is the synthesis of the per-metric
   commentary, not a preview.
4. **Be honest about misses.** Down-weeks don't get hedged. Name the cause
   if known; mark it as under investigation if not.
5. **Avoid chart restatement.** "Orders were up 5% week-over-week" adds
   nothing the chart didn't already show. Instead: "Orders were up 5% WoW,
   driven by the Tuesday promotion email which over-delivered (+12% open
   rate vs plan)."
6. **Tag movements as initiative-driven, external, or unexplained.** If
   unexplained, add it to the watchlist or open a follow-up.
7. **Action items are inline**, not in a separate table — each metric blurb
   carries its own follow-up with owner.
8. Apply the `amazon-writing-style` self-review checklist.

## Common failure modes to avoid

- Narrative restates the charts. Cut every sentence the chart already says.
- Down-weeks get euphemisms ("modest softness"). Use the actual number.
- Movements are reported without a cause or an "unknown — investigating"
  tag.
- Every metric gets a blurb regardless of whether it moved. Cover only the
  decision-relevant ones; the rest of the deck speaks for itself.
- Comparisons mix bases (e.g. WoW % alongside YoY absolute) without saying
  so.
- No watchlist, so the same surprise lands again next week.

## Checklist

- [ ] Coverage period and comparison windows stated in the header.
- [ ] Headline is a judgement (on-plan / off-plan and why), not a chart
      summary.
- [ ] 3–5 top callouts, each with a one-line reason and (if any) an owned
      action.
- [ ] Every covered metric shows this-week value, WoW, vs plan, YoY in
      consistent units.
- [ ] Movements tagged as initiative-driven, external, or unexplained.
- [ ] Data-quality and instrumentation issues called out separately so
      readers don't over-interpret.
- [ ] Watchlist sets expectations for next week.
- [ ] Sources listed.
- [ ] `amazon-writing-style` self-review checklist passes.
```

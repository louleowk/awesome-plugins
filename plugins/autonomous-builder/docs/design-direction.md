# Autonomous-builder — process, subagent interaction & direction

> **Status:** living document. **v2 design — all architecture decisions
> (D1–D8) RESOLVED; build-ready.** §1–§5 describe the agreed design; §6
> records each decision + answer. §6.B (metrics) stays deferred until we
> have usage data.
>
> Last updated: 2026-06-21 (v2 redesign — decisions resolved)

---

## 1. What this is

`autonomous-builder` orchestrates a multi-step code change end-to-end.
**v2 adds a single design gate before execution and an inner
task-coordination loop** so each task is implemented, tested, and reviewed
as a unit:

```
intake
  → design        → user approval        (.features/<slug>/<slug>-design.md)
  → plan          (projected from the approved design — NO separate gate)
  → per-phase task loop
        task-coordinator { implementer → tester → reviewer
                           → advance / retry / escalate / revise-plan }
  → phase checkpoint
  → wrap-up
```

The **design gate is the only mandatory approval before code** (D7): if the
design is detailed enough, the plan is a mechanical projection of it and
doesn't need its own gate. A single **orchestrator** agent runs the
top-level state machine and is the only writer of overall / phase status
and the only agent that talks to the user. Inside each task, a
**task-coordinator** runs the implement → test → review micro-loop and
reports a terminal task verdict back up.

**Per-task ledger (D1).** Every task has a shared ledger
(`.features/<slug>/tasks/<task-id>.md`) the inner-loop agents append to:
the implementer lists files changed + why; the tester lists tests
added/inspected + recommendations; the reviewer adds its opinion on top.
The ledger is the shared working memory for the loop and a human-readable
trail of how the task was built.

**Cast of agents** (v2 — designer replaces planner; task-coordinator is
new; implementer owns green tests)

| Agent              | Role                                                                                                              | Talks to user? | Edits code? |
| ------------------ | --------------------------------------------------------------------------------------------------------------- | :------------: | :---------: |
| `orchestrator`     | Runs the top-level state machine, owns overall/phase status writes, owns every user touchpoint                  |       ✅       |     ❌      |
| `designer`         | Senior technical role: drafts/revises the design **and** the projected plan; holds **office hours** for the task-coordinator (two modes: `design`, `plan`) under `.features/<slug>/` |       ❌       |     ❌      |
| `task-coordinator` | Owns one task's inner loop: dispatches implementer → tester → reviewer, owns retry budgets, writes task status, returns the task verdict |       ❌       |  ❌  |
| `implementer`      | Makes the minimal **product-code** edits **and writes tests for its own changes**; must get **all tests green** before filing for review |   ❌   |  ✅ (product + tests) |
| `tester`           | Inspects test **thoroughness** vs. the AC; **adds missing tests itself**; bounces to the implementer (via TC) **only when the implementation is wrong** |   ❌   |  ✅ (test code only) |
| `reviewer`         | Verifies a task against its AC **and the ledger**; emits PASS / FAIL / PLAN_WRONG                                |       ❌       |     ❌      |
| `researcher`       | Read-only exploration; **maintains a shared, list-based knowledge base per feature**; returns cited findings     |       ❌       |     ❌      |
| `reflector`        | At terminal states, writes a retrospective **for the developers** — prompt-tuning / design / workflow fixes (not fed back to the agent at runtime) |       ❌       |     ❌      |

_Decisions resolved in this section: **D1** (status + per-task ledger),
**D2** (implementer owns green tests; tester inspects/adds), **D3**
(designer owns design + plan) — see §6._

---

## 2. Invocation

### User → orchestrator (entry points)

- **Slash command** `/autonomous-build <goal>` — hands the goal to the
  orchestrator verbatim. Acts as a **goal-shaping gate** first:
  - ✓ Well-shaped: `verb + concrete object + scope/surface`
    (e.g. "Add a `/version` command to plugin-creator that prints the
    version from `plugin.json`").
  - ✗ Under-specified ("refactor the codebase") → one targeted question.
  - ✗ Over-specified (a pre-written diff) → bounce; not a planning job.
- **Direct** — "build this autonomously", "plan then implement", or any
  multi-step goal matching the agent's `description` triggers.

### Orchestrator → subagents (dispatch payloads)

| Subagent           | Invoked by                       | Invoked with                                                                         |
| ------------------ | -------------------------------- | ------------------------------------------------------------------------------------ |
| `designer`         | orchestrator                     | mode (`design`/`plan`, each + `revision`), feature dir, (revision) the trigger; **office-hours: a task-coordinator question + the task ledger** |
| `task-coordinator` | orchestrator                     | feature dir, task ID, phase ID, the task's AC + dependencies                          |
| `implementer`      | task-coordinator                 | feature dir, task ID, ledger path, attempt number, (retries) previous bounce reason  |
| `tester`           | task-coordinator, reviewer       | feature dir, task ID, ledger path, the changed surface, regression scope             |
| `reviewer`         | task-coordinator                 | feature dir, task ID, ledger path, AC mode (`fast-only`/`fast+full`/`dod`)            |
| `researcher`       | **any agent**                    | question, thoroughness, expected return shape (checks shared KB first)               |
| `reflector`        | orchestrator                     | feature dir, slug, terminal Status (`Done`/`Blocked`), optional note                 |

**Dispatch rules** (v2)

- The **orchestrator** dispatches `designer`, `task-coordinator`, and
  `reflector` (and may dispatch `researcher` directly when investigating
  a repeated `failure_mode`).
- The **task-coordinator** dispatches `implementer`, `tester`, and
  `reviewer` — it owns the inner per-task loop, the retry budgets, and the
  task ledger.
- **Designer office hours (D6).** The task-coordinator may dispatch the
  `designer` with a question when it suspects the design/plan is wrong.
  The designer answers from the design doc (read-only advice — no status
  writes). If the answer implies the plan must change, the
  task-coordinator returns `PLAN_WRONG` to the orchestrator rather than
  editing the plan itself.
- **Session reuse (D6).** The task-coordinator keeps a **session-reuse
  list** mapping `{task-id → implementer/tester/reviewer session handles}`
  so a retry re-enters the *same* subagent session instead of
  re-populating context. The ledger is the durable fallback if a session
  can't be reused.
- The **reviewer** may dispatch `researcher` and `tester` any time it
  needs more evidence.
- **Any agent may dispatch `researcher`** to obtain more information.
- `researcher` maintains a **centralized, shared knowledge base per
  feature** (`.features/<slug>/knowledge.md`), kept **list-based** so a
  human can read, edit, and prune it easily.
- `researcher` **checks the shared knowledge base first**, then falls
  back to the code, tools, and other sources to fulfil the request — and
  writes new findings back to the KB.
- Workers return structured data to their caller; they never message the
  user. Only the orchestrator talks to the user.

_Decisions resolved in this section: **D4** (researcher fan-out / KB entry
shape), **D5** (no cross-session memory layer), **D6** (office hours +
session reuse) — see §6._

---

## 3. Workflow (state machine)

Step-by-step. Indentation = nesting; `→` = transition; `[?]` = decision.

```
1. INTAKE
   - Pick slug; create .features/<slug>/<slug>-design.md   (Status: Design)
   - Seed .features/<slug>/knowledge.md (shared KB, empty list)

2. DESIGN   (every change earns a design — small or large)
   - Dispatch designer (mode: design). The design must be clear on:
       • changing components
       • changing / new APIs
       • key decisions (new libs, new tools, new patterns, trade-offs)
       • the potential scope of the feature (so the user can judge size)
   - designer ⇒ design doc                         (Status: Awaiting design approval)

3. APPROVE DESIGN   [?] User approves?   (this is the ONLY pre-code gate — D7)
   - edit    → back to DESIGN (designer, mode: design + revision)
   - approve → (Status: Design approved → In progress)

4. PLAN   (no separate gate — projected from the approved design)
   - Dispatch designer (mode: plan) to project the approved design into
     phases + tasks + tiered AC at .features/<slug>/<slug>-plan.md
   - designer ⇒ plan. The orchestrator shows it to the user as an FYI but
     does NOT block on approval (the design was the gate).

5. EXECUTE — for each PHASE in order (set phase: In progress):
   For each TASK in phase (honour "Depends on"):
     - Dispatch task-coordinator(task_id); create .features/<slug>/tasks/<task-id>.md (ledger)
       INNER LOOP (task-coordinator) — two independent budgets, 5 each (D8):
         impl_bounces = 0..5   (implementation-wrong bounces)
         review_bounces = 0..5 (reviewer FAIL bounces)

         a. Dispatch implementer (product code + its own tests; MUST get
            all tests green; append to ledger: files changed + why)
              - reuse the implementer session if one exists (D6)
         b. Dispatch tester (inspect test thoroughness vs AC; ADD missing
            tests itself; append to ledger: tests added/inspected + notes)
            [?] tester finds the IMPLEMENTATION wrong?
                - yes → impl_bounces++; bounce to implementer (a)
                        if impl_bounces = 5 → return ESCALATE to orch
                - no  → continue
         c. Dispatch reviewer (fast-only, or fast+full on the Done attempt;
            review against AC + ledger; append opinion to ledger)
            [?] Reviewer verdict:
                - PASS                          → task Done; return to orch
                - FAIL                          → review_bounces++; bounce to (a)
                                                  if review_bounces = 5 → ESCALATE
                - PLAN_WRONG                    → return PLAN_WRONG to orch
                                                  (after designer office hours, b/D6)

     - task-coordinator ⇒ orchestrator:
         { verdict, impl_bounces, review_bounces, last_failure_mode, evidence }
       [?] orchestrator routes:
           - Done       → next task
           - ESCALATE   → ADAPTIVE_ESCALATE (5d)
           - PLAN_WRONG → REVISE_PLAN (5e)

   5b. PHASE DEFINITION OF DONE:
       - Dispatch reviewer (dod mode); tester runs any [Journey] AC
       [?] DoD PASS?
           - no  → re-open last task via task-coordinator → back to inner loop
           - yes → continue

   5c. Phase Done → post PHASE CHECKPOINT to user
       [?] More phases? yes → next phase | no → WRAP-UP (6)

   5d. ADAPTIVE_ESCALATE:
       - Dispatch researcher (medium): "why is failure_mode blocking?"
       [?] AC/plan/design the problem?
           - yes → REVISE_PLAN (5e)
           - no  → Status: Blocked; escalate to user; dispatch reflector
                   → PAUSE (wait for user direction)

   5e. REVISE_PLAN / REVISE_DESIGN:
       - If the plan alone is wrong: dispatch designer (mode: plan + revision),
         apply, resume the revised task.
       - If the DESIGN is wrong: Status: Awaiting design approval; dispatch
         designer (mode: design + revision); re-run the design gate (step 3).
       [?] User approves?
           - approve → apply; (In progress); resume revised task → 5
           - reject  → Status: Blocked; escalate (as 5d "no")
           - edit    → re-dispatch designer → ask again

6. WRAP-UP (all phases Done)
   - overall Status: Done; dispatch reflector (Done)
   - reflector writes a retrospective FOR THE DEVELOPERS (prompt/design/
     workflow improvements) — it is NOT fed back into the agent at runtime
   - reflector appends a FEATURE SCORECARD to .features/<slug>/scorecard.md
     (one row per feature — see §6.B for the fields)
   - Send summary + reflection link to user
```

_Decisions resolved in this section: **D6** (office hours + return shape),
**D7** (single design gate, no plan gate), **D8** (tester bounces to
implementer; 5+5 budgets) — see §6._

### Key control mechanisms

- **Reviewer AC modes:** `fast-only` (cheap early iterations),
  `fast+full` (the about-to-Done attempt), `dod` (phase verification
  incl. journeys).
- **Two retry budgets, 5 each (D8):** `impl_bounces` (tester found the
  implementation wrong) and `review_bounces` (reviewer FAIL) are counted
  separately; either hitting 5 escalates the task.
- **Implementer owns green (D2):** the implementer writes its own tests
  and must get them passing before review; the tester adds missing tests
  and only bounces when the *implementation* (not the test) is wrong.
- **Designer office hours (D6):** the task-coordinator can ask the
  designer a question mid-task; if the answer implies a plan/design change
  it returns PLAN_WRONG rather than editing the plan itself.
- **Session reuse (D6):** retries re-enter the same subagent session;
  the ledger is the durable fallback.
- **MoSCoW AC priorities:** only `Must` `[Fast]`/`[Full]` failures cause
  FAIL/retry; `Should` → WARN, `Could` → INFO (surfaced in checkpoints,
  never blocking).
- **Always reflect** at terminal states (`Done` or `Blocked`).

---

## 4. Subagent interaction (sequence)

Notation: `A → B: x` means A dispatches/sends x to B. `B ⇒ A: y` means B
returns y to A. Indentation shows nesting.

```
DESIGN   (the only pre-code approval gate)
  User    → Cmd:   goal text
  Cmd     → Orch:  hand off goal verbatim
  Orch:            intake — pick slug, create .features/<slug>/ + knowledge.md
  Orch    → Des:   dispatch(design, feature_dir)
    [opt] Des  → Res:  dispatch(question)            // any agent may research
          Res  ⇒ Des:  Answer + KB update
  Des     ⇒ Orch:  design doc + scope summary
  Orch    → User:  design-approval message
  User    ⇒ Orch:  approve

PLAN   (projected from approved design — NO gate, FYI only)
  Orch    → Des:   dispatch(plan, feature_dir)
  Des     ⇒ Orch:  plan (phases, tasks, tiered AC)
  Orch    → User:  "here's the plan" (informational; not blocking)

PER-PHASE TASK LOOP   (orchestrator dispatches one task-coordinator per task)
  Orch    → TC:    dispatch(task_id, AC, deps)
  TC:              create ledger .features/<slug>/tasks/<task-id>.md
    INNER LOOP (TC owns budgets: impl_bounces 0..5, review_bounces 0..5):
      TC    → Impl: dispatch(task_id, ledger)        // reuse session if exists
        [opt] Impl → Res: dispatch(question)          // checks shared KB first
              Res  ⇒ Impl: Answer + Evidence
      Impl  ⇒ TC:  product code + own tests (ALL GREEN) + ledger: files+why
      TC    → Test: dispatch(task_id, ledger, changed surface, regression scope)
      Test:         inspects thoroughness; ADDS missing tests itself
      Test  ⇒ TC:  ledger: tests added/inspected + verdict
            implementation wrong  → impl_bounces++; → Impl  (or ESCALATE at 5)
            tests OK              → continue to reviewer
      TC    → Rev:  dispatch(task_id, ledger, fast-only | fast+full)
        [opt] Rev → Res:  dispatch(question)
        [opt] Rev → Test: dispatch(re-run / extra test)
      Rev   ⇒ TC:  verdict (PASS / FAIL / PLAN_WRONG) + ledger: opinion
            PASS        → task Done; break inner loop
            FAIL        → review_bounces++; → Impl  (or ESCALATE at 5)
            PLAN_WRONG  → office hours, then break → PLAN_WRONG
        [opt, on suspected plan/design fault] TC → Des: dispatch(office-hours, question, ledger)
              Des ⇒ TC:  advice (read-only; no status write)
  TC      ⇒ Orch:  { verdict, impl_bounces, review_bounces, last_failure_mode, evidence }
          Done       → next task
          ESCALATE   → ADAPTIVE_ESCALATE
          PLAN_WRONG → REVISE_PLAN / REVISE_DESIGN

PHASE DEFINITION OF DONE
  Orch    → Rev:   dispatch(phase_id, dod)
    [opt] Rev   → Test: dispatch(journey AC, surface, entry point)  // [Journey] AC
          Test  ⇒ Rev:  journey log (PASS / FAIL / INCONCLUSIVE)
  Rev     ⇒ Orch:  DoD verdict
  Orch    → User:  phase checkpoint
  User    ⇒ Orch:  continue

ADAPTIVE_ESCALATE  (on block)
  Orch    → Res:   dispatch(medium, "why is failure_mode blocking?")
  Res     ⇒ Orch:  finding
          plan is the problem:
            Orch → Des:  dispatch(plan + revision, PLAN_WRONG reason)
            Des  ⇒ Orch: revised plan; resume revised task (no user gate)
          design is the problem:
            Orch → Des:  dispatch(design + revision, reason)
            Des  ⇒ Orch: revised design
            Orch → User: design-approval message (re-run the gate)
            User ⇒ Orch: approve
          genuine block:
            Orch:        Status: Blocked
            Orch → User: blocked escalation
            Orch → Refl: dispatch(feature_dir, slug, "Blocked")
            Refl ⇒ Orch: reflection file

WRAP-UP  (all phases Done)
  Orch:            overall Status: Done
  Orch    → Refl:  dispatch(feature_dir, slug, "Done")
  Refl    ⇒ Orch:  developer retrospective (prompt/design/workflow fixes)
                   + feature scorecard row
  Orch    → User:  wrap-up summary + reflection link
```

_Decisions raised by this section: **D8** (tester-before-reviewer; does a
tester FAIL burn a retry?) — see §6._

---

## 5. What makes the agent succeed (the levers)

The three obvious levers — **context**, **plan**, **review/tests** — are
the spine. They are necessary but not sufficient: each is capped by three
behavioral layers wrapped around them.

| # | Lever                       | What it forces                                  | Where it lives in v2                                                    |
| - | --------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------- |
| 1 | **Accurate context**        | Read, don't guess; cite; dedupe                 | `researcher` + **shared `knowledge.md` KB (check-first, deep-dive)**     |
| 2 | **Shared understanding**    | Human sees scope before code                    | **design gate** (the single pre-code approval; D7)                       |
| 3 | **Well-shaped plan**        | Objective AC; projected from the design         | designer `plan` mode + tiered MoSCoW × `[Fast]/[Full]/[Journey]` AC      |
| 4 | **Better review & tests**   | "Looks done" → "is done"                        | per-task `tester` (writes tests) + mandatory `reviewer` + 3-verdict       |
| 5 | **Honesty** (contract)      | Prove what you did                              | validation block (exit codes, paths, line counts); caller rejects if missing |
| 6 | **Rigor** (engineering bar) | Hit the senior bar                              | ≥2 sibling citations, pre-mortem, 5-Whys before shortcut, banned phrases |
| 7 | **Adaptive control**        | Know when to stop                               | task-coordinator inner retry + orchestrator `Blocked` escalation        |
| 8 | **Learning** (offline)      | Each session yields developer-facing improvements | `reflector` blameless 5-Whys → prompt / design / workflow fixes **we** apply |

### How they compose

```
Shared KB + context  →  Design (gate)  →  Plan  →  Implement → Test → Review
(researcher,             (scope shown      (phases +   (task-coordinator inner loop)
 knowledge.md)            to user)          tiered AC)
      ^                       ^                ^                        |
      |                       |                +---- repeated failure --+
      |                       +----------- design wrong -----------------+
      |                                                                 v
  (within one feature)                                            Reflection
                                                          (developer-facing 5-Whys)
                                                                       |
                                                                       v
                                               WE improve the agents offline
                                            (prompt tuning, design, workflow fixes)
```

- Forward path: shared context feeds the **design**, the approved design
  drives the per-task implement → test → review loop.
- A **repeated failure_mode** loops back to the plan; a deeper mismatch
  loops back to the **design** (the design, not just the plan, was wrong).
- **Reflection** is an **offline output for the developers**, not a
  runtime feedback loop. At a terminal state the reflector writes a
  blameless retrospective; **we** read it and improve the agents (prompt
  tuning, better design, workflow fixes). The running agent does **not**
  consume its own reflection.

**One-line thesis:** context + design + plan + review are the spine, but
they only scale when wrapped in **honesty** (prove it), **rigor** (senior
bar), and **offline learning** (each session produces a retrospective
*we* use to improve the agents). v2's bet is that a **shared knowledge
base** and an explicit **design gate** raise the floor on the two weakest
levers — context depth and shared understanding.

### Notes on the traps

- **More context ≠ better.** Dumping the whole repo poisons the window.
  Curated, cited, deduplicated context wins.
- **"Detailed plan" is the wrong target — "well-shaped" is the right one.**
  The biggest churn driver is an under-/over-specified *goal*, not a thin
  plan.
- **Banned-phrase list is the highest-leverage single intervention.**
  Agents rewrite to avoid "should work" / "appears to" / "likely" /
  "left as future work", which incidentally forces them to gather the
  evidence those phrases were hiding.

---

## 6. Decisions to make

> **Status: all architecture decisions (D1–D8) are RESOLVED.** The body
> (§1–§5) reflects these answers — the design is build-ready. Each entry
> keeps the original question + your answer for the record. §6.B (metrics)
> stays deferred until we have usage data.

### A. Architecture decisions — RESOLVED

**D1 — Task status ownership + per-task ledger.** _(§1)_ ✅ RESOLVED
Who writes `task Done/Blocked`?
- **Resolved:** the **task-coordinator owns task-level status**;
  orchestrator owns phase/overall. Every task has a shared **ledger**
  (`.features/<slug>/tasks/<task-id>.md`): implementer lists files changed
  + why; tester lists tests added/inspected + recommendations; reviewer
  adds its opinion on top. The user can read the ledger to follow the
  process.

**D2 — Implementer vs tester division of labour.** _(§1)_ ✅ RESOLVED
Who writes tests, who makes them pass, when does work bounce back?
- **Resolved (implementer-owns-green):** the **implementer** writes
  product code **and** tests for its own changes and must get **all tests
  green** before filing for review. The **tester** inspects test
  *thoroughness* against the AC and **adds missing tests itself** — it
  does **not** kick simple gaps back. The tester bounces to the
  implementer (via the task-coordinator) **only when the implementation is
  wrong**. The task-coordinator stores subagent sessions so the loop
  reruns without re-populating context (see D6 session reuse).
- **Answer:** implementer is the main one to write tests for its changes. It should also be responsible to make all the tests pass before it files for change review. Tester is more like inspecting the changed tests to ensure the tests are thorough enough for the requirements.
- in the case the a new test need to be added, tester should add instead of kicking the ball back to the implementer to do that. tester should only kick the ball back to implementer via task coordinator if the implementation is incorrect. WIth that being said, the task-coordinator should store the sessions of implementer, tester and reviewer to ensure the loop can run without repopulating context to the subagents. 

**D3 — Designer scope.** _(§1)_ ✅ RESOLVED
Should one `designer` own both the design doc and the plan?
- **Resolved:** one agent, two modes (`design`, `plan`), each with a
  `revision` variant; mode is explicit in every dispatch so a plan is
  never generated from an unapproved design. The designer is a **senior
  technical role** responsible for both, and holds **office hours** (D6).
- **Answer:** designer is for both, it's a snr technical role who is respoinsible for design and plan.

**D4 — Researcher fan-out + KB entry shape.** _(§2)_ ✅ RESOLVED
"Any agent may dispatch researcher" risks duplicate concurrent research.
How do we dedupe, and what does a KB line look like?
- **Resolved:** append-with-dedupe — researcher checks the KB first; a
  dispatch that yields no new line means the answer was already known.
  Entry shape (one bullet per fact):
  `- [<date> · <agent>] <fact> — <file:line or URL>`. Back this with
  **skills** for dedupe, race-safe append, and fast search.
- **Answer:** can do that, we can help researcher with skills if needed for append with dedupe, append under race competition and fast search

**D5 — Do we need a cross-session memory layer at all?** _(raised in §2)_
v2 reframes reflection as an **offline developer signal** (not fed back to
the agent at runtime), which removes the original reason for a
cross-session `memory_*` layer. Knowledge now lives in two per-feature
artefacts: the shared `knowledge.md` (durable facts about this feature's
area) and the per-task ledgers (implementer / tester / reviewer notes).
- **Resolved (v2):** **drop the cross-session memory layer.** Context is
  per-feature only —
  - `knowledge.md` = durable facts about *this* feature's code/area.
  - per-task ledgers = what implementer/tester/reviewer did, reused inside
    the task loop and read by the reflector at wrap-up.
  - the reflector consumes the ledgers + KB to produce the **developer**
    retrospective; nothing is promoted into a runtime memory store.
- **Answer:** I don't think we still need the memory layer under the new
  design. For each task the implementer / tester / reviewer notes are
  shared (the ledgers), and the reflector leverages those logs. No
  separate cross-session memory needed.
- **Open:** if a *future* feature wants context from a *past* one, the
  only carrier left is a human pointing the researcher at the old
  `.features/<old-slug>/knowledge.md`. Decide later whether that's enough
  or whether we revisit a lightweight cross-feature index.

**D6 — Adaptive retry location, return shape, office hours, session reuse.** _(§3)_ ✅ RESOLVED
The retry loop moves inside the task-coordinator. How does the
orchestrator still decide PLAN_WRONG-vs-Blocked, and how do we avoid
re-populating context on every retry?
- **Resolved:**
  - The **task-coordinator owns the inner loop** and returns a trail to
    the orchestrator on failure:
    `{ verdict, impl_bounces, review_bounces, last_failure_mode, evidence }`.
  - **Designer office hours:** when the task-coordinator suspects the
    plan/design is wrong, it dispatches the designer with a question (+
    ledger). The designer answers read-only (no status writes); if the
    answer implies a change, the task-coordinator returns `PLAN_WRONG` and
    the orchestrator brings the designer in to revise.
  - **Session reuse:** the task-coordinator keeps a list mapping
    `{task-id → subagent session handles}` so retries re-enter the same
    implementer/tester/reviewer session; the ledger is the durable
    fallback.
- **Answer:** task coordinator advise the orchestrator if task fails. if plan is wrong, the task coordinator should advise orchestrator who will include designer in the conversation. Let's make a office-hour for designer so that designer agent can answer questions for task coordinator. This also involes in subagnet session preservation. I think we probably need to have a list to ensure we can reuse the previous session as much as possible. 

**D7 — Gate model: one gate or two?** _(§3)_ ✅ RESOLVED
Design gate, plan gate, both, or a fast-path?
- **Resolved: design gate only.** If the design is detailed enough, the
  plan is a mechanical projection and needs **no** separate approval. The
  orchestrator still shows the plan to the user as an FYI but does not
  block on it. A wrong design re-runs the design gate.
- **Answer:** how about we only need the approval for design if the design is detailed enough. I don't think the plan matters that much if design can make it correct the first place,

**D8 — Bounce semantics + retry budget.** _(§4)_ ✅ RESOLVED
What happens when the tester is unhappy, and how many retries?
- **Resolved:** the tester **bounces to the implementer** (via the
  task-coordinator) when the implementation is wrong — it does not own a
  pass/fail of its own. **Two independent budgets, 5 each:**
  `impl_bounces` (tester found the implementation wrong) and
  `review_bounces` (reviewer FAIL). Either hitting 5 escalates the task.
- **Answer:** tester should kick back to the implementer. I think we cna increase the retry budget to give tester 5 and reviewer 5.

### B. Metrics to collect (deferred — no data yet)

> We have **no usage data yet**, so the strategic questions (success
> metric, highest-leverage lever, approval-load calibration) can't be
> answered from evidence. Rather than guess, we **instrument now and
> decide later**: at wrap-up the reflector appends one row to a
> per-feature scorecard. After ~10–20 features we revisit §6.B with real
> numbers.

**Feature scorecard** — reflector appends one row to
`.features/<slug>/scorecard.md` (or a shared `.features/scorecard.md`) at
every terminal state. Proposed fields (cheap to capture, all derivable
from the plan file + task ledgers):

| Field                     | Why it matters / which future question it feeds                 |
| ------------------------- | --------------------------------------------------------------- |
| `slug`, `date`            | identity                                                        |
| `terminal_status`         | Done / Blocked — base rate of clean completion                  |
| `phases`, `tasks`         | size proxy                                                      |
| `tasks_pass_first_try`    | % tasks PASS on attempt 1 (candidate success metric)            |
| `total_retries`           | implementer/tester/reviewer churn                              |
| `escalations`             | how often a task hit ESCALATE                                   |
| `plan_revisions`          | how often the design/plan was wrong (PLAN_WRONG count)          |
| `human_touchpoints`       | approvals + checkpoints + answered questions — approval load    |
| `researcher_dispatches`   | research depth actually used                                    |
| `kb_facts_added`          | how much was learned about this feature's area                  |
| `wall_to_done`            | rough elapsed time / turn count                                 |

Once a dozen rows exist, the deferred questions become answerable from
the table:

- **Success metric** — likely `tasks_pass_first_try` and the
  `Done`-without-`Blocked` rate.
- **Highest-leverage lever** — correlate `plan_revisions` /
  `total_retries` against which lever was weakest that session.
- **Approval-load calibration** — watch `human_touchpoints` vs. feature
  size to judge whether the design gate (D7) pays for itself.

**Research depth (already decided, not deferred).** Research must **deep
dive** — agents need to understand the area *correctly* to produce
correct results; a shallow KB defeats the purpose. Pruning ownership of
`knowledge.md` is still open (the human can edit it freely since it's
list-based; do we also want the reflector to compact it at wrap-up?).

### C. Validation gaps to confirm (audit, not design)

- [ ] **Honesty** — is the validation block enforced uniformly across
      implementer / tester / reviewer, or only described?
      we don't have validation block, but I just think the agent should be honest 
- [ ] **Rigor** — are banned phrases actually checked, or just listed?

- [ ] **Learning (offline)** — does the reflector's retrospective actually
      get read and turned into prompt / design / workflow fixes by us?
      (There is no runtime feedback loop and no KB→memory promotion in v2 —
      the only "learning" is the developer acting on the retrospective.)

### D. Where we think we are strong (keep)
- Orchestration state machine, dispatch wiring, adaptive retry.
- Review protocol with tiered AC and journey tests.
- Reflection at terminal states.

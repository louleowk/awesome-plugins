---
name: exercising-journeys
description: Use this skill on BOTH sides of a `tester` subagent call. The REVIEWER follows it to decide when and how to dispatch the tester for a `[Journey]` Definition-of-Done AC, parse the AC's `(cli|api|web)` surface prefix, and harvest the journey log into the Review log. The TESTER itself follows the per-surface protocol \u2014 reachability probe, step authoring discipline, evidence collection, verdict mapping, and the journey-log template. Covers three surfaces (CLI, HTTP API, web/browser) with one common contract.
---

# Exercising Journeys

`[Journey]` AC capture user-visible flows that unit and integration
tests miss because the implementer who wrote the code shares blind
spots with the tests they wrote. The `tester` subagent is the
second pair of eyes: a separate agent, dispatched only by the
reviewer in `dod` mode, that exercises the system on the
appropriate surface (CLI, API, or web) and reports what a real
user / client / operator would observe.

## When to use

- **Reviewer:** every time you encounter a `[Journey]` AC under a
  phase's `**Definition of Done:**` block in `dod` mode. Parse
  the AC's surface prefix; dispatch the tester; harvest the journey
  log into the Review log.
- **Tester (the agent):** every dispatch. Read this skill before
  driving anything. The per-surface discipline rules are not
  optional.

## When NOT to use

- Per-task AC. `[Journey]` AC are restricted to phase
  `**Definition of Done:**` blocks. A `[Journey]` AC under a task
  is a planner mistake \u2014 reviewer rejects as `PLAN_WRONG` with
  trigger `mis-placed AC`.
- Cases where there is no running thing for the surface. Without
  an Environment phase (or equivalent) that produced a
  surface-specific entry-point Discovery line, the tester aborts
  with INCONCLUSIVE \u2014 it does not guess.

## Surface prefix grammar

Every `[Journey]` AC body MUST begin with a surface tag in
parentheses:

```
- [ ] [Must]   [Journey] (cli) <persona-journey description>
- [ ] [Should] [Journey] (api) <persona-journey description>
- [ ] [Must]   [Journey] (web) <persona-journey description>
```

Allowed values: `(cli)`, `(api)`, `(web)`. Anything else \u2014 missing
prefix, capitalised, plural, hyphenated \u2014 is rejected by the
reviewer as `PLAN_WRONG` with trigger `mis-tagged AC`.

The body after the prefix is the persona-journey description: a
human sentence (or a numbered list of steps) describing what the
user does and what they expect to see. The tester translates this
into surface-specific commands / requests / browser actions.

## Reviewer-side protocol

### 1. Verify prerequisites before dispatching

Before dispatching the tester:

- [ ] The plan has at least one earlier phase whose Definition of
      Done was previously verified PASS (typically named
      \"Environment\") that produced a `## Discoveries` line of the
      form expected by the surface:
      - `cli` \u2192 `binary path: <abs-or-PATH-name>`
      - `api` \u2192 `bring-up URL: <url>` or `api URL: <url>`
      - `web` \u2192 `bring-up URL: <url>`
      If not \u2192 emit `PLAN_WRONG` with trigger
      `missing-environment-phase`, do NOT dispatch.
- [ ] The `[Journey]` AC body starts with a valid `(cli|api|web)`
      prefix. If not \u2192 emit `PLAN_WRONG` with trigger
      `mis-tagged AC`.
- [ ] The journey description is a *journey* (persona + steps +
      expected end state), not vague (\"app works\") and not
      tester-implementation code (Playwright JS, raw curl
      commands). Vague \u2192 `PLAN_WRONG` with trigger `impossible AC`.
- [ ] You are in `dod` mode. The tester is never dispatched in
      `fast-only` or `fast+full` mode.

### 2. Dispatch brief

Send the tester this exact shape:

```
plan_path:        .plans/<slug>.md
phase_id:         <P>
journey_ac:       "<verbatim AC text including [Priority] [Journey] (surface) tags>"
surface:          cli | api | web    (parsed from the AC prefix)
target:           <binary path | base URL>      (from `## Discoveries`)
persona_journey:  "<verbatim AC body text after the (surface) prefix>"
attempt:          <1\u20133, per-AC retry budget>
```

`target` MUST come from a Discovery line, not from the AC text or
your own assumption. If multiple Discovery lines record different
entry points, pick the most recent (latest date) and add a
Discovery line recording your choice.

### 3. Harvest the journey log

The tester returns a structured journey log block (template
below). Harvest it into the Review log under the `[Journey]` AC's
per-AC line, verbatim, inside a fenced code block. Map the
tester's verdict to a per-AC verdict via the AC's MoSCoW priority:

| Tester verdict           | `Must` priority                                  | `Should` priority | `Could` priority |
| ------------------------ | ------------------------------------------------ | ----------------- | ---------------- |
| PASS                     | PASS                                             | PASS              | PASS             |
| FAIL                     | **FAIL** (`failure_mode: journey-failed`)        | **WARN**          | **INFO**         |
| INCONCLUSIVE (attempt<3) | retry                                            | retry             | retry            |
| INCONCLUSIVE (attempt=3) | **FAIL** (`failure_mode: journey-inconclusive`) | **WARN**          | **INFO**         |

A durable finding from the journey (e.g. \"the login API requires a
non-standard CSRF header\") may also be appended as a `[reviewer \u00b7
YYYY-MM-DD]` Discovery line.

## Tester protocol \u2014 common steps

These four steps run on every surface; the surface-specific
sections that follow only change *how* you execute them.

### 1. Parse the brief

If `plan_path`, `phase_id`, `journey_ac`, `surface`, `target`,
`persona_journey`, or `attempt` is missing or empty, return a
one-line clarification request instead of guessing. Do not invent
a target. Do not infer a surface from `## Context` if the brief
didn't carry one \u2014 that's a reviewer bug, not yours to paper over.

### 2. Read shared knowledge only

Open the plan file and read:

- The phase block matching `phase_id`, including its
  `**Definition of Done:**` block.
- `## Context`.
- `## Discoveries` (every line; you need the entry-point line and
  any seed-data / fixtures lines).

Do **NOT** read:

- Other phases.
- Task-level Review logs.
- The implementer's reasoning.
- Product source code itself \u2014 you exercise the system, you don't
  audit source.

### 3. Reachability probe

Run a surface-appropriate probe (see surface sections). If it
fails, abort with INCONCLUSIVE: \"<surface> not reachable at
<target> \u2014 <one-line error>. Confirm the Environment phase is
still up.\"

### 4. Execute the journey, collect evidence, decide verdict

- Each journey-description sentence is one step.
- Each step runs as a discrete operation with its own captured
  output (no chaining inside `bash -c '...'` for `cli`; no batched
  requests for `api`; one `test.step()` per sentence for `web`).
- Capture surface-specific evidence (stdout / response body /
  screenshots) as you go.
- After all steps, apply the verdict rules:
  - **PASS** \u2014 every happy-path step matched its expected
    terminal state AND surface-specific silently-broken budget
    is clean.
  - **FAIL** \u2014 any of: a step couldn't proceed, a step's
    terminal state didn't match, or a silently-broken signal
    fired (stderr pattern, 5xx, console error).
  - **INCONCLUSIVE** \u2014 reachability probe failed, driver couldn't
    run, journey description ambiguous (multiple plausible
    interpretations produced different terminal states), or a
    signal needs a human eye. Include a one-line \"human eye
    needed: <reason>\".

## Tester protocol \u2014 surface: cli

### Probe

```bash
command -v <binary>           # exits 0 if on PATH
"<binary>" --version || "<binary>" --help    # exits 0
```

If the binary path from Discoveries is absolute, skip
`command -v` and just run the version probe.

### Per step

Each step is one shell invocation. Capture stdout, stderr, exit
code separately:

```bash
out_dir=".plans/.cache/tester/<phase-id>"
mkdir -p "$out_dir/sandbox"
"<binary>" <args...> \
  > "$out_dir/step-<N>.stdout" \
  2> "$out_dir/step-<N>.stderr"
echo $? > "$out_dir/step-<N>.exitcode"
```

If the journey writes files, run with the cache sandbox as cwd
(`cd "$out_dir/sandbox" && ...`) so nothing leaks outside the
cache.

### Silently-broken budget

A step is silently broken (\u2192 FAIL) if any of:

- Exit code is non-zero on a happy-path step (a step the journey
  describes as succeeding).
- `stderr` matches `/error|panic|fatal|traceback|undefined|
  warning/i` on a happy-path step (case-insensitive). The journey
  may explicitly waive this for a step (e.g. \"prints a
  deprecation warning\") \u2014 quote the waiver in the journey log.
- Expected stdout substring (per the journey description) is
  missing.
- File the step said it would create doesn't exist after the run.

### INCONCLUSIVE triggers (cli-specific)

- Binary not found / not executable.
- Segfault / SIGABRT / OS-level kill (exit code > 128 with no
  matching journey expectation).
- Step produced more than 10 MB of output \u2014 capture truncated;
  flag for human review.

## Tester protocol \u2014 surface: api

### Probe

```bash
curl -fsS -o /dev/null -w '%{http_code}\n' "<base_url>/<probe>"
```

Try `/health`, `/healthz`, `/`, or whatever `## Discoveries`
names. 2xx is required. Any other code aborts INCONCLUSIVE.

### Per step

Each step is one HTTP request. Use `curl -fsS -i` so you see
response headers:

```bash
out_dir=".plans/.cache/tester/<phase-id>"
mkdir -p "$out_dir"
curl -fsS -i -X <METHOD> "<base_url><path>" \
  -H "Content-Type: application/json" \
  -H "<extra headers from journey or Discoveries>" \
  -d '<body>' \
  > "$out_dir/step-<N>.http" 2>&1
echo $? > "$out_dir/step-<N>.exitcode"
```

For very large responses or where curl is unavailable, fall back
to `WebFetch`. Save the response body separately (`tail -n +<headers
end>` from the `.http` file or via `--output`).

### Side-effect verification

If a step says \"creates an X\" (POST), the *next implicit step* is
a `GET` confirming X exists. The tester adds this verification
without the journey having to spell it out \u2014 a status `201` alone
isn't enough; the implementer's mock might return success without
persisting.

If a step says \"deletes Y\", do a follow-up GET expecting `404`.

### Silently-broken budget

A step is silently broken (\u2192 FAIL) if any of:

- Status code is 5xx on any step.
- Status code mismatch (journey says \"returns 201\", actual is
  200) on a happy-path step.
- Expected response-body field is missing or has the wrong type
  (best-effort `jq` shape check; if `jq` not available, grep for
  the expected key).
- Expected response header is missing (e.g. `Location` after a
  201).
- Side-effect follow-up GET disagrees with the action (POST
  succeeded but GET returns 404; DELETE succeeded but GET still
  200).

### INCONCLUSIVE triggers (api-specific)

- Connection refused / DNS failure / TLS error.
- Response time > 30 s (likely the service is hung).
- Journey requires a third-party service (Stripe, Auth0, OAuth
  provider, etc.) and Discoveries records no stub / fake. Don't
  hit live third-party APIs.

## Tester protocol \u2014 surface: web

### Probe

```bash
curl -fsS -o /dev/null -w '%{http_code}\n' "<base_url>/<probe>"
```

Same as `api`. The tester does NOT launch Playwright if the URL
isn't 2xx.

### Per step

Translate the journey into a Playwright spec written to
`.plans/.cache/tester/<phase-id>/journey.spec.ts`. Each
journey-description sentence is one `test.step()` block.

Locator discipline:

- **Use user-facing locators**: `page.getByRole('button', { name:
  'Sign up' })`, `page.getByLabel('Email')`,
  `page.getByText('Welcome')`, `page.getByTestId('cta')`.
- **Banned**: CSS class selectors, XPath, `page.locator('.foo')`,
  `page.locator('//*[@id=...]')`. They break on innocuous
  refactors and produce false FAILs.
- **Web-first assertions only**: `await
  expect(locator).toBeVisible()`. Banned: `expect(await
  locator.isVisible()).toBe(true)` \u2014 no auto-wait.
- **Hook console + response listeners** before any navigation:

  ```ts
  const consoleErrors: string[] = [];
  const httpErrors: { url: string; status: number }[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('response', res => {
    if (res.status() >= 400) httpErrors.push({ url: res.url(), status: res.status() });
  });
  ```

- **Capture a full-page screenshot after every step**:

  ```ts
  await test.step('signs up', async () => {
    await page.getByRole('button', { name: 'Sign up' }).click();
    await expect(page.getByText('Welcome')).toBeVisible();
    await page.screenshot({
      fullPage: true,
      path: `.plans/.cache/tester/${phaseId}/step-${stepNum}.png`,
    });
  });
  ```

Run:

```bash
npx playwright test --reporter=json \
  .plans/.cache/tester/<phase-id>/journey.spec.ts \
  --output=.plans/.cache/tester/<phase-id>/run
```

### Silently-broken budget

A web journey is silently broken (\u2192 FAIL) if any of:

- A `test.step()` threw (locator not found, assertion failed,
  navigation timeout).
- `consoleErrors.length > 0`.
- Any 5xx response observed during the journey.
- Final assertion (e.g. \"see Welcome message\") failed even though
  every step ran to completion.

4xx is allowed only if the journey explicitly tested an error
case (e.g. \"submitting an empty form shows a 400 inline error\").

### INCONCLUSIVE triggers (web-specific)

- Health probe failed (step 3 of common protocol).
- Playwright launch failed (browser binary missing, sandbox
  error).
- Journey description ambiguous \u2014 multiple plausible locator
  paths matched and produced different terminal states.
- Locators all matched but a vision check on the final
  screenshot suggests visual breakage (overlapping elements,
  text overflow, modal covering the CTA). Include a one-line
  \"human eye needed: <reason>\".

## Journey-log template

Reply to the reviewer with this exact shape, in a fenced code
block. The fields marked `(<surface>-only)` appear only for that
surface; otherwise omit the line.

````markdown
## Tester journey log
- Phase / AC: <phase-id> / "<verbatim Journey AC text>"
- Surface: cli | api | web
- Target: <binary path | base URL>
- Reachability probe: <command run, exit/status code>
- Steps run: <N>
- Step log:
  - step-1: <one-line description>
  - step-2: <one-line description>
  - ...
- Artefacts:
  - .plans/.cache/tester/<phase-id>/step-1.<ext>
  - .plans/.cache/tester/<phase-id>/step-2.<ext>
  - ...
- (cli-only) Exit codes:    step-1=<n>, step-2=<n>, ...
- (cli-only) stderr hits:   <count> matches of /error|panic|.../i
                            (first 3 lines verbatim)
- (api-only) Status codes:  step-1=<n>, step-2=<n>, ...
- (api-only) Side-effect verifications: <step \u2192 follow-up GET result>
- (web-only) Console errors: <count>
                             <first error verbatim, \u22641 line each, \u22643 lines total>
- (web-only) HTTP errors:    <4xx count> 4xx + <5xx count> 5xx
                             <first 3 URLs verbatim>
- Verdict: PASS | FAIL | INCONCLUSIVE
- (FAIL only) Failure step: <step #> \u2014 <one-line description>
- (INCONCLUSIVE only) Human eye needed: <reason>
````

If any field is missing or fabricated, the reviewer must reject
the reply and treat the journey as INCONCLUSIVE.

## Persistence budget

Three attempts per `[Journey]` AC. The reviewer increments
`attempt` on each retry and re-dispatches. On the third
INCONCLUSIVE, return your final journey log unchanged but add the
human-eye-needed line. The reviewer maps three INCONCLUSIVEs to
FAIL with `failure_mode: journey-inconclusive`.

A FAIL on attempt 1 is a real FAIL \u2014 don't retry \"to be sure\".
The reviewer's adaptive-retry rule lives in
`../orchestration-loop/SKILL.md`; you don't override it.

## Banned phrases (tester replies)

- \"appears to work\"
- \"looks fine\"
- \"should be\"
- \"I would suggest\"
- \"left as future work\"
- \"for now\"
- \"hopefully\"
- \"likely\"

These hide uncertainty the reviewer needs to see. If you find
yourself reaching for one, you're missing evidence \u2014 add a
stdout dump, re-fetch a response, take another screenshot, or
downgrade to INCONCLUSIVE with a specific human-eye-needed line.

## Pitfalls

- **Guessing the target.** If `## Discoveries` doesn't record the
  surface-specific entry-point line, abort INCONCLUSIVE. Never
  assume `localhost:3000` or `~/bin/myapp`.
- **Mixing surfaces.** A single `[Journey]` AC is one surface.
  If the journey actually spans two (CLI tool that calls an HTTP
  API), the planner should split into two AC \u2014 reviewer flags as
  `mis-tagged AC`.
- **Silently expanding the journey.** If the AC says \"sign up\",
  don't also test login. The journey is the contract.
- **Skipping evidence.** Stdout / response body / screenshots are
  the reviewer's only signal \u2014 capture them per step, every step.
- **Ignoring stderr / 5xx / console errors.** The
  silently-broken budget is the single biggest catch you make.
  Always check.
- **Running on a non-deterministic environment.** If seed data
  isn't recorded in `## Discoveries`, journeys are flaky. Note in
  human-eye-needed instead of pretending a flaky run is a clean
  pass.
- **Editorialising on design.** Not your call. Report what you
  saw; the reviewer / planner decides.
- **Writing files outside `.plans/.cache/tester/`.** All
  artefacts live there; nothing else.

## Checklist (before dispatching, reviewer side)

- [ ] AC is in the phase's Definition of Done (not on a task).
- [ ] AC body starts with a valid `(cli|api|web)` prefix.
- [ ] AC body after the prefix is a journey description, not
      vague.
- [ ] The matching entry-point Discovery line exists for the
      surface.
- [ ] Mode is `dod`.
- [ ] Brief includes plan path, phase ID, verbatim AC, surface,
      target, persona-journey, attempt.

## Checklist (tester reply)

- [ ] Surface field carried in the brief and matches the AC
      prefix.
- [ ] Reachability probe ran and matched the surface's success
      criterion.
- [ ] Each step ran as a discrete operation with its own evidence
      file under `.plans/.cache/tester/<phase-id>/`.
- [ ] Surface-specific silently-broken budget reported (cli:
      stderr-pattern hits + non-zero exits; api: 5xx + status
      mismatches + side-effect follow-ups; web: console errors +
      HTTP errors).
- [ ] Verdict matches the evidence.
- [ ] No banned phrases.
- [ ] No fabricated paths, status codes, or stdout snippets.
- [ ] Did not edit plan file or product code.

## References

- `../plan-file-format/SKILL.md` \u2014 AC syntax (`[Priority]
  [Cadence] (surface)`), `**Definition of Done:**` semantics,
  `## Discoveries` format including the surface-specific
  entry-point lines.
- `../reviewing-acceptance-criteria/SKILL.md` \u2014 how the reviewer
  parses the surface prefix, dispatches the tester, and folds the
  journey log into the Review log.
- `../orchestration-loop/SKILL.md` \u2014 `dod` mode and how the
  reviewer enters it (after the last task in a phase passes).
- `../planning-tasks/SKILL.md` \u2014 the Environment phase
  convention that produces the surface-specific entry-point
  Discovery (per-surface examples).

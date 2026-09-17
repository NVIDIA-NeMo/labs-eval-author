---
name: eval-author-task-create
description: >-
  Propose dataset improvements from Eval Author audit findings, then optionally
  create or strengthen a Harbor eval for a tool gap, capability, failure case,
  or observed regression. Check task correctness, run the real agent when
  authorized, and report performance and coverage separately. Use when the user
  asks to suggest dataset changes, fill an eval gap, turn audit uncovered_items into a
  Harbor task, or add missing tool coverage. Writes proposals, drafts, and
  measurements only under `.eval-author/`.
triggers:
  - create a Harbor task from an audit gap
  - fill an uncovered eval tool
  - generate missing eval tasks
  - close audit coverage gaps
  - turn uncovered_items into Harbor tasks
  - propose dataset improvements from audit findings
not-for:
  - eval-author-first-eval (use when the user has no evaluations yet)
  - eval-author (use for the shared standard and routing)
  - eval-author-audit (use to create the denominator and coverage report)
  - eval-author-discover (use to prove an existing suite is runnable)
  - nemo-evaluator (use to run an existing benchmark without authoring tasks)
compatibility: >-
  Proposals read local audit artifacts and task evidence without running Harbor.
  Task creation needs Python 3.11 or later and a Harbor CLI compatible with `harbor task init`.
  Docker is required for Oracle and Docker-backed real-agent runs. Real-agent
  runs may require provider credentials and explicit user approval.
maturity: alpha
license: Apache-2.0
user-invocable: true
allowed-tools: [Bash, Read, Write, Grep, Glob]
---
<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eval Author: create task

Read `eval-author` for the shared evidence standard and boundaries. Read
`eval-author-audit` for measurement and aggregation. Start with the proposal step
to turn audit evidence into prioritized dataset improvements across tools,
capabilities, and failure cases. For proposal-only requests, stop after Step 1.
For authorized continuation, choose a recommendation from Step 1 and implement
one new scenario or improvement to an existing eval at a time. Tool gaps use the
script below; non-tool recommendations use Harbor directly as described in
Steps 2–4. Keep drafts under `.eval-author/` and preserve original tasks and
customer source. Reuse authorization already given; model spend and source
changes still require their applicable authorization.

An existing suite without a coverage report belongs in `eval-author-discover`
and `eval-author-audit`. A missing report alone is not a first-eval request.

## Script

`scripts/task_pipeline.py` has three deterministic commands for tool gaps only.
Their eligibility rules do not limit the broader skill workflow:

| Command | Verdict |
|---|---|
| `select` | Lists only tool items with `reason: not_covered_by_any_input_report` and emits a deterministic `task_slug` plus artifact paths |
| `scaffold` | Calls Harbor's own `harbor task init`, requires matching draft/proposal names for that slug, and installs the supplied instruction |
| `verify` | Exits 0 only when the selected tool was uncovered before and covered in two distinct repeated after-reports with distinct ATIF `subject.run_id` values |

The script prints one JSON object. Exit code 0 is success; do not replace its
verdict with model judgment.

## Step 1: propose dataset improvements

Read the aggregate audit report, relevant per-trace `details.json` and capability
judgments, and the source traces or verifier results needed to explain the
findings. Check existing task instructions, fixtures, and verifiers before
claiming a scenario is absent or proposing a duplicate. A capability covered in
one run can still fail in another; review observed failures even when the item
is absent from `uncovered_items`.

Distinguish the basis for each recommendation:

| Basis | What it supports |
|---|---|
| Observed failure | A trace or verifier shows incorrect behavior on an exercised scenario. Preserve the existing failing task as a regression; propose strengthening it only when a specific fixture or verifier change adds value. An agent fix may be the next action without any dataset change. |
| Coverage gap in inspected inputs | A measured item is not demonstrated and the inspected tasks or traces lack the intended scenario. Propose a concrete new task or extension; state the inspected scope rather than claiming the entire dataset lacks coverage. |
| Unmeasured or insufficient evidence | The method was not selected or is unsupported, judgments are missing or unclear, or the scenario's trigger is unverified. Recommend measurement or inspection first. Ethos-backed scenarios may still be proposed as candidates, with their unmeasured status explicit. |

`not_covered_by_any_input_report` alone does not distinguish an absent scenario,
an agent failure, or missing judgments. `not_measured_by_any_method` is a
measurement limitation, not proof of a dataset deficiency. Preserve measured
`failure_cases` results from the audit; manual observations do not substitute
for measurement. Inspect the rationale and trace before treating a missing
judgment as incorrect behavior.

Write recommendations to `.eval-author/proposals/dataset-recommendations.md` as
skill-authored analysis; keep the generated coverage JSON unchanged. Rank by
expected value and strength of evidence, explaining why the first action comes
first. Prefer a short, useful list over one suggestion per uncovered item.
For each recommendation, include:

- **Change and scenario:** add a task, strengthen a named existing task, retain
  an existing regression, or gather evidence; describe the concrete request and
  fixture or failure trigger that makes it useful.
- **Expected behavior and verification:** the outcome to check and how a verifier
  would distinguish correct from incorrect behavior. For failure cases, identify
  evidence that the trigger actually occurred as well as the expected response.
- **Basis and evidence:** the category above, stable audit item names, and task,
  run, trace-step, judgment, or verifier references supporting the recommendation.
  Mark proposed fixture details as proposals, not observed facts.
- **Next action:** name the implementation route (tool-gap script or direct
  Harbor authoring), or the missing evidence, design, or intended behavior that
  must be resolved first. A written recommendation is not a generated, validated,
  or accepted Harbor task.

Lead the proposal response with the highest-value recommendations and enough
scenario and expected-behavior detail to act on them. Follow with supporting
coverage counts, measurement limits, and links to the proposals and audit report.
Full tool coverage or an unsupported task-generation path must not suppress
useful capability or failure-case suggestions. Do not relabel those suggestions
as tool gaps to pass the selector. If evidence supports no dataset change, say why
and identify any useful measurement or agent-fix action instead of inventing
additions. Do not scaffold or run tasks for a proposal-only request.

## Step 2: choose the implementation route

For authorized continuation, choose the highest-value recommendation with a
concrete scenario and an Ethos-backed outcome that can be verified. An unresolved
recommendation does not prevent independent supported work. The Markdown
recommendations from Step 1 are the handoff; no additional manifest is required.

For an uncovered tool, use the existing selector:

```bash
uv run <skill_dir>/scripts/task_pipeline.py select \
  --report .eval-author/audit-coverage-report.json
```

Choose from `actionable_tools` and use its `task_slug` and `paths` verbatim.
An empty list means only that there are no eligible tool gaps.

For a capability, failure case, or observed regression, proceed directly to task
design. Choose an unused descriptive slug and record the target audit item,
evidence, and intended change in the draft README. Use
`.eval-author/proposals/<task-slug>-instruction.md`,
`.eval-author/task-drafts/<task-slug>`, and
`.eval-author/task-measurements/<task-slug>/` for its artifacts. Do not relabel the
finding as a tool gap or pass it through the tool-only selector.

## Step 3: design the smallest objective task

Read the recommendation and the selected audit item's requirements. Read one
nearby task for domain conventions only. Do not copy its directory: a sibling can carry an obsolete Harbor schema, placeholder
verifier, or unrelated solution.

Write the instruction to the proposal path from Step 2. State the observable
goal, paths, and constraints without naming the target tool or leaking verifier
logic. The task should exercise the selected outcome; require a tool only when
that outcome naturally needs it.

Decide the verifier before scaffolding. Prefer deterministic shell or pytest.
The verifier must grade the task outcome, not the tool call; ATIF measurement
proves coverage separately.

When a scenario already exposes the problem, strengthen it in a separate draft
instead of adding a duplicate. Port the relevant fixtures and grading logic into
a fresh Harbor skeleton, preserve existing metrics, and document changes from
the original. For example, retain offsite feasibility grading and add checks that
the explanation agrees with accepted reservation times and prices.

For failure cases, design a check for the specific trigger before grading the
response. An unknown-route error is not a rejected reservation; recovery needs
an actual rejection followed by repair, with state evidence where required.
Proposed triggers are not observed coverage. Defer source/adapter integration
outside the authorized draft scope. If Ethos leaves successful infeasibility
handling undefined, retain that open question rather than inventing a score.

## Step 4: scaffold with Harbor

For a selected tool gap:

```bash
uv run <skill_dir>/scripts/task_pipeline.py scaffold \
  --report .eval-author/audit-coverage-report.json \
  --target <tool-name> \
  --out .eval-author/task-drafts/<task-slug> \
  --task-name <org>/<task-slug> \
  --description "<one-line description>" \
  --author "<author>" \
  --instruction-file .eval-author/proposals/<task-slug>-instruction.md
```

Use the Step 2 `task_slug` for `<task-slug>` in every path above. `scaffold`
rejects mismatched draft, task-name, or proposal filenames.

For non-tool recommendations, check that the chosen draft path does not already
exist, then call Harbor's scaffolder directly:

```bash
harbor task init <org>/<task-slug> \
  --tasks-dir .eval-author/task-drafts \
  --description "<one-line description>" --author "<author>"
```

Install the Step 3 instruction as the new draft's `instruction.md`. Neither route
may overwrite an existing task. A revision stays separate until adoption into the
suite is explicitly in scope.

Then complete Harbor's generated files:

- `environment/Dockerfile`: task prerequisites, never the solution.
- `tests/test.sh`: deterministic reward writer using absolute paths.
- `solution/solve.sh`: executable Oracle solution.
- `task.toml`: nonempty keywords, metadata, realistic timeouts and resources.
- `README.md`: purpose, environment, verifier, layout, and run commands.

Do not leave generated placeholders, `pass`, unconditional reward 1, or empty
keywords.

## Step 5: prove task correctness with Oracle

Run Harbor's Oracle before spending model credentials:

```bash
harbor run -p .eval-author/task-drafts/<task-slug> -a oracle
```

Check Oracle reward 1.0 without exceptions and NOP failure. For a changed grader,
check that the observed wrong outcome fails and valid alternatives pass. Fix the
task, solution, or verifier when Oracle fails; do not weaken the verifier merely to
make it pass.

## Step 6: run the real agent twice

Running a model spends credentials. Do it only when the user asked for the run
or approved it. Use the repository's proven agent configuration, point it at the
draft, and set `n_attempts: 2`. Keep the resulting job under `.eval-author/`.

Record both trials' rewards and exceptions. A correct eval can expose an agent
failure; keep that regression without weakening grading or retrying until the
agent passes. Coverage measurement requires valid ATIF for each trial.

`SUPPORTS_ATIF = true` is not evidence that the emitted JSON matches Harbor's
current schema. A `measure.py` parse failure is an agent-adapter defect, not a
coverage result.

## Step 7: measure and aggregate each trial

Run `eval-author-audit`'s `measure.py` and `report.py` separately for each
trial. Keep repeat outputs separate so one successful run cannot hide another:

```bash
uv run --with-requirements <audit_skill_dir>/requirements.txt \
  <audit_skill_dir>/scripts/audit_spec/measure.py \
  --audit .eval-author/audit.md \
  --trial-dir <job-dir>/<trial-1> \
  --task-id <task-slug> \
  --run-id repeat-1 \
  --out-dir .eval-author/task-measurements/<task-slug>/repeat-1

uv run --with-requirements <audit_skill_dir>/requirements.txt \
  <audit_skill_dir>/scripts/audit_spec/report.py \
  --audit .eval-author/audit.md \
  --coverage-dir .eval-author/task-measurements/<task-slug>/repeat-1 \
  --out .eval-author/task-measurements/<task-slug>/repeat-1-report.json
```

The example defaults to tool measurement. For a capability, add
`--measure capabilities --capability-judgments <trace-bound-sidecar>`; for a
failure case, use
`--measure failure_cases --failure-case-judgments <trace-bound-sidecar>`.
Follow the audit skill's evidence and digest checks. Tool presence alone cannot
prove the outcome or trigger. Repeat for trial 2 with its own judgments.

## Step 8: report correctness, performance, and coverage

For the tool-gap route, use the existing closure check:

```bash
uv run <skill_dir>/scripts/task_pipeline.py verify \
  --before .eval-author/audit-coverage-report.json \
  --after .eval-author/task-measurements/<task-slug>/repeat-1-report.json \
  --after .eval-author/task-measurements/<task-slug>/repeat-2-report.json \
  --target <tool-name>
```

The tool-only `accepted` result establishes repeated tool coverage, not task
quality. For non-tool recommendations, inspect each trial's report from Step 7
for the selected capability or failure case; do not use the tool-only `verify`
command. Claim repeated coverage only if both trials satisfy the item's actual
requirements, including any trigger. A prior aggregate-covered status does not
erase an observed failing run.

Report task correctness (Oracle/NOP and relevant grader controls), agent
performance (both rewards and exceptions, or not run), and coverage (each trial's
measurement, or unmeasured) separately. Keep useful regressions even when the
agent fails and coverage remains open. Missing trigger evidence and undefined
intended behavior remain explicit next actions.

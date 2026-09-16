---
name: eval-author-task-create
description: >-
  Propose dataset improvements from Eval Author audit findings, then optionally
  create or strengthen a Harbor eval for a tool, capability, failure case, or
  observed regression. Check task correctness with controls, measure agent
  performance when authorized, and report repeated coverage separately. Use when the user asks to
  suggest dataset changes, fill an eval gap, turn audit uncovered_items into a
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
capabilities, and failure cases. For proposal-only requests, complete Steps 1–2 and stop.
For authorized continuation, select a supported proposal and proceed:

```text
reviewed finding (including failures on aggregate-covered items)
  → new scenario or separate revision of an existing eval
  → Oracle/NOP and discriminating verifier controls
  → authorized real-agent runs
  → task correctness, agent performance, and coverage reported separately
```

Implement one proposal at a time. Keep generated artifacts under `.eval-author/`.
Preserve existing tasks and customer source. Reuse authorization already present
in the conversation; an explicit request to continue without intermediate
confirmations does not require another stage check-in. Model spend and source
changes still require their own applicable authorization.

An existing suite without a coverage report belongs in `eval-author-discover`
and `eval-author-audit`. A missing report alone is not a first-eval request.

## Script

`scripts/task_pipeline.py` prints deterministic JSON; nonzero exits indicate
invalid inputs or an unmet verification condition.

| Command | Result |
|---|---|
| `propose` | Validates skill-authored findings against audit targets; emits proposals with evidence, basis, action, and explicit readiness blockers |
| `select --proposals ...` | Routes all proposal kinds; proposal-only scope reports recommendations without implementation |
| `scaffold --proposals ...` | Initializes a separate Harbor draft for an eligible proposal in implementation scope |
| `verify --proposals ...` | Checks the target's own measurement method in two distinct single-run reports; reports coverage only |
| `select`, `scaffold`, `verify` without `--proposals` | Backward-compatible tool-gap path; its empty selection says nothing about other proposals |

Read [Proposal records](references/proposals.md) when writing findings or using
these commands. The script checks structure and routing, not the truth of
skill-authored evidence judgments or conversation authorization.

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
`failure_cases` results and trigger judgments from the audit. Manual observations
do not substitute for measurement, and a missing judgment is not an agent failure.

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
- **Next action:** name the implementation route (new scenario or separate
  revision), retention of an existing regression, evidence gathering, or behavior
  definition. Record a precise blocker when design or source integration is
  missing. A written recommendation is not a generated, validated, or accepted Harbor task.

Lead the proposal response with the highest-value recommendations and enough
scenario and expected-behavior detail to act on them. Follow with supporting
coverage counts, measurement limits, and links to the proposals and audit report.
Full tool coverage or an unsupported task-generation path must not suppress
useful capability or failure-case suggestions. Do not relabel those suggestions
as tool gaps to pass the selector. If evidence supports no dataset change, say why
and identify any useful measurement or agent-fix action instead of inventing
additions. Do not scaffold or run tasks for a proposal-only request.

## Step 2: record and select proposals

Write reviewed findings to `.eval-author/proposals/findings.json` using the
[proposal record contract](references/proposals.md). Findings must include
observed failures found during per-run review even when aggregate coverage is
complete. A `missing` judgment alone does not establish incorrect behavior:
inspect its rationale, scenario/trigger evidence, and trace before classifying it.

```bash
uv run <skill_dir>/scripts/task_pipeline.py propose \
  --report .eval-author/audit-coverage-report.json \
  --findings .eval-author/proposals/findings.json \
  > .eval-author/proposals/dataset-proposals.json
uv run <skill_dir>/scripts/task_pipeline.py select \
  --report .eval-author/audit-coverage-report.json \
  --proposals .eval-author/proposals/dataset-proposals.json
```

The default scope is `proposal-only`: stop with the Markdown recommendations and
JSON proposals. For an authorized implementation request, add `--scope implement`
to `propose`; that flag records existing authorization, it does not grant it.
Choose an `actionable_proposals` entry in priority order. Deferred entries remain
useful proposals with explicit next actions; continue with independent eligible
entries. Full tool coverage cannot block this route. Use `id` as `--target` and
the generated `task_slug` and `paths` verbatim.

The older `select --report ...` tool-gap interface remains available for an
explicit tool-gap request. There `--target` is the tool name. Do not rename
non-tool findings to use it.

## Step 3: design the smallest objective task

Read the proposal's scenario, expected behavior, verifier design, evidence,
and audit item requirements (or the legacy tool gap's generation context). Read
one nearby task for domain conventions only. Do not copy its directory: a sibling can carry an obsolete Harbor schema, placeholder
verifier, or unrelated solution.

Write the instruction only to `paths.proposal` from Step 2. State the observable
goal, paths, and constraints without naming the target tool or leaking verifier
logic. The task should exercise the selected outcome. A capability or failure-case
verifier must check that outcome, not incidental tool presence.

Decide the verifier before scaffolding. Prefer deterministic shell or pytest.
The verifier must grade the task outcome, not the tool call; ATIF measurement
proves coverage separately using the target's method. For a failure case,
check that its specific trigger occurred before scoring the response. A proposed
trigger is a design, not observed coverage. For rejection recovery, an unknown
route error is not a rejected reservation; require an actual rejection plus
repair and, where required, reservation-state evidence.

Prefer `strengthen_existing` when a scenario already exposes the regression.
Initialize a fresh draft, port the relevant fixture and grading logic, and make
the proposed changes there. Record the original task path and changes in the
README; never overwrite the original. Preserve existing feasibility metrics and
add the missing communication check. An agent defect already caught by a sound
grader may need only `retain_regression`, with an agent-fix recommendation.
Source/adapter changes beyond draft authoring remain a separate scoped action.
Never infer a positive success policy for infeasible requests from a prohibition
on false confirmations; leave `expected_behavior` null and use `define_behavior`
until the scoring contract is established.

## Step 4: scaffold with Harbor

```bash
uv run <skill_dir>/scripts/task_pipeline.py scaffold \
  --report .eval-author/audit-coverage-report.json \
  --proposals .eval-author/proposals/dataset-proposals.json \
  --target <proposal-id> \
  --out .eval-author/task-drafts/<task-slug> \
  --task-name <org>/<task-slug> \
  --description "<one-line description>" \
  --author "<author>" \
  --instruction-file .eval-author/proposals/<task-slug>-instruction.md
```

Use the Step 2 `task_slug` for `<task-slug>` in every path above. `scaffold`
rejects mismatched draft, task-name, or proposal filenames.

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

Check Oracle reward 1.0 without exceptions and NOP failure. Add targeted controls
showing that the new grader rejects the observed wrong outcome and accepts valid
alternatives (for example 15:00 and 3:00 PM). Oracle alone cannot prove grading
quality. Fix the task, solution, or verifier when Oracle fails; do not weaken the verifier merely to
make it pass.

## Step 6: run the real agent twice

Running a model spends credentials. Do it only when the user asked for the run
or approved it. Use the repository's proven agent configuration, point it at the
draft, and set `n_attempts: 2`. Keep the resulting job under `.eval-author/`.

Record exceptions and actual verifier rewards for both trials. Require valid
ATIF for coverage measurement. A valid new regression can expose an agent failure;
retain that useful eval and report its failing score. Do not weaken grading or
rerun until the model happens to pass. Separate task defects from agent defects.

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

The example above defaults to tool measurement. For capabilities use
`--measure capabilities --capability-judgments <trace-bound-sidecar>`; for failure
cases use `--measure failure_cases --failure-case-judgments <trace-bound-sidecar>`.
Follow the audit skill's evidence and digest checks. Trigger, actual outcome, and
prohibited behavior evidence cannot be replaced by tool presence. Repeat for
trial 2, with its own judgments. Use the selected draft's `task_slug` as task ID.
Keep all methods from a single trial together; never union separate trials to
hide a failure.

## Step 8: report three separate results

```bash
uv run <skill_dir>/scripts/task_pipeline.py verify \
  --before .eval-author/audit-coverage-report.json \
  --after .eval-author/task-measurements/<task-slug>/repeat-1-report.json \
  --after .eval-author/task-measurements/<task-slug>/repeat-2-report.json \
  --proposals .eval-author/proposals/dataset-proposals.json \
  --target <proposal-id>
```

For proposals, `coverage_closed` reports repeated evidence of the selected item,
including a regression whose aggregate baseline was already covered. It does not
judge task correctness or agent performance. Report separately:

- **Task correctness:** Oracle/NOP and discriminating grader controls, with paths.
- **Agent performance:** both real-agent rewards and exceptions, or not run.
- **Coverage:** target method, each trial's evidence, and verify result, or unmeasured.

Keep a correct eval that exposes a failing agent as a regression even when coverage
is not closed. Diagnose a missing scenario trigger separately from an incorrect
response after the trigger. The legacy tool-only `verify` retains its `accepted`
field as the repeated tool-coverage verdict; it is not a task-quality verdict.

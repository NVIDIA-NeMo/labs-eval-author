<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Read your results

Eval Author saves reports and evaluation artifacts in the repository you are
working on. Start with the report for your requested workflow, and read its
limitations before deciding what to change.

## Discovery and readiness

Open `.eval-author/discovery.md`. An inventory describes the evaluations found,
what they test, and documented or source-derived run commands. It does not prove
that the suite can run. A report that found no evaluations describes the scope
inspected; it is not a claim about material outside that scope.

A discovery report adds Gym static validation or Harbor validation evidence and any blockers. Check which
validation steps completed, which could not run, and what needs attention. A
missing backend or credential is a readiness problem, not a failed agent test.
See [Check readiness](existing-evals.md#check-readiness) for the next step.

## First evaluations

The plan in `.eval-author/first-eval.md` records the intended behavior, proposed
cases, and acceptance criteria. Task drafts and run results show which checks
have actually completed.

The no-op baseline and reference solution check the task and its verifier.
Results from running your actual agent are separate evidence of its performance.
A valid task, a working environment, and a successful agent run are distinct
outcomes. See [Build your first evaluations](first-evals.md).

## Coverage audits

Open `.eval-author/audit-progress.md` for the current milestone, selected eval
and trace paths, limitations, answered or pending questions, and next action.
This workflow record lets Eval Author resume unfinished work without repeating
completed milestones and stays separate from generated coverage evidence.

Read `.eval-author/audit.md` to see the behaviors and evidence requirements being
measured. Measurement details live under `.eval-author/audit-measurements/`;
`.eval-author/audit-coverage-report.json` combines the available measurements.
Without usable traces, coverage is **unmeasured**, not 0%; the specification can
still be completed while measurement remains pending. The unchecked **Measure
coverage** step states the reason inline, for example “deferred — selected trace
directory is missing,” so the limitation remains visible in later reviews.

A covered item has supporting evidence under the audit's declared criteria.
An uncovered item may lack evidence in the measured traces, or its evidence type
may not have been measured at all. Review that distinction before proposing a
new evaluation. Coverage does not establish overall agent quality or prove that
an unobserved behavior never occurs.

Use [Propose new evaluations](existing-evals.md#propose-new-evaluations) to turn
supported gaps into candidate cases.

## Trace workflows

Intake inspection writes a report under `.eval-author/traces/` with observed
behavior, issues, recoveries, and uncertainty. Review the cited trace evidence
before treating an observation as a general pattern.

The **experimental** trace-to-environment workflow writes a workspace under
`.eval-author/trace-environments/` containing a summary and the evidence for its
candidate and validation decisions. A `no_candidate` result means the available
evidence did not support a task.
A generated candidate can still have an unproven environment or unresolved
software requirements. Read those limits before attempting execution or
[sharing a task](traces.md#sharing-generated-tasks).

Converting a trace to ATIF, the Agent Trajectory Interchange Format, produces a
structured record for downstream tools. Conversion alone does not measure
coverage or validate a runnable evaluation task.

## Saved output

These are typical paths relative to the repository being evaluated. An existing
Ethos can be reused from a different location, and workflows may stop before
producing every artifact when prerequisites are missing.

| Workflow | Main outputs |
| --- | --- |
| First evaluations | `ETHOS.md`, `.eval-author/first-eval.md`, `.eval-author/task-drafts/`, and `.eval-author/first-eval.yaml` when the agent integration supports it. |
| Discovery and readiness | `.eval-author/discovery.md` |
| Coverage audit | `.eval-author/audit-progress.md`, `.eval-author/audit.md`, `.eval-author/audit-measurements/`, and `.eval-author/audit-coverage-report.json` |
| Intake trace inspection | `.eval-author/traces/` |
| Trace-derived environments (**experimental**) | A private, gitignored workspace per task under `.eval-author/trace-environments/` |
| MLflow conversion | One `.atif.json` file per trace in the private output directory you select. |

[Choose another workflow](../README.md#start-here) or review
[runtime requirements](getting-started.md#requirements).

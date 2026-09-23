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

A readiness report adds Harbor validation evidence and any blockers. Check which
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

Start with `.eval-author/audit-coverage-report.md`. Eval Author authors this
readable report to explain the audit scope, map audit items to existing
evaluations, and summarize coverage, gaps, evidence limits, and next steps. It
links the specification and available supporting evidence. A mapping to an
existing test describes what that test is designed to address; it does not
establish that a recorded run satisfied the audit's coverage criteria.

Read `.eval-author/audit.md` to see the behaviors and evidence requirements being
measured. Measurement details live under `.eval-author/audit-measurements/`;
`.eval-author/audit-coverage-report.json` combines the available measurements.
The Markdown report explains these findings; the JSON report contains the
machine-readable measurement results.

Without usable traces, coverage is **unmeasured**, not 0%; the specification can
still be completed and the Markdown report prepared while measurement remains
pending. The unchecked **Measure coverage** step states the reason inline,
for example “deferred — selected trace
directory is missing,” so the limitation remains visible in later reviews.

A covered item has supporting evidence under the audit's declared criteria.
An uncovered item may lack evidence in the measured traces, or its evidence type
may not have been measured at all. Review that distinction before proposing a
new evaluation. Coverage does not establish overall agent quality or prove that
an unobserved behavior never occurs.

The final checklist step, **Generate and review coverage report**, creates or
updates the Markdown report and reviews its findings with you. The review stays
pending until you respond to the check-in. Whenever a session creates or updates
the report, its final response explicitly says so and links it, even if the
audit stops at an intermediate checkpoint. When an audit resumes, changed
inputs are reconciled with the report before its findings are treated as current.

Open `.eval-author/audit-progress.md` for the current milestone, selected eval
and trace paths, limitations, answered or pending questions, and next action.
This workflow record lets Eval Author resume unfinished work without repeating
completed milestones and stays separate from the coverage report and evidence.

At the report review, Eval Author names the main supported gaps and offers to
[propose new or improved evaluation tasks](existing-evals.md#propose-new-evaluations).
It asks whether to begin, ends the turn, and waits for your answer. Reviewing the
report alone does not start proposal work.
Accepting the findings and this offer starts the proposal workflow directly,
reusing the report, specification, selected sources, and prior answers. Its
recommendations are ranked with expected behavior, verifier design, and evidence,
and saved in `.eval-author/proposals/dataset-recommendations.md`. Creating or
running the proposed tasks remains separately scoped.

The next-step offer adapts to the findings: with no evaluations, Eval Author
offers first-eval creation; with missing evidence, it recommends the needed
measurement and labels any candidate proposals unmeasured. If more tasks would
not address the findings, it explains a useful alternative, such as an agent fix
or gathering specific evidence.

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
| Coverage audit | `.eval-author/audit.md`, `.eval-author/audit-coverage-report.md`, and `.eval-author/audit-coverage-report.json`; supporting artifacts: `.eval-author/audit-progress.md` and `.eval-author/audit-measurements/` |
| Intake trace inspection | `.eval-author/traces/` |
| Trace-derived environments (**experimental**) | A private, gitignored workspace per task under `.eval-author/trace-environments/` |
| MLflow conversion | One `.atif.json` file per trace in the private output directory you select. |

[Choose another workflow](../README.md#start-here) or review
[runtime requirements](getting-started.md#requirements).

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Work on existing evaluations

Follow [the setup guide](getting-started.md) to load Eval Author in your coding
agent. Choose the request below that matches your goal. If you are unsure where
the evaluations live, start with the setup guide's inventory request.
Review the [runtime requirements](getting-started.md#requirements) for the
operation you choose.

## Check readiness

```text
Check whether the Harbor evaluations in this repository are ready to run.
Explain any blockers and show the command for each suite you check.
```

Eval Author uses Harbor's own validators to check configuration, task resolution,
agent and environment setup, and required host variables. It saves its findings
and evidence in `.eval-author/discovery.md`.

Verified readiness requires Harbor in the Python environment used for the
checks, plus access to the selected backend. Without those prerequisites, the
report explains what remains unverified. Readiness establishes whether the
suite can run; it does not measure agent performance or evaluation quality.

Discovery can also describe non-Harbor evaluations and their documented run
commands. Converting those suites to Harbor is currently unsupported.

## Audit coverage

```text
Audit these evaluations against my agent's intended behavior using the
available traces. Explain what is covered, what is missing, and what the
evidence cannot establish.
```

Eval Author opens a fresh full audit with five literal checkboxes and a brief
description of each step:

- [ ] **Understand your agent** — agree on what your agent should do, what it should avoid, and what a good result looks like.
- [ ] **Confirm evals and traces** — find existing evaluations and locate traces (records of agent runs) so we can check what the evaluations actually exercised.
- [ ] **Define what the evals should cover** — agree on the behaviors, tools, and failure cases to check.
- [ ] **Measure coverage** — use the run records to see which of those items were exercised.
- [ ] **Review findings and next steps** — explain gaps, what the evidence can tell us, and what to do next.

It then asks whether you want to continue and waits. This opening comes before
the first milestone: no repository inspection, Ethos reading or validation, or
progress-file reading or writing starts until you accept. An accepted existing
Ethos or supplied trace location does not skip the opening. After your answer,
Eval Author begins **Understand your agent** and checks in after each milestone.
The checklist and opening question appear together in the reply that ends the
turn. Requesting an audit, including asking to load the skill and audit together,
does not answer that question.

After acceptance, Eval Author explains **Ethos**: the document recording what
your agent should do, its boundaries, and what success means, which gives the
audit its target. It links the [Ethos documentation](https://docs.nvidia.com/nemo-helix/documentation/agents/optimize-agents/ethos)
even when a document already exists. An existing Ethos is linked as soon as it is
found, with a short explanation of its intent and an opportunity to request edits
before it becomes the audit baseline.

Opening, milestone, and source-selection questions hand the conversation back
to you. Work stops while the answer is pending, including background work and
delegated reviews. Independent work can finish before a checkpoint or continue
after you explicitly defer the missing input and agree to that work; asking a
question while continuing it in the background is not a check-in.

After the Ethos check-in, Eval Author shows the existing evaluations it found,
links their suite and case locations, and explains what they test. It explains
that traces record the agent's actual actions during a run, letting the audit
check what was exercised beyond the test definitions and pass/fail scores. It then asks
you to select the trace source and location, before searching or reading traces.
This also applies to using traces to identify runtime tool names. A source you
already explicitly selected is reused. If the location is unknown, it helps you
choose a bounded place to look before searching.

The reviewable specification is saved in `.eval-author/audit.md`. Progress,
selected paths, limitations, answered or pending questions, and the next action
are saved separately in `.eval-author/audit-progress.md` after acceptance. On
return to an already-started audit, Eval Author reuses the answered opening and
resumes unfinished milestones with completed work and prior answers intact.
Requests only to validate a specification or measure or aggregate coverage stay
within that scope.

Coverage measurement compares that specification with recorded ATIF traces.
ATIF is a structured record of an agent's interaction. Measurements are saved
under `.eval-author/audit-measurements/`, with an aggregate report at
`.eval-author/audit-coverage-report.json`.

Without usable traces, you can establish the audit specification, but coverage
is **unmeasured**, not 0%. The unchecked measurement step includes the reason,
such as “deferred — selected trace directory is missing,” including in later
check-ins and the final review. If you have no evaluations yet, Eval Author can define
the specification and then offer the [first-eval workflow](first-evals.md).
An uncovered item can reflect a missing scenario,
an agent failure, or insufficient evidence. A coverage report alone does not
identify which explanation applies or establish overall agent quality.

See [Read your results](results.md) for the saved artifacts and their limits.

## Propose new evaluations

```text
Use this audit report to propose the next evaluations to add or improve.
Rank the recommendations and explain the evidence behind each one.
```

Eval Author considers the audit, traces, and existing cases. Recommendations may
include a new scenario, a stronger check, retaining a failing case as a
regression test, or gathering more evidence. They are saved in
`.eval-author/proposals/dataset-recommendations.md`.

This request produces proposals. To create a task, ask for the selected proposal
to be implemented and validated. The current automatic creation workflow supports
one eligible, measured tool-coverage gap at a time; other recommendations may
need further task design or measurement.

For the complete workflows, see the [discovery](../skills/eval-author-discover/SKILL.md),
[audit](../skills/eval-author-audit/SKILL.md), and
[task-creation](../skills/eval-author-task-create/SKILL.md) skills.

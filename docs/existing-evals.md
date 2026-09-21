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

Eval Author establishes or reuses a local **Ethos**, which records the agent's
purpose, boundaries, and success criteria. It then creates a reviewable
`.eval-author/audit.md` describing the tools, capabilities, and failure behavior
that the evaluations should cover.

Coverage measurement compares that specification with recorded ATIF traces.
ATIF is a structured record of an agent's interaction. Measurements are saved
under `.eval-author/audit-measurements/`, with an aggregate report at
`.eval-author/audit-coverage-report.json`.

Without usable traces, you can establish the audit specification, but measured
coverage remains unavailable. An uncovered item can reflect a missing scenario,
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

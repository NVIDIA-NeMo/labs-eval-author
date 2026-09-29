<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Build your first evaluations

Use this guide when your agent has no evaluations yet. Eval Author helps you
build a small Harbor suite that you can rerun after changes.

Follow [the setup guide](getting-started.md) to load Eval Author in your coding
agent, with the repository you want to evaluate open. Then ask:

```text
Help me build my first evaluations for this agent. I do not have evals yet.
Show me the plan first, and explain the cases and how they will be graded.
```

## Establish what the agent should do

Eval Author first helps you establish an **Ethos**: a local document describing
your agent's purpose, boundaries, and success criteria. It can reuse an existing
`ETHOS.md` or help you create and review one.

The initial plan usually contains two or three representative cases. Each case
defines a request, the starting data or environment, an expected outcome, and
checks that distinguish success from failure. For a support agent, that could
mean answering a question from a supplied policy and handling a request the
policy does not cover.

You can plan cases before Harbor is installed. Creating runnable tasks requires
Harbor; see the [Harbor setup guide](../skills/eval-author-discover/references/harbor-setup.md).
Execution also needs the selected environment backend, any required application
access, and a supported connection to your agent. See the full
[runtime requirements](getting-started.md#requirements).

## Check the cases and evaluate the agent

Eval Author creates each case's instructions, environment, reference solution,
and grader. It then checks the tasks with Harbor:

- **NOP** runs a no-op baseline to check what happens when no work is done.
- **Oracle** runs the prepared reference solution to check that the grader
  recognizes the expected outcome.

These checks test the cases themselves. The agent's performance is measured by
running your actual agent with its configured model and credentials. Eval Author
reports that run separately, including scores and execution errors.

A working suite can reveal that your agent performs poorly. Its value is giving
you a repeatable baseline. A few passing cases do not establish broad coverage
or prove that the grader handles every possible response.

## Read the output and run again

The plan and run summary are saved in `.eval-author/first-eval.md`. Generated
tasks live under `.eval-author/task-drafts/`, and run artifacts under
`.eval-author/jobs/`. When the agent integration supports it, Eval Author creates
`.eval-author/first-eval.yaml` with the selected cases and run settings.

Start with `.eval-author/readme.md` when you return to run evaluations. It saves
the required setup, a full-suite command, and a mapping from coverage items to
cases with commands for running them individually. It also explains where to
find rewards, errors, and logs. These commands preserve the saved agent settings
and use fresh output paths. Task sanity checks and actual agent evaluations are
labeled separately.

If a dependency or agent connection is unavailable, the summary identifies the
blocked work and what is needed to continue. See [Read your results](results.md)
for the meaning of the saved outputs.

To extend the suite, ask:

```text
Help me add another case to this suite and update its rerun README.
```

Once you have run evidence, [audit coverage and propose new evaluations](existing-evals.md#audit-coverage).
The [first-eval skill](../skills/eval-author-first-eval/SKILL.md) documents the
complete workflow.

---
name: eval-author-first-eval
description: >-
  Help a user with no evals establish a required Ethos, plan evaluation cases,
  and set up a small working Harbor suite while explaining its parts. No prior
  traces or coverage reports are required. Missing Harbor blocks scaffolding
  and execution, not planning.
triggers:
  - help me build my first evals
  - my agent has no evals yet
  - create an evaluation suite from scratch
not-for:
  - eval-author (use for the shared standard and routing)
  - eval-author-task-create (use for measured audit coverage gaps)
  - eval-author-discover (use to check an existing suite)
compatibility: >-
  Ethos is required before evaluation design and is saved and checked locally
  in the user's repository. No NeMo service, account, CLI, or upload is needed.
  Planning needs no Harbor installation. Scaffolding requires an existing Harbor CLI;
  validation requires its Python environment. Execution may require Docker,
  an agent adapter, and provider credentials.
maturity: alpha
license: Apache-2.0
user-invocable: true
allowed-tools: [Bash, Read, Write, Grep, Glob]
---
<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eval Author: first eval

Read `eval-author` for the shared standard and boundaries. Follow
[Milestone check-ins](../eval-author/references/milestone-checkins.md) throughout
these ten internal stages; that procedure owns transitions, progress, and user
check-ins. Display progress using the core's five-step checklist.
For a direct invocation, use the core's first-eval entry route and authoring
opening before repository work. The user's statement that there are no evals is
enough to select this flow. When routed here from discovery inventory, carry its
findings and prior answers forward, then start at the earliest unfinished
milestone; inventory alone does not establish Ethos or Harbor readiness. Enter
stage 4 only when the first three milestones and applicable check-ins are settled.
Do not repeat completed work or restart an existing intent interview.

No evals is a normal starting state. Do not require a previous run or manufacture
a coverage report to enter `eval-author-task-create`. The initial deliverable is
a small working suite the user understands and can rerun. Modest coverage is
acceptable: comprehensive coverage, difficult cases, repeated agent success, and
trace-driven optimization are not prerequisites. A working suite and strong
evaluation quality are separate claims.

## 1. Establish the agent’s Ethos

Read and follow [Local Ethos](../eval-author/references/local-ethos.md) using the
agent's documentation and intended behavior; this does not depend on discovering
existing evals. Carry its result into the later case plan: the applicable checked
Ethos path, established intent, completed content review when needed, and any
unresolved prerequisite.

## 2. Get Harbor ready

Use the Harbor introduction in the shared milestone procedure before obtaining
setup evidence from [`eval-author-discover`](../eval-author-discover/SKILL.md),
including its interpreter probe and optional assistant-skills check. For missing
or broken installations, follow
[Help the user get Harbor ready](../eval-author-discover/references/harbor-setup.md).

## 3. Understand the evaluation starting point

Reuse the user's stated absence of evals or discovery's confirmed starting point,
along with available agent and documentation findings. Do not run discovery or
ask whether evals exist again solely to complete this milestone. Explain the
outcome concretely: a starter eval set of customer scenarios
with criteria for scoring responses, which the user can rerun after changes to
detect improvement or regression.

Use “starter eval set” for the collection and “eval case” for each scenario.
Introduce a case as a request with criteria for scoring the response. Reserve
“sanity checks” for validation of the cases themselves; use Harbor's technical
term “task” when discussing its files or CLI.

## 4. Define the evaluation scope

Read the agent entry point, tool definitions, and usage docs to understand how
the actual agent runs. Aim for two or three simple representative cases from Ethos,
adjusting to the user's scope and available resources rather than enforcing a quota:
the user request, initial fixture, expected observable outcome, a meaningful
failure example, and the Ethos requirement each case tests. Ask only for intent
or invocation details not already established. Do not make the user supply
Harbor YAML or choose a framework.

When agent or setup evidence points to software or state outside the agent
process, use [Execution dependencies](../eval-author/references/execution-dependencies.md)
to establish the selected cases' runtime and result-collection requirements.

Save `.eval-author/first-eval.md` with the Ethos path and requirement references,
cases, agent invocation, planned verifiers, prerequisites,
and unresolved questions. This is an **evaluation plan**, not a coverage report
or runnable evals.

Start with a reproducible happy path, then a useful variation or expected failure
when supported by Ethos. Grade an observable result rather than a specific tool
call or exact prose. Simple assertions are acceptable if their limits are clear.
Do not replace subjective quality with brittle string
matching or mock away the behavior under test. If the requested case cannot be
tested with available resources, explain the limitation and select a supported
case with the user.

Without Harbor, the deliverable at this point is the evaluation plan; native
task creation remains blocked on setup.

Present the plan using the shared [scope checkpoint](../eval-author/references/milestone-checkins.md#scope-checkpoint).

## 5. Prepare cases and grading

Require a working Harbor CLI and Python environment. Read its
`harbor task init --help` and `harbor run --help` before using options. Use an
unused descriptive slug for each selected case under `.eval-author/task-drafts/`.
Start with one representative task and check its available parts before reusing
the pattern. If its live environment or agent connection is pending, continue
independent case and grading work for the other selected tasks. For each task:

```bash
harbor task init <org>/<slug> --tasks-dir .eval-author/task-drafts \
  --description "<behavior being tested>" --author "<actual author>"
```

Verify that the expected directory was created. Complete Harbor's generated
`instruction.md`, `task.toml`, `tests/test.sh`, and `solution/solve.sh` using its
installed schema; prepare `environment/` in the next milestone. Set executable permissions,
realistic timeouts, and deterministic rewards; leave no scaffold placeholders.
Before running, document each case's reward format, metric names and ranges,
and expected NOP and Oracle acceptance criteria in its README. Derive these
criteria from the intended outcome. For a binary completion metric, NOP should
score 0 and Oracle 1. For named or graded metrics, specify the expected values
or thresholds for each relevant metric instead of imposing a universal 0/1 pair.
Add a README with the Ethos requirement, fixtures, verifier, and run commands.

Apply the core's **Explain the eval pieces as they become relevant** guidance to
the files being created. For each verifier, explain its actual assertion and an
example it cannot distinguish yet. Introduce the Oracle as the prepared reference
solution when creating it. Keep this teaching part of building the starter cases,
without requiring a separate tutorial or exhaustive methodology exercise.

## 6. Prepare the execution environment

Populate the generated `environment/` with the dependencies, fixtures, and
starting state each selected case needs. Check documented access requirements,
credential variable names, and the reset behavior that makes reruns repeatable.
For external dependencies, apply the runtime plan from
[Execution dependencies](../eval-author/references/execution-dependencies.md).
Keep solutions and verifier-only data outside the agent's initial environment.
Verify the selected backend and required application access before declaring
this milestone complete; identifying their requirements is only partial progress.
For Docker-backed execution, check `docker info` first. Record unavailable access
and which cases or checks it blocks.

## 7. Connect the agent

Establish a supported Harbor integration for the actual agent from its entry
point, installed adapter code, registry, and CLI help. Do not substitute another
agent or rewrite the application. If the adapter is missing, identify the specific
integration requirement. Control-agent task validation remains available, but
performance of the user's agent remains unmeasured.

When supported, write `.eval-author/first-eval.yaml` using the installed Harbor
JobConfig schema: explicitly select the working starter tasks, the actual agent
and model settings, one attempt per task, and jobs under `.eval-author/jobs/`.
Do not include unrelated drafts merely because they share a parent directory.
Resolve paths from the repository
root and reference credential environment variables rather than embedding secrets.
Configure request delivery, required conversation state, and collection of outputs
and actions for grading using supported interfaces. Record subsequent connection
checks under **Validate the evals**; configuration alone does not prove that the
connection works.

## 8. Validate the evals

Use Harbor's installed validators to check task validity. Exercise the environment
and grading with the controls below, retaining all jobs under `.eval-author/jobs/`
with new names on reruns:

```bash
harbor run -p .eval-author/task-drafts/<slug> -a nop \
  --jobs-dir .eval-author/jobs --job-name <slug>-nop-1
harbor run -p .eval-author/task-drafts/<slug> -a oracle \
  --jobs-dir .eval-author/jobs --job-name <slug>-oracle-1
```

For each task, inspect Harbor trial results and recorded rewards. Require both
runs to complete without exceptions and meet the case's predeclared NOP/Oracle
criteria, including the expected reward shape. The reference solution should
satisfy the intended outcome; doing nothing should not earn completion credit
when the case requires an answer or action. If inaction is itself correct, NOP
success does not show that the verifier rejects incorrect behavior: exercise
an explicit incorrect response or action as a negative control for that case.
These are basic wiring and verifier sanity
checks, not evidence of broad coverage or a robust benchmark. Do not add repeated
proof runs or a separate negative-control campaign as an onboarding gate.
Investigate obvious unconditional rewards or leaked answers. Fix broken tasks
and rerun affected checks; do not weaken the intended assertion to force a pass.
Report blocked tasks separately and deliver the working subset without silently
dropping planned cases or claiming the whole suite passed.

When the agent config is available, follow `eval-author-discover` to validate it
and report its per-config verdict if other configs exist. Keep unfinished config
validation visible separately from successful control runs. Do not claim a config
is runnable from YAML presence.

## 9. Evaluate the agent

Confirm that the resolved task set matches the selected starter tasks. Explain
the selected task count and where rewards and errors will appear.
Once validated, show the tasks, agent, model, and one-attempt-per-task command.
For authorized execution, run from the repository root:

```bash
harbor job start -c .eval-author/first-eval.yaml
```

Inspect results for every selected task; retain outputs, actions, rewards, and
exceptions as fresh run evidence. A completed evaluation can have low scores.

## 10. Review results and explain reruns

Update `.eval-author/first-eval.md` with exact commands, artifact paths, control
results, per-task agent rewards and exceptions, and remaining blockers. Show how
to rerun the suite, inspect one result, and add or modify a task. Label rerun
commands as task sanity checks or actual agent evaluation.

The working-suite deliverable is reached when the selected starter tasks execute
and record rewards through a validated config, even if the agent scores poorly
or checks are basic. A functioning case that the agent fails provides a useful
baseline; do not weaken it to obtain success.

Name each created eval case and explain the customer behavior it measures.
Translate the recorded controls into their meaning: for a binary action case,
doing nothing failed and the prepared reference solution passed, so the grader
distinguishes those examples. Do not call NOP an empty answer unless that is what
it tested. For graded metrics or cases where inaction is correct, explain the
actual acceptance criteria and observed controls. These checks do not show how
the user's agent performs or prove that all correct answers receive credit.

State whether the actual agent ran and explain the observed scores when it did.
If integration is missing, describe the concrete connection needed at the verified
entry point; use “Harbor adapter” only if that helps the user act. If execution is
blocked by a credential, name the required environment variable to configure in
the execution environment. Describe the next run as scoring actual agent responses,
distinguishing it from configuration or connection setup checks.

Explain practical limitations, such as narrow fixtures, a wording assertion
rejecting a correct paraphrase, or an assertion checking only part of an outcome.
Link the eval cases, results, and established Ethos requirements; identify relevant
intent left outside the starter set. Keep raw scores, interpreter details, and
full commands in the saved report unless useful in the explanation.

Traces and improvement are optional follow-up work. Explain that traces reveal
steps and tool calls that can expose failure patterns, missing coverage, and weak
checks. Link actual trace artifacts when emitted; otherwise identify the adapter
or instrumentation needed to produce them. For requested coverage accounting,
hand the established Ethos and actual ATIF to `eval-author-audit`, then use
`eval-author-task-create` for measured actionable gaps.

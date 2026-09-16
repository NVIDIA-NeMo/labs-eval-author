---
name: eval-author
description: >-
  Build first evals or adapt non-Harbor evals from a required Ethos, work on existing
  evaluation suites in a user's repository, or derive an environment from
  trace evidence, or understand an agent run from NeMo Intake. Owns the evidence
  standard that every Eval Author sub-flow
  follows. Use when the user asks "help me with my evals",
  "what's the state of the eval suite here?", "what happened in this trace?", or
  when you need to pick between the Eval Author sub-flows. Establishes local
  Ethos before routing, without changing the agent's implementation. The selected
  sub-flow uses the provider's supported tools and saves findings under `.eval-author/`.
triggers:
  - help me build evals for my agent
  - my agent has no evals yet
  - help me with the evals in this repo
  - what is the state of the eval suite here
  - I inherited a repo with Harbor tasks in it
  - work on my evaluation suite
  - my evals do not use Harbor
  - what happened in this agent trace
  - create an evaluation environment from a trace
  - which eval author step do I need
not-for:
  - eval-author-first-eval (use to establish Ethos and build first evals without prior coverage or traces)
  - eval-author-discover (use to run the discovery pass and get a runnable verdict)
  - eval-author-adapt (use to adapt existing non-Harbor evaluations after discovery)
  - eval-author-audit (use to generate, validate, measure, or aggregate audit.md coverage)
  - eval-author-task-create (use to propose dataset improvements; when task creation is requested, create and prove an eligible Harbor task)
  - eval-author-inspect-trace (use after this skill selects the trace sub-flow)
  - eval-author-trace-environment (use to derive a Harbor environment from canonical ATIF evidence)
  - nemo-intake (use to instrument agents, ingest telemetry, or query Intake outside Eval Author)
  - mlflow-to-atif (use to convert MLflow traces into canonical ATIF files)
  - nemo-experimentalist (use to run insight-driven optimization end to end, which drives the Eval Author agent itself)
  - nemo-evaluator (use to run an existing benchmark rather than work on a repository's own suite)
compatibility: >-
  The core can save the local Ethos; execution is delegated to sub-flows.
  Discovery, audit, and task creation use the local checkout.
  Task execution requires Harbor and may require Docker and provider
  credentials. Trace inspection requires the nemo CLI, an explicit workspace,
  and read access to configured Intake.
maturity: alpha
license: Apache-2.0
user-invocable: true
allowed-tools: [Read, Write, Grep, Glob]
---
<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eval Author

Work on repository-owned evaluation suites and understand agent traces. Route
each request to the narrow sub-flow that owns it.

## Show the path ahead

For a fresh request to get repository evals working, give the opening reply from
this section immediately after reading this file. No other skill, reference,
repository inspection, Harbor probe, or discovery result is needed to show the
plan. A request to read the whole local skill tree does not require doing so before
this welcome; defer that reading until after the opening answer. Otherwise load
only the instructions needed for the current stage, from this same local tree.

Briefly acknowledge the experience, then render this checklist with literal
`- [ ]` checkboxes, all unchecked, marking the first stage **We're here**. Plain
bullets are not the checklist. Shorten descriptions as useful, but retain the labels:

- [ ] **Establish the agent’s Ethos** — understand the agent's purpose, boundaries, and success criteria; reuse or create and review its Ethos.
- [ ] **Get Harbor ready** — introduce the required framework, then verify its installation and check optional assistant skills.
- [ ] **Understand the evaluation starting point** — find existing evals and confirm the material to use, or establish that we are starting from scratch.
- [ ] **Define the evaluation scope** — select behaviors and cases, establish success criteria, and resolve conflicts between Ethos and existing evals.
- [ ] **Prepare cases and grading** — create task instructions, expected outcomes, and scoring checks; preserve existing scoring when adapting.
- [ ] **Prepare the execution environment** — set up dependencies, fixtures, application access, starting conditions, and reset behavior.
- [ ] **Connect the agent** — configure how tasks reach the agent and how its responses and actions reach the grader.
- [ ] **Validate the evals** — check task validity, environment behavior, and whether graders distinguish correct and incorrect outcomes.
- [ ] **Evaluate the agent** — execute the selected cases and capture fresh evidence and scores.
- [ ] **Review results and explain reruns** — explain outcomes, limitations, remaining gaps, and how to repeat the evaluation.

End with “Ready to get started?” and wait. Do not follow the opening with tool
calls in the same turn. After acceptance, read
[Milestone check-ins](references/milestone-checkins.md) for stage transitions,
progress, and resumption; begin with Ethos. The opening answer does not complete
that stage or waive its check-in.

On return visits, reuse an answered opening and resume the saved stage. Narrow
inventory, readiness, audit, and trace requests use their scoped sub-flow instead
of this onboarding experience. If onboarding later finds an existing Harbor suite,
tailor the remaining work to that suite without restarting the completed stages.

A report that a downstream model trusts has to be right. A plausible report is
worse than no report when somebody acts on it.

## The standard

**Every fact you record comes from authoritative evidence, not a guess.**

The authority depends on the sub-flow:

- For suite discovery, Harbor's validators judge runnability. A file's presence
  doesn't prove that Harbor accepts it.
- For adapting existing evals, Ethos establishes intended agent behavior; the
  original cases, fixtures, and scoring rules establish what to preserve.
  Resolve conflicts with the user before changing scoring. Harbor validation and
  controlled task runs prove the new wiring, not scoring equivalence by themselves.
- For first evals, Ethos establishes intended behavior. NOP and Oracle check
  basic task wiring and verifier behavior; the user's agent run establishes
  a baseline. Working setup does not establish evaluation quality or coverage,
  and a plan alone is not proof of runnability.
- For audit-spec validation, the bundled schema and validator judge the finite
  `audit.md` coverage denominator.
- For task creation, Harbor's Oracle judges task solvability and verifier
  correctness; measured ATIF proves whether repeated runs close the selected gap.
- For trace inspection, Intake establishes what happened. Local source code can
  explain behavior, but it can't replace recorded trace evidence.
- For trace-derived environments, canonical ATIF establishes the request and
  Harbor's NOP and Oracle runs prove the generated environment.

No sub-flow reimplements a provider's rules. When evidence can't settle a claim,
the report marks the claim unproven or uncertain.

## Vocabulary

The sub-flows share this language, and reports use it verbatim.

| Term | Meaning |
|---|---|
| Check | One named result: `pass`, `warn`, or `fail`. Carries a message and, when it fails, a hint |
| Required | A failing required check blocks the suite. Report the suite as not ready |
| Advisory | A warning worth surfacing that blocks nothing |
| Rung | One step of a provider's validation ladder, ordered so a lower rung's failure often clears once a higher one is fixed |
| Proven | A provider judged this check. An unproven check is an observation and never evidence |
| Provider | The evaluation framework that owns the rules. Harbor today |
| Finding | One trace claim categorized as `behavior`, `issue`, `recovery`, or `uncertainty`, with evidence IDs |
| Outcome | The trace assessment: `success`, `failure`, or `unknown` |

## Sub-flows

Read the selected sub-flow's own `SKILL.md` when its stage begins and follow it.
This file carries the standard and boundaries; the sub-flow carries the steps.

| Sub-flow | Use it to |
|---|---|
| `eval-author-first-eval` | Establish required Ethos, plan cases even without Harbor, and set up a small working suite while teaching the user how to run and extend it |
| `eval-author-discover` | Establish whether a repository's evaluations run, name the rung that fails, and get the exact command to run them |
| `eval-author-adapt` | Establish required Ethos, convert existing non-Harbor material into task files, preserve scoring, and guide validation and execution |
| `eval-author-audit` | Generate and validate a finite `audit.md` coverage denominator, measure and aggregate trace coverage, and report findings |
| `eval-author-task-create` | Propose concrete dataset improvements from audit findings; when task creation is requested, create one eligible Harbor task and prove it with Oracle and repeated measured runs |
| `eval-author-inspect-trace` | Understand one Intake trace without presuming that the trace contains a failure. Not user-invocable; this skill selects it |
| `eval-author-trace-environment` | Normalize one trace to ATIF, make a privacy-reviewed candidate decision, and build a private Harbor task when evidence supports it |

`eval-author-audit` works one level above tasks: it generates and validates the
coverage denominator, measures traces against it, and aggregates deterministic
coverage reports. `eval-author-task-create` owns the proposal step: prioritize
dataset improvements from those findings across tools, capabilities, and failure
cases while preserving their measured or unmeasured status. Proposal-only
requests stop there. Its subsequent task-creation path consumes only actionable
tool gaps and uses Harbor's native task scaffolder rather than guessing a task
layout. For a requested full workflow, proceed from audit to proposals even when
there are no eligible tool gaps; an audit-only request ends with the findings.

## Establish Ethos before authoring

Both first-eval and adaptation require an applicable `ETHOS.md` before case design,
new scoring decisions, or task authoring. Read [Local Ethos](references/local-ethos.md)
for the shared locate, reuse, intent, creation, validation, and review procedure.
Agent documentation can inform Ethos before any evaluation inventory. Existing
evals establish what is currently tested; they do not replace intended behavior.

## Gather requirements and setup from evidence

During discovery and source inspection, read relevant repository and supplied
documentation before asking the user to reconstruct it. Follow references to
requirements, rubrics, setup guides, dependency manifests and lockfiles, agent
configs, runner scripts, and license or access instructions. Gather what applies:

- **Purpose and success:** scenarios, expected behavior, grading rules, and relevant constraints.
- **Inputs and documentation:** source cases, fixtures, example outputs, and instructions for using them.
- **Execution:** the agent and how to invoke it, required software/services and versions, OS, hardware, and where each dependency runs.
- **Access and licenses:** documented installation and execution requirements, license provisioning, required accounts and credential variable names. Do not request secret values in chat or copy them into reports.
- **Repeatability:** starting data/state, session handling, reset procedure, and how results reach the grader.

Distinguish documented requirements, user-confirmed information, verified
availability, and unknowns. Cite the source and record what an unresolved item
blocks: task preparation, a particular grading check, or live execution. A repo
license does not establish the license or availability of its dependencies.
Ask focused questions only about missing facts that affect the next work, and
reuse earlier answers. Missing access or license provisioning can leave execution
pending while task files and independent checks proceed.

Keep the gathered requirements, progress, and next action in the selected
sub-flow's existing human-readable findings or task README under `.eval-author/`.
Do not overwrite generated evidence reports or require a new intake document
before conversion. For read-only requests, explain findings in the reply within
that sub-flow's reporting boundaries.

## Route after the evaluation starting point

The shared milestone procedure leads onboarding through Ethos, Harbor, then
`eval-author-discover`. Discovery owns the evaluation inventory, source selection,
and saved findings; its runtime probes can be used separately during the Harbor
stage. Reuse completed checks and answers when their inputs are unchanged.

Follow discovery's **When no Harbor evals were found** conversation before routing
candidate material; an empty Harbor scan does not establish that no evals exist.
An explicitly supplied source already answers source selection. Once the evaluation
starting point is settled, carry the established Ethos, Harbor invocation, findings,
and answered check-ins into the selected path:

- **Existing Harbor suite or tasks:** continue discovery and resolve configuration
  or readiness failures. Broken evals are not a reason to start over.
- **Existing non-Harbor material:** read
  [`eval-author-adapt`](../eval-author-adapt/SKILL.md) and continue at **Define the
  evaluation scope**. When Harbor and non-Harbor evals coexist, follow the user's
  chosen suite. Adaptation owns mapping, scoring preservation, and task delivery.
- **Confirmed absence of evals:** read
  [`eval-author-first-eval`](../eval-author-first-eval/SKILL.md) and continue at
  **Define the evaluation scope**. A missing config does not block this starter
  flow; do not substitute audit-gap task creation.
- **Unknown or inaccessible evals:** ask for the location or an accessible
  representative case and its scoring. An access failure does not prove absence.

An inventory-only request ends with findings and an offered next step. Discovery
alone does not authorize creating or running evals.

## Continue after a successful evaluation

Follow the shared [post-evaluation handoff](references/milestone-checkins.md#after-a-successful-evaluation)
to offer help creating more evals through a repository and coverage audit.
That procedure owns the trigger, question, and accepted handoff to
`eval-author-audit` for both first-eval and adaptation.

## Boundaries

These hold for every sub-flow. They exist because the repository belongs to the
user, not to you.

- **Propose, never mutate customer source.** Read the user's source and report on
  it. Do not edit, move, or reformat any of it, including its `.gitignore`. The
  evaluation artifacts you add belong under `.eval-author/`, which is theirs to
  commit or ignore. The sole additional write scope is the requested local
  `ETHOS.md`: follow [Local Ethos](references/local-ethos.md) to create or make
  user-requested edits to it in the repo. Preserve existing Ethos content and
  custom sections; downstream audit measurement does not rewrite it.
  `eval-author-discover` scripts write nothing; `eval-author-audit` writes only
  requested audit artifacts; `eval-author-task-create` writes only drafts,
  proposals, job outputs, and measurements there; `eval-author-trace-environment`
  writes only private, gitignored task workspaces there.
  `eval-author-adapt` writes its mapping, task copies, configs, and job outputs
  under `.eval-author/`; the original evals remain the source for preserved cases
  and scoring. `eval-author-first-eval` writes plans, drafts, configs, and jobs there.
  Both authoring flows use the narrow local Ethos write exception above.
- **A missing tool is a finding, not a task.** When the provider is not installed,
  say so and stop short of proving anything. Report what you found regardless, and
  do not install the provider automatically. Use discovery's Harbor setup guidance
  to explain installation and verification. An explicit request to install is
  authorization for that setup; a broad eval request alone is not.
- **Do not run without approval.** Discovery proves an existing suite can run and
  hands over the command. Task creation may run Oracle locally, then starts
  real-agent jobs only when the user explicitly asked for or approved that spend.
  Adapting evals may run local task sanity checks when task creation is requested;
  real-agent or paid-judge runs require authorization for that execution and spend.
- **Trusted repositories only.** Validating a config can execute repository code,
  because an agent named by import path gets imported. If the repository is not
  trusted, say so and stop.
- **Intake reads are narrow.** Only `eval-author-inspect-trace` reads Intake. It
  uses read-only `nemo intake` commands against the configured instance and
  workspace. No sub-flow discovers accounts, ingests data, uploads files, or
  changes a remote resource.

## Communicating with the user

### Explain the eval pieces as they become relevant

Do not assume the user knows Harbor terminology or has a particular repository
layout, scorer, agent runner, or access to the system being tested. Ground the
explanation in inspected material and the user's answers. Introduce the relevant
pieces in plain language before asking the user to make decisions about them:

| Piece | What it does |
|---|---|
| Task | The test scenario: what the agent is asked to do, with any inputs and conversation steps |
| Environment | The files, data, tools, and software the task needs, including its starting state and how to reset it |
| Agent connection | How Harbor gives the task to the actual agent and collects its responses and actions |
| Grading criteria | The rules for deciding whether the agent did the task well |
| Grader, also called a verifier | The checks that apply those rules to evidence from the attempt and produce a result or score |
| Run and results | One attempt at the task, its recorded actions or outputs, and the grading results |

Use a short explanation of the pieces relevant now, not this entire table in
every reply. When useful, explain a reference solution as a known correct way to
complete the task, used to test the grader; a past response is not automatically
such a solution. Keep environment setup separate from the agent connection.

Map each discussed piece to what was found or created, what was actually tested,
and any specific gap. Existing executable evals may already supply grading;
written criteria may need implementation; recordings may lack intended outcomes.
Unknown access is not proof that access is unavailable. Missing evidence should
lead to a focused question or an explicit limitation, not an assumed setup.
Explain unfamiliar terms such as rubric, judge, weights, or partial credit before
asking about them. A checklist status or file link cannot replace that explanation.

Grading asks how an attempt performed against the task's criteria. A coverage
audit asks which intended agent behaviors the evaluation evidence covers. Explain
that distinction when offering the existing audit flow; the audit does not finish
a task's grader or supply its runtime access.

### Validation and result reports

For completed discovery, validation, or execution reports, lead with the verdict
or outcome, then the evidence. This format does not apply to onboarding or an
intent question while establishing Ethos.

For dataset proposals, follow `eval-author-task-create` Step 1: lead with concrete
recommendations and their evidence, then supporting coverage counts and limits. An empty
task-generation selection does not establish that the dataset needs no changes.

In validation and execution reports, state whether findings are proven, whether
the suite is ready, and the checks that failed. Never describe a suite as ready while a required check
fails, and never present an observation as proof. When a sub-flow could not reach
its provider, its validation report must state that readiness was not proven.
This does not block the empty-scan conversation, source-grounded adaptation
planning, or first-eval Ethos and case planning within their prerequisite rules.

For a trace, use `success`, `failure`, or `unknown`. Tie key moments and findings
to span IDs, evaluator result IDs, or source symbols. A healthy trace doesn't
need an issue finding.

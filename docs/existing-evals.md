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
- [ ] **Confirm evals and traces** — confirm which evaluations to audit and locate traces (records of agent runs) so we can check what the evaluations actually exercised.
- [ ] **Define what the evals should cover** — agree on the behaviors, tools, and failure cases to check.
- [ ] **Measure coverage** — use the run records to see which of those items were exercised.
- [ ] **Generate and review coverage report** — create or update `audit-coverage-report.md`, then review coverage, gaps, evidence limits, and next steps together.

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
The first Ethos check-in explains both what the document is and how the audit
uses it to define expected coverage before comparing with tests and run records.
That explanation stays in the reply even when the file needs formatting repairs;
it comes before validation details and the repair question.

Opening, milestone, and source-selection questions hand the conversation back
to you. Work stops while the answer is pending, including background work and
delegated reviews. Independent work can finish before a checkpoint or continue
after you explicitly defer the missing input and agree to that work; asking a
question while continuing it in the background is not a check-in.

After the Ethos check-in, Eval Author shows the existing evaluations it found,
links their suite and case locations, and explains what they test. It asks you
to confirm which suites belong in the audit, including any additions or
exclusions, and waits before moving to traces. Suites you already explicitly
selected are reused without another confirmation. Discovery alone does not
select a suite, and giving a trace location does not confirm the suite list.

Once the evaluation scope is confirmed, it explains that traces record the
agent's actual actions during a run, letting the audit check what was exercised
beyond the test definitions and pass/fail scores. It then asks you to select
the trace source and location, before searching or reading traces.
This also applies to using traces to identify runtime tool names. A source you
already explicitly selected is reused. If the location is unknown, it helps you
choose a bounded place to look before searching.

At **Define what the evals should cover**, Eval Author explains the two review
artifacts: `.eval-author/audit.md` specifies the proposed checks and required
evidence, and `.eval-author/audit-coverage-report.md` presents that scope alongside
readable test mappings and evidence findings. The specification is a draft
pending your review; the report is preliminary at this point.

The report's **Intended coverage** section lists every audit item's stable name
and kind, a plain-language explanation of what should be checked, and the
evidence required to establish coverage. Existing tests, observed evidence, and
measurement status stay distinct from those intended checks. At the scope
check-in, the reply previews the proposed checks grouped by tools, capabilities,
and failure cases and links directly to the full **Intended coverage** section.
It asks which intended checks are missing or incorrect and names the next
milestone. Agreeing to this scope does not approve the final report's findings.

Progress, selected paths, limitations, answered or pending questions, and the
next action are saved separately in `.eval-author/audit-progress.md` after
acceptance. On return to an already-started audit, Eval Author reuses the answered
opening and resumes unfinished milestones with completed work and prior answers
intact. Requests only to validate a specification or measure or aggregate
coverage stay within that scope.

Coverage measurement compares that specification with recorded ATIF traces.
ATIF is a structured record of an agent's interaction. Measurements are saved
under `.eval-author/audit-measurements/`, with an aggregate report at
`.eval-author/audit-coverage-report.json`.

Eval Author also writes `.eval-author/audit-coverage-report.md`, a readable report
that explains the audit scope, maps audit items to existing evaluations, and
summarizes measured coverage, gaps, evidence limits, and next steps. It links the
specification and available evidence. The agent authors this report using the
shared template; it is separate from the generated JSON measurement report.
Test mappings describe what evaluations are designed to address and do not,
by themselves, establish measured coverage.

The Markdown report can be prepared before measurement and updated as evidence
becomes available. Without usable traces, you can establish the audit
specification and report, but coverage is **unmeasured**, not 0%. The unchecked
measurement step includes the reason, such as “deferred — selected trace
directory is missing,” including in later
check-ins and the final review. If you have no evaluations yet, Eval Author can define
the specification and then offer the [first-eval workflow](first-evals.md).
An uncovered item can reflect a missing scenario,
an agent failure, or insufficient evidence. A coverage report alone does not
identify which explanation applies or establish overall agent quality.

The final checklist step includes generating the Markdown report and reviewing
it with you. Saving it does not complete that step: the review remains pending
until you respond to the review check-in. Whenever a session creates or updates
the report, its final response says so and links it, including at intermediate
checkpoints. On resume, Eval Author reconciles the report with changed inputs
before presenting its findings as current.

The review ends with a concrete offer to help with the next step. For an existing
suite with supported gaps, Eval Author names the main gaps and offers to propose
new or improved evaluation tasks, ranked with their expected behavior, verifier,
and supporting evidence. It explicitly asks whether you want those proposals,
ends the turn, and waits. Accepting the findings alone does not start proposal
work. Accepting the findings and that offer moves directly
into the proposal workflow, reusing the report, specification, selected sources,
and prior answers.

The offer follows the evidence. With no evaluations, it points to the
[first-eval workflow](first-evals.md). With insufficient evidence, it recommends
the needed measurement first; any candidate task proposals are explicitly
unmeasured. If the findings do not support more tasks, it explains the useful
alternative, such as addressing an observed agent failure or gathering specific
evidence.

See [Read your results](results.md) for the saved artifacts and their limits.

## Propose new evaluations

```text
Use this audit report to propose the next evaluations to add or improve.
Rank the recommendations and explain the evidence behind each one.
```

Eval Author considers the Markdown coverage report, underlying measurements,
traces, and existing cases. Recommendations may include a new scenario, a
stronger check, retaining a failing case as a regression test, or gathering more
evidence. Each recommendation explains its priority, expected behavior, how a
verifier would check it, and supporting evidence. They are saved in
`.eval-author/proposals/dataset-recommendations.md`. You can request this directly
or accept Eval Author's offer during the audit review; the handoff reuses the
audit inputs and settled answers.

The coverage report's next steps provide context for this separate proposal
workflow; they do not replace its recommendations artifact.
Accepting the proposal offer produces recommendations. Creating, validating,
or running tasks remains separately scoped: ask for the selected proposal to be
implemented and validated when you are ready. The current automatic creation
workflow supports one eligible, measured tool-coverage gap at a time; other
recommendations may need further task design or measurement.

For the complete workflows, see the [discovery](../skills/eval-author-discover/SKILL.md),
[audit](../skills/eval-author-audit/SKILL.md), and
[task-creation](../skills/eval-author-task-create/SKILL.md) skills.

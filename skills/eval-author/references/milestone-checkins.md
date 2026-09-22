<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Check in after each milestone

The core selects the entry route before its authoring welcome and canonical
checklist. Read this reference for first-eval after the user starts
that experience; it owns stage transitions, progress, and resumption. Discovery
inventory, audits, and proposals keep their scoped entry procedures. Sub-flows
own the work within authoring stages. Throughout this procedure, a stage means
one of the ten internal stages. The core's five visible checklist steps group
their progress without combining stages or changing their check-ins.

## Complete, explain, check in, wait

1. Finish the authorized work for the current stage, or identify the specific
   requirement preventing completion. Make its result concrete and reviewable.
2. Explain what was found or produced, why it matters, and the limits of the
   evidence. Link artifacts beside their explanation and refresh the checklist.
3. Name the next stage and ask one focused question about the result or that next
   step. End the reply and wait for the answer before starting the next stage.
   Address questions or corrections within the current stage first. At the final
   results stage, ask whether anything needs explanation or revisiting and stop.

A question requesting the next stage's first needed input can serve as this
check-in. Review of a saved Ethos can settle the Ethos stage; a source-selection
answer can settle the evaluation starting point and allow scope planning. Reuse
answered transitions without another readiness prompt. A broad request to get
evals working does not waive stage conversations. Preserve existing installation
and execution authorization under the core's boundaries.

Keep tool work and instruction loading focused on the current stage. Read-only
inspection needed to answer its question is allowed, but do not begin later-stage
scans, probes, interviews, artifact creation, integration, or runs while its
check-in is unanswered. Within the current stage, complete independent authorized
work. If a prerequisite prevents completion, explain the limitation and ask whether
to defer it and move to a named independent stage. Wait for that choice, keep the
deferred stage incomplete and its visible step unchecked, and return when its
prerequisite is available.

## Progress and resumption

Use the core's five visible checklist labels, stage grouping, and checkbox syntax
throughout the sub-flows; do not render the ten internal stages as another checklist.
Render it in source-selection replies, stage check-ins, and return visits, rather
than after every tool call. A saved report, link, findings list, or promise to show
it later does not replace the visible checklist. Put findings and the checklist
before the closing question. Mark the visible step containing the current internal
stage **We're here**, including when an earlier prerequisite was explicitly
deferred. Use `[x]` only when every internal stage in that step is complete; an
answered check-in is separate from technical completion. Leave future and partial
steps unchecked, naming their remaining work. Continue the same check-ins between
internal stages even when the visible step does not change. Ordinary intent or
source questions do not need a blocked status.

Track case/grader preparation, environment availability, and agent configuration
separately. A first case is partial progress when the agreed scope is a larger
suite. Configuration is not validation; a successful control run is not evaluation
of the actual agent. Keep validation open when required checks fail or remain
unrun. A completed evaluation can have low scores without being incomplete.
The owning sub-flow defines the evidence needed to complete each stage.

Save the internal stage, evidence, pending question or answered transition, and
next action in the existing findings or task README. Before those exist, retain early-stage
state in the conversation or existing intent notes; do not run discovery just to
obtain a report. Keep Gym or Harbor probe evidence, local interpreter paths, and milestone
or approval records in that workflow state, not in `ETHOS.md`. This does not exclude
substantive evaluation requirements from Ethos's Evaluation Setup section.
On return, reuse applicable answers and completed work, rechecking
readiness when inputs changed. Do not infer an answer from an installed tool or
saved file, or restart a completed opening or Ethos interview. Inventory before
authoring may already have settled the evaluation starting point, but does not
complete Ethos or provider setup. Narrow inventory, readiness, audit, proposal,
trace, and internal validation requests keep their scoped flow.

## Early stages: Ethos, provider setup, then evals

### 1. Establish the agent’s Ethos

After the opening answer, follow [Local Ethos](local-ethos.md). Identify the agent,
understand its intended purpose and limits, and reuse or create its document.
This stage uses agent context, not an eval inventory. Do not load authoring or
audit sub-flows, probe Gym or Harbor, or scan reports and traces to choose an eval source.
A missing Ethos calls for the next focused intent question. An applicable existing
Ethos calls for a brief explanation of its intent, not a fresh interview.

New or revised saved content is reviewed through the local procedure. That review
is the check-in before provider setup; name Gym or Harbor as the selected next stage. For an applicable
unchanged document, summarize what it establishes and check in before provider setup
without demanding another content approval. Neither mentioning Ethos in the plan
nor answering an intent question completes the document procedure.

### 2. Get Gym or Harbor ready

After the Ethos check-in, select the provider from the user's choice and existing
suite. For a new suite, offer **Gym first, Harbor second**, explaining the fit to
the actual agent. Introduce the selected framework before probing its installation.
Explain that it supplies tasks and environments, connects the agent, applies
grading, and records results. Eval Author requires the **selected** provider for
native authoring and execution, not both frameworks.

For Gym, follow [Get Gym ready](../../eval-author-discover/references/gym-setup.md)
and link [Gym's documentation](https://docs.nvidia.com/nemo/gym/latest/).
For Harbor, follow the existing [runtime prerequisite checks](../../eval-author-discover/SKILL.md#runtime-prerequisite-checks)
and [Harbor setup guide](../../eval-author-discover/references/harbor-setup.md),
including the optional assistant-skills advisory, and link
[Harbor's documentation](https://www.harborframework.com/docs).
Do not run a full evaluation scan at this setup milestone.

Retain the actual interpreter, command, version, and unresolved requirements.
The checkpoint reply explains the selected framework even when an existing
installation is reused. Working setup does not prove task-specific readiness,
model access, correct verifiers, or successful runs. For example:

> NeMo Gym composes your evaluation dataset, tools and verifier, agent, and model
> connection. It records rollouts and rewards so we can repeat tests after changes.
> Gym's command and Python environment work. We still need to check this task's
> components and the connection to your actual agent.

Use actual setup evidence, include any relevant optional-skills advisory, and
retain the shared checklist. Do not report setup as passed when only installation
instructions were supplied.

Check in before the next unfinished stage. If the evaluation starting point is
already settled, carry it forward and proceed to **Define the evaluation scope**
after this check-in. Otherwise, asking about existing material can serve as the
transition to **Understand the evaluation starting point**. If a source is already
supplied, name the planned inspection without asking them to select it again.
Missing Gym or Harbor can be deferred using the rule above; it does not prevent finding
the user's eval material.

### 3. Understand the evaluation starting point

Reuse a starting point already settled by the user or discovery inventory; no
repeat scan or source-selection question is needed. Otherwise, after the provider setup
check-in use `eval-author-discover` for inventory and source selection, reusing
verified runtime evidence. Determine whether there is an existing Gym or Harbor suite,
other eval material, or confirmed absence of evals. Ask about actual candidates
or a missing location; keep this stage unchecked and current until the source is
settled. The report's summary and examples supply findings and question wording,
not a complete onboarding reply in place of the checklist.

A source answer identifies the material, not its scoring quality or coverage.
Name **Define the evaluation scope** as the next stage and use the core's
**Route after the evaluation starting point** handoff. Carry forward Ethos,
setup evidence, and answered transitions; do not restart them when authoring
continues. Any conflict between discovered criteria and Ethos is
resolved during scope planning, not by silently changing either one.

## Scope checkpoint

At **Define the evaluation scope**, explain what the selected cases will measure
before moving to **Prepare cases and grading**. Use the calling flow's existing
plan or mapping to make the scope concrete:

- **Behavior and purpose:** what the agent should accomplish and why these cases
  matter, using established workflow priorities when available.
- **Success and evidence:** the expected outcome, what the grader must inspect,
  and whether the rule comes from existing criteria or is a proposed decision.
- **Execution requirements:** the capabilities, software, starting state, and
  access the cases need; distinguish known requirements from verified readiness.
- **Limits and open decisions:** missing criteria or evidence, which checks or
  runs they affect, and what is needed to resolve them.

Explain this through a representative case, grouping others with the same needs
and calling out material differences. Distinguish checking a tool sequence from
checking its resulting outcome. Explain the role of operational metrics such as
cost or latency when present; they establish success only where the agreed
criteria use them. Preserve existing scoring and explain its limits rather than
silently replacing it.

Use the existing stage check-in to settle the next affected decision or confirm
the scope. Reuse established answers; missing inputs for one check need not hold
up independent case preparation. This checkpoint explains the selected scope,
without requiring a coverage audit or a new intake document.

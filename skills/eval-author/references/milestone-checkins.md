<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Check in after each milestone

The core owns the immediate welcome and canonical checklist. Read this reference
after the user starts the experience; it owns stage transitions, progress, and
resumption. Sub-flows own the work within stages.

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
deferred stage unchecked, and return when its prerequisite is available.

## Progress and resumption

Use the core's same checklist labels and checkbox syntax throughout the sub-flows.
Render it in source-selection replies, stage check-ins, and return visits, rather
than after every tool call. A saved report, link, findings list, or promise to show
it later does not replace the visible checklist. Put findings and the checklist
before the closing question. Mark the current focus **We're here** and use `[x]`
only for work actually completed; an answered check-in is separate from technical
completion. Leave future and partial stages unchecked, naming their remaining
work. Ordinary intent or source questions do not need a blocked status.

Track case/grader preparation, environment availability, and agent configuration
separately. A first case is partial progress when the agreed scope is a larger
suite. Configuration is not validation; a successful control run is not evaluation
of the actual agent. Keep validation open when required checks fail or remain
unrun. A completed evaluation can have low scores without being incomplete.
The owning sub-flow defines the evidence needed to complete each stage.

Save the stage, evidence, pending question or answered transition, and next action
in the existing findings or task README. Before those exist, retain early-stage
state in the conversation or existing intent notes; do not run discovery just to
obtain a report. On return, reuse applicable answers and completed work, rechecking
readiness when inputs changed. Do not infer an answer from an installed tool or
saved file, or restart a completed opening or Ethos interview. Narrow inventory,
readiness, audit, trace, and internal validation requests keep their scoped flow.

## Early stages: Ethos, Harbor, then evals

### 1. Establish the agent’s Ethos

After the opening answer, follow [Local Ethos](local-ethos.md). Identify the agent,
understand its intended purpose and limits, and reuse or create its document.
This stage uses agent context, not an eval inventory. Do not load authoring or
audit sub-flows, probe Harbor, or scan reports and traces to choose an eval source.
A missing Ethos calls for the next focused intent question. An applicable existing
Ethos calls for a brief explanation of its intent, not a fresh interview.

New or revised saved content is reviewed through the local procedure. That review
is the check-in before Harbor; name Harbor as the next stage. For an applicable
unchanged document, summarize what it establishes and check in before Harbor
without demanding another content approval. Neither mentioning Ethos in the plan
nor answering an intent question completes the document procedure.

### 2. Get Harbor ready

After the Ethos check-in, introduce Harbor in the conversation before probing its
installation. Explain its purpose and required role even if installation evidence
is already available. For example:

> Now that we've established what your agent should do, we'll prepare the eval
> framework. [Harbor](https://www.harborframework.com/docs) gives the agent cases,
> runs them in their required environment, applies grading checks, and records
> results for repeatable comparisons. Eval Author requires Harbor to create,
> validate, and run its eval tasks. I'll check its setup next.

Then use discovery's [runtime prerequisite checks](../../eval-author-discover/SKILL.md#runtime-prerequisite-checks),
including its optional-skill advisory, without running the full evaluation scan.
Use its [setup guide](../../eval-author-discover/references/harbor-setup.md) for a
missing or broken installation. Preserve the actual command, interpreter, and
version for later use; setup does not prove task-specific readiness.

Explain the setup result and check in before **Understand the evaluation starting
point**. If the user has not supplied evals, asking whether they have existing
material can serve as this transition. If a source is already supplied, name the
planned inspection without asking them to select it again. Missing Harbor can be
deferred using the rule above; it does not prevent finding the user's eval material.

### 3. Understand the evaluation starting point

After the Harbor check-in, use `eval-author-discover` for the inventory and its
source-selection conversation. Reuse the verified runtime instead of repeating
setup. Determine whether there is an existing Harbor suite, other eval material,
or confirmed absence of evals. Ask about actual candidates or a missing location;
keep this stage unchecked and current until the source is settled. The report's
summary and examples supply findings and question wording, not a complete
onboarding reply in place of the checklist.

A source answer identifies the material, not its scoring quality or coverage.
Name **Define the evaluation scope** as the next stage and use the core's
**Route after the evaluation starting point** handoff. Carry forward Ethos,
setup evidence, and answered transitions; do not restart them when first-eval
or adaptation takes over. Any conflict between discovered criteria and Ethos is
resolved during scope planning, not by silently changing either one.

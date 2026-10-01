<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Preserve evaluation evidence during recovery

Apply this guidance when executing or reporting an evaluation, including after
an endpoint, adapter, dependency, or environment failure. Preserve the selected
provider, target agent, tasks, fixtures, and original verifiers during recovery.
For a Harbor evaluation, completion requires actual Harbor job/trial artifacts
from that agent and those verifiers. Native Gym evaluations retain their native
evidence requirements; they are not a fallback completion path for a Harbor run.

## Repair the integration, then rerun

Retain failed trials, raw results, logs, and the command and configuration that
produced them. Diagnose the failing boundary before changing it. An endpoint
rejecting an unsupported request parameter is an integration failure, not an
observed failure of the agent's task-solving ability.

Within the authorized scope, repair the integration while preserving the task,
fixture, and grading semantics. For example, removing an unsupported
`prompt_cache_key` from the affected endpoint request may be a compatibility
fix; replacing the agent, application, or verifier is not that fix. Record the
patch and affected source/configuration versions, including provider, adapter,
model/endpoint settings and task/verifier revisions or digests. Do not record
credentials. Run the selected target agent through Harbor again, with the
original verifiers and fresh job/trial outputs. Keep the failed attempt and
link it to the rerun instead of overwriting or relabeling it.

Approval for a temporary compatibility patch does not authorize a different
evaluation protocol. If repair cannot preserve the selected path within scope,
report the evaluation incomplete with the remaining blocker. A separately
requested protocol change produces a separately identified evaluation; its
results do not retroactively complete the original Harbor run.

## Keep diagnostic work separate

Local application runs, direct endpoint calls, and manual verifier probes may
help debug the integration. Never substitute assistant-authored task answers,
local diagnostic runs, reconstructed graders, or manufactured job artifacts for
the requested evaluation. Do not synthesize Harbor results from local outputs,
even when the real application ran and the workaround was disclosed.

Start a diagnostic report with **Diagnostic only — Harbor evaluation incomplete**
when the requested Harbor run remains incomplete. Retain that qualification in
later summaries, comparisons, and checklist recaps. Label any diagnostic score
beside the score; do not lead with an unqualified pass rate or “comparison
complete.” Keep diagnostic outputs outside authoritative Harbor aggregates.
Never mark the requested run or whole pipeline complete based on those outputs.

## Report what actually executed

For each completed evaluation claim, identify the actual job and trial paths,
selected target agent/model configuration, tested task/verifier versions, and
the retained native results and verifier outputs. Oracle controls establish
reference behavior, not results for the target agent. Missing jobs, trials,
or verifier evidence remain explicit; report any completed subset separately
from the outstanding requested work.

Preserve raw Harbor rewards, exceptions, and trial statuses. Add an explanation
that distinguishes infrastructure failures, blocked or missing trials, and
agent-quality failures without rewriting those outcomes. Show requested and
completed trial counts and the denominator of every score. An infrastructure
failure is not evidence of poor agent quality; a genuine low score from completed
trials does not justify weakening the task or its grader. Completion describes
execution with evidence, not a requirement that the agent pass.

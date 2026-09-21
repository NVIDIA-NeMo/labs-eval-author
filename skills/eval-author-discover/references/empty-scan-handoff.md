<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Empty-scan handoff

## When no Harbor evals were found

Use this conversation only after a completed scan has no configs, task files, or
dataset directories. Files that failed validation or tasks without a config stay
on the existing-suite path. The inventory's depth and excluded directories limit
what was inspected; a user-supplied location takes precedence over scan absence.
The scanner also picks up configs by `tasks` or `datasets` keys. If source or
documentation shows that a candidate belongs to another framework, explain that
finding and use the source-selection conversation below; do not try
to repair it as Harbor merely because Harbor rejected it. A schema failure alone
does not identify its format.

For an empty scan, explain the absence and possible source material without
adding “readiness remains unproven.” Actual validation failures still need their
explanation and next action. For example:

> I didn't find Harbor evals in the locations I checked. Do you already have
> evals in any form, such as tests, scripts, a dataset, a notebook, or a manual
> checklist? Can you point me to them?

If the user already supplied evals or said they have none, use that answer instead
of asking again. If inspection found possible eval files, mention their concrete
paths as candidates, without claiming they are a validated suite. Do not label
ordinary software tests as agent evals without inspecting what they exercise.
Inspection alone does not settle whether the user wants to use those files.
When candidates were found but the user has not identified them as their evals,
briefly explain what makes them look useful. The finding and question could be:

> I didn't find Harbor evals in the locations I checked, but I did find reports
> with example conversations and descriptions of what a good answer should look
> like. Those could give us a useful starting point.
>
> Let's confirm we're using the right material. Are these your
> existing evals, or do you keep them somewhere else?

Use actual source descriptions and links. If no candidate material was found,
use the open question above. Source selection must precede choosing a case, bulk
extraction, or task creation; candidate files alone do not settle that choice.
Reuse an explicitly supplied source or earlier selection.

Save discovery before handing off, even when Harbor is unavailable. Return the
selected source, confirmed absence, or unresolved location to the core's **Route
after the evaluation starting point** section, carrying any established Ethos
and prior setup findings. The shared milestone
procedure owns the next conversation. The summary formatter supplies the default
empty-scan question; adapt it to the selected source while retaining the saved
report's original diagnostics and JSON.

For example, when Docker preflight fails and host access has not been verified:

> This repo has Harbor evals, but I could not verify readiness because the Docker preflight check failed.
>
> Check Docker access from this session, then rerun discovery with the necessary permission.
>
> Details are saved in `.eval-author/discovery.md`.


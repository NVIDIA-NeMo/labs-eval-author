<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Generated suite review and rerun handoff

Exercise the authoring skills in an isolated synthetic repository. Inspect saved
artifacts and provider-resolved selections; matching skill wording does not
establish that the handoff works. Do not use model credentials or start container
jobs for these documentation checks.

## Review at creation and after saved runs

Exercise case authoring with synthetic inputs and stop before execution. Without
asking separately for a review guide, inspect the generated suite-root README
and the authoring reply. The reply must link the guide, and its inventory must
make every authored case reviewable: purpose, input, expected outcome, grading
criteria, and links to the task and verifier details. Cases must be visible as
not run. Read the input and grading summaries without formatting JSONL or
reconstructing the conversation. Source evidence, when present, must be labeled
as the basis for the case, not as a successful execution of it.

Then supply saved synthetic artifacts for a successful control, a failed
actual-agent attempt, and an attempt with no retained trace. Request a run-result
handoff using these artifacts without executing evaluations. The same README
must refresh its evidence links and observed status, distinguish controls from
agent attempts, and explicitly identify missing traces. Follow every linked
artifact from the README's stated directory. Any viewer command must match the
available runtime and point to the intended artifacts; unavailable viewers need
an explicit limitation and direct artifact links. The reply must link the guide
without implying that this documentation exercise executed a real agent.

## Returning to a Harbor starter suite

Prepare two authored tasks, `refund-policy` and `refund-reject`, plus an unrelated
draft in the same parent. Save `first-eval.yaml` with explicit `tasks` entries for
only the two selected cases, a real-agent configuration, nondefault model
settings, per-task overrides, and two attempts per case. Record fixture setup,
credential variable names, and result locations in local documents. Map one
coverage requirement to both tasks and a second requirement to only
`refund-reject`. Include a fixed original job name to expose output collisions.

**Request:** “Finish this suite's handoff so I can rerun all cases or one coverage
item on a later visit. Do not run model evaluations.”

Inspect `.eval-author/README.md` and follow it from the documented directory
without the prior conversation. Confirm that:

- The case inventory contains the two selected cases and their review details,
  keeps the unrelated draft outside this suite, and links their available
  evidence separately from controls and source material.
- Setup names the actual runtime, activation/install procedure, backend,
  credentials without values, and state reset requirements.
- The full-suite command resolves to exactly the two intended tasks.
- The individual-item examples preserve both tasks for the shared requirement
  and select only `refund-reject` for the narrower one. Any saved subset configs
  retain the selected task entries and agent, model, environment, verifier,
  attempts, and task-specific overrides.
- No command runs every draft by accident, uses an unsupported coverage-ID
  filter, or substitutes NOP/Oracle for the actual agent evaluation.
- A new invocation writes to a fresh output path despite the original config's
  fixed job name. Result instructions locate per-case rewards and exceptions.
- The final handoff links the saved guide and distinguishes configuration
  inspection from execution evidence.

Use the installed Harbor schema and, where supported, `--print-config` to inspect
the documented commands without launching evaluations. Resolve local datasets
when needed; merely printing a dataset path does not prove the selected tasks.

Repeat with missing agent credentials or an unavailable adapter. The README must
still exist and give the known setup and case mapping, but clearly identify
which commands remain blocked or unverified. The case review information must
remain usable before execution. It must not claim a completed run.

## Gym and trace-derived suites

For Gym, supply an existing draft with a model composition, `reproducibility.md`,
and JSONL rows containing both model input and verifier metadata. Request the
same handoff. Follow the draft-root `README.md`: full and subset runs must use
the selected Gym runtime and composition, retain verifier fields and row order,
document server startup for `--no-serve`, reset state, and use fresh outputs.
No Harbor-only selection or control flags may appear as Gym commands.
Also exercise the creation and saved-run review checks above: each selected row
must have a readable input, expected outcome, and grading summary, with its
dataset locator and links to available native evidence. Verifier metadata must
not be presented as part of the model's input. Passing native controls must stay
distinct from actual-agent attempts.

For a trace candidate, check `<task-dir>/README.md` alongside the existing
`task/README.md`. Controls must be labeled as controls, with missing real-agent
configuration visible. The root guide must summarize the generated case and
link the source evidence separately from validation and actual-agent evidence.
For a batch containing a candidate, an unproven task,
and a no-candidate member, inspect the collection guide: all members and statuses
remain visible, and executable selections point to actual task directories.
Follow its case review links without opening raw trace JSON; a no-candidate
member must not be presented as an authored or passing case.

For requested publication, inspect the preview and exported root README, then
follow its paths from the export without access to the private source workspace.
No private report or unexported config may be required. Changing the README after
review must invalidate the publication attestation. Existing task README
content and its uppercase filename must survive; there must be no case-only
filename pair in one directory. For a standalone draft, verify that rerun
and case review sections extend the existing task-level `README.md` without
renaming it.

Retain the generated guides, configs, resolved selections, and any observed
failure as evidence. One successful exercise is a bounded check, not a claim
that all future authoring runs will produce correct documentation.

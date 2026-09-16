<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Proposal records

The skill authors semantic findings after reviewing the aggregate report, per-run
measurement details/judgments, traces, and existing tasks. The deterministic
`propose` command validates and routes those findings; it does not diagnose trace
text or turn every `missing` judgment into an observed failure. Keep the original
coverage report unchanged. Do not commit customer evidence into the skill repo.

Write a JSON object with a `findings` list. List findings in priority order; several
proposals may target the same item. Each finding has:

| Field | Meaning |
|---|---|
| `id` | Unique lowercase hyphenated proposal slug |
| `name`, `kind` | Exact audit target and `tool`, `capability`, or `failure_case`; retain the real kind |
| `basis` | `observed_failure`, `absent_scenario` in the inspected scope, or `insufficient_evidence` |
| `action` | `new_scenario`, `strengthen_existing`, `retain_regression`, `gather_evidence`, or `define_behavior` |
| `scenario` | Concrete request/fixture change or exercised scenario |
| `expected_behavior` | Ethos-backed outcome, or null when undefined |
| `verifier` | How to distinguish the intended outcome from wrong outcomes, or null pending design |
| `evidence` | References to reviewed tasks, fixtures, run/trace steps, judgments, and verifier results; empty when missing |
| `existing_task` | Original task directory for a revision; the scaffold checks it exists and never writes inside it |
| `source_changes_required` | Boolean, default false; true defers implementation until separately authorized integration is resolved |
| `trigger` | Required for failure cases, and for any capability whose outcome depends on a failure trigger |

A trigger object carries `description`, `status` (`observed`, `proposed`, or
`unverified`), `evidence` (references to that exact trigger), and `verification`
(how the new eval will establish it). Proposed triggers can support new task
design, but do not prove observed failures or coverage. Observed-failure claims
require observed trigger evidence when a trigger applies. The script checks
presence, not semantic correspondence: inspect the cited evidence before using
it. A route lookup error cannot establish rejection of a reservation.

For a capability marked covered in the aggregate, the report's `input_reports`
provides its kind. The reviewed finding must still cite the failing run, not only
the aggregate. Unreviewed uncovered items become explicit `gather_evidence`
proposals, preserving the measurement reason. This avoids guessing whether an
uncovered item is an absent scenario, incorrect behavior, or missing evidence.

Example (illustrative fixture and references, not shipped customer evidence):

```json
{
  "findings": [
    {
      "id": "offsite-communication",
      "name": "accurate_user_communication",
      "kind": "capability",
      "basis": "observed_failure",
      "action": "strengthen_existing",
      "existing_task": ".eval-author/task-drafts/offsite",
      "scenario": "Keep the workshop/dinner fixture; check the explanation against the accepted reservation.",
      "expected_behavior": "Describe minute 900 as 15:00 or 3:00 PM, with consistent duration and price claims.",
      "verifier": "Preserve feasibility grading; add a communication metric. Replay a six-hour shift as a negative control and equivalent correct time phrasing as positive controls.",
      "evidence": ["offsite run A: accepted submission and final explanation", "offsite verifier: grades itinerary only"]
    }
  ]
}
```

Run `propose --report <aggregate.json> --findings <findings.json>` and save stdout
as `.eval-author/proposals/dataset-proposals.json`. It defaults to `proposal-only`.
Only add `--scope implement` when the user has requested implementation. This
records conversation scope, not new permission for model calls or source edits.
`select --report <aggregate.json> --proposals <dataset-proposals.json>` returns
all eligible and deferred proposals, including their blockers. A valid proposal
stage can have zero implementation-ready entries. Missing behavior remains a
`define_behavior` action, not a failed proposal stage.

For supported continuation, pass the same `--proposals` file to `scaffold` and
`verify`, with proposal `id` as `--target`. The report digest must still match;
changed audit evidence requires renewed review. Derived eligibility and paths
are recomputed rather than trusted from saved JSON. Proposal-only manifests
cannot scaffold. The old tool-gap commands remain available without this flag.

`strengthen_existing` uses a fresh Harbor skeleton at the new draft path. Port
only relevant environment/fixture/grader logic, retaining the original metrics
and provenance in the draft README. Do not copy a whole task with potentially
obsolete metadata. Compare the original and draft before handoff. The script
never overwrites an existing output directory. Adopting a draft into an existing
suite or changing customer source requires the appropriate explicit scope.

`verify --proposals` requires two distinct single-run reports for the selected
draft's task ID and the target's measurement method (`tool_calls`, `capabilities`,
or `failure_cases`). Generate these with the audit tools and trace-bound judgments;
a JSON flag is not a substitute for evidence. Report task controls, agent rewards,
and `coverage_closed` independently. A correct regression remains useful when
an agent fails it. Stop after the planned two runs and diagnose; do not weaken
grading or retry until a favorable score appears.

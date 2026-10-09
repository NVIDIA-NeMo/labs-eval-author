---
name: eval-author-audit
description: >-
  Use when auditing eval coverage against Ethos: define and validate audit.md,
  measure selected ATIF traces, and report evidence gaps.
triggers:
  - audit my existing evals
  - generate audit.md from ETHOS.md
  - validate audit.md coverage schema
  - measure audit.md coverage against a harbor trace
  - aggregate audit.md coverage reports
  - check audit.md coverage denominator
  - what should my evals cover from the agent ethos
  - review the audit coverage denominator
  - audit coverage of my evals against the ethos
not-for:
  - eval-author (use for the standard, the boundaries, and to pick a sub-flow)
  - eval-author-discover (use to check Gym or Harbor suite readiness)
  - eval-author-inspect-trace (use after eval-author selects an Intake trace)
  - nemo-experimentalist (use to optimize an agent from Insights or explicit datasets)
compatibility: >-
  Python 3.11 or later for generation and validation; Python 3.12 or later for
  ATIF measurement via Harbor's trajectory model. Dependencies are listed in requirements.txt.
  Generation, validation, measurement, and aggregation read local files only;
  they do not start Harbor jobs or call platform services.
maturity: alpha
license: Apache-2.0
user-invocable: true
allowed-tools: Bash Read Write Grep Glob
---
<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eval Author: audit

## Purpose

Read `eval-author` for the shared standard, vocabulary, and boundaries. This
sub-flow generates and validates a finite coverage denominator from `<ethos_path>` and
reviewed audit items, then can measure ATIF traces and aggregate coverage reports
against it. It also writes a human-readable `audit-coverage-report.md` and reviews
the findings with the user. It does not generate tasks yet.

## Start a guided audit

For a fresh full audit, the first deliverable is a turn-ending opening (`final`
when available). Explain that the audit compares intended behavior with evaluation
evidence, then show these five literal unchecked checkboxes, retaining each label
and description and marking **Understand your agent** as **We're here**:

- [ ] **Understand your agent** — agree on what your agent should do, what it should avoid, and what a good result looks like.
- [ ] **Confirm evals and traces** — confirm which evaluations to audit and locate traces (records of agent runs) so we can check what the evaluations actually exercised.
- [ ] **Define what the evals should cover** — agree on the behaviors, tools, and failure cases to check.
- [ ] **Measure coverage** — use the run records to see which of those items were exercised.
- [ ] **Generate and review coverage report** — create or update `audit-coverage-report.md`, then review coverage, gaps, evidence limits, and next steps together.

End with **“Ready to get started?”** and wait. Before acceptance, do no repository
work: no Ethos checks or writes, eval/trace inspection, runtime probes, progress
writes, or delegation. Do not batch them with skill loading. Existing Ethos,
supplied paths, or permission to audit do not answer this checkpoint; keep it
pending in the conversation, not an asynchronous question followed by more work.

After acceptance, read [Guided audit milestones](references/guided-audit.md) and
begin **Understand your agent**. The reference owns completion criteria,
turn-ending milestone check-ins, missing inputs, and resumption. Acceptance of
the opening starts that milestone; it does not approve later transitions. Known
inputs do not answer check-ins. End all independent work and delegation while a
checkpoint awaits its answer. Reuse answered checkpoints and resume the earliest
unfinished, non-deferred milestone, preserving agreed deferrals. The core's
authoring welcome and Harbor setup are not audit prerequisites.

Use directly named non-trace inputs and saved progress for orientation. Before
any trace search or read, including tool-name inspection, follow
[Confirm evals and traces](references/guided-audit.md#2-confirm-evals-and-traces).
A user-selected source and location already supplied in this conversation suffice;
a path found in a file does not. Until selection, do not list or recursively
search the whole workspace where traces could be exposed. Confirmed absence
needs no search to prove it.

Scoped generate, validate, measure, or aggregate requests keep their scope without
the full checklist. Generation still needs Ethos pre-flight; existing-spec
validation, measurement, and aggregation use supplied inputs without a new Ethos
interview. The trace-source rule still applies.

## Ethos Pre-flight

Use this procedure within **Understand your agent** after the guided opening is
accepted, or for a scoped generation request. Carry selected eval paths,
user-confirmed evidence locations, and prior findings forward. Reuse established
Ethos and review state. Merely loading this reference does not start the Ethos
milestone; for a fresh guided audit, return the opening first and wait for its
answer before any checks, including checks of an existing Ethos.

Before drafting audit items or generating `audit.md`, require the selected agent's
established Ethos to define what the audit should cover. An explicit
`--ethos <path>` overrides any prior handoff path; otherwise pass the established
path supplied by first-eval when available.

For a full audit, explain what `ETHOS.md` is and how this audit uses it before
checking or creating it. Include that explanation in the first Ethos check-in,
even when requesting format repairs. Follow [Understand your agent](references/guided-audit.md#1-understand-your-agent)
to link the document and documentation, summarize its intent, and offer edits.

Follow [Local Ethos](../eval-author/references/local-ethos.md) to locate, check,
reuse, or create and review the document. That procedure owns the document
prerequisite and its recovery. Use its exact returned path as `<ethos_path>` and
resume audit-item drafting only after the prerequisite is complete. For a full
audit, check in before **Confirm evals and traces**. In that next milestone,
show and confirm the evaluation suites with the user before asking about traces.

## Coverage specification

The audit-spec approach has three item kinds in v1:

| Kind | Meaning |
|---|---|
| `tool` | A canonical tool name the agent may call |
| `capability` | A high-level behavior the agent should exercise |
| `failure_case` | Expected safe behavior when a capability cannot proceed normally |

Every item uses `name` as its stable coverage key. Names must be unique across
the whole file; do not add sequential numeric IDs. Tool references in
`required_tools`, `expected_tools`, and `evidence_required[].tool` must match the
`name` of a declared `tool` item. `prohibited_tools` may name any syntactically
valid tool name, including tools the agent must never call and therefore should
not declare as allowed tools.

Write audit artifacts under `.eval-author/`. Audit operations do not edit the
customer's source, existing evals, source-of-truth documents, or `ETHOS.md`;
prerequisite Ethos work belongs to the shared procedure in the pre-flight above.

## Audit outputs

Use these names in replies and artifact links; follow [artifact naming](references/coverage-report.md#artifact-names).

| Name | File under `.eval-author/` | Purpose |
|---|---|---|
| Audit specification | `audit.md` | Structured source of checks and required evidence, reviewed through the report's Intended coverage section |
| Audit coverage report | `audit-coverage-report.md` | Readable intended coverage, test mappings, measured coverage, gaps, evidence limits, and next actions |
| Coverage measurements (JSON) | `audit-coverage-report.json` | Script-generated measurements aggregated over the selected runs, when available |
| Audit progress | `audit-progress.md` | Conversation checkpoints and resumption |

For a full audit, create the Audit coverage report with the validated Audit
specification, refresh it after measurement, and update it for final review.
Follow the [report guidance](references/coverage-report.md) and [template](templates/audit-coverage-report.md) even when measurement is deferred.

Whenever the Markdown report is created or updated, explicitly say so and link
it in the turn-ending response, including intermediate milestone check-ins.

Focused operations need this report only when requested or continuing a full
audit; keep their scope. Read-only and `suggest` requests remain read-only.

## Scripts

Audit-spec mechanics live under `scripts/audit_spec/`:

Read `scripts/audit_spec/README.md` for the current measurement assumptions:
ATIF input, Harbor trajectory parsing, v1 `tool_calls`, `capabilities`, and
`failure_cases` coverage, and coverage aggregation from `coverage.json` files.

| Script | Use it to |
|---|---|
| `scripts/audit_spec/generate.py` | Create, reconcile, replace, or preview `.eval-author/audit.md` from `ETHOS.md` and reviewed item proposals |
| `scripts/audit_spec/measure.py` | Measure one ATIF trace or Harbor trial directory against `audit.md` and write coverage/details files for each selected method |
| `scripts/audit_spec/report.py` | Aggregate per-trace `coverage.json` files into one coverage report with uncovered audit items |
| `scripts/audit_spec/validate.py` | Validate the marked audit-spec block in `audit.md` |

Shared helpers, measurement method contracts, schemas, and examples are
documented in `scripts/audit_spec/README.md`.
Runtime dependencies are listed in `requirements.txt`.

## Step 1: Draft Or Update Audit Items

Before drafting or updating `.eval-author/audit-items.yaml`, read
`templates/audit.md` and `schemas/audit.schema.json`. Use the template as the
worked example and the JSON Schema descriptions as the field definitions. Do not
use validation as the primary way to discover the format; validation is the
enforcement and repair step after drafting.

Read `<ethos_path>` and draft audit items at the level between Ethos and runnable
tasks: canonical tools, high-level capabilities, and material failure cases. Keep
the list finite. Do not create separate items for prompt paraphrases, fixture
variants, or ordinary happy-path permutations.

For `tool` items, use the names that appear in the actual runtime traces or tool
registry, including eval-specific tools that may be more precise than product
tools named in Ethos prose. If Ethos describes a generic tool such as `sqlite`
but measurement traces expose `execute_sql` and `submit_sql`, declare the
runtime tool names and connect capabilities or failure cases to those names.
Do not invent tool names that will not appear in the measurement surface.
Read traces for this purpose only after user confirmation of their source and
location. Without usable traces, use an authoritative tool registry or agent
configuration; keep unresolved names as open questions rather than inventing
tool items. Explain any resulting limits on the proposed specification.

Save the reviewed item proposals as `.eval-author/audit-items.yaml`. The items
file may be either a mapping with an `items` key or the item list itself. It
should use the same item shape shown in `templates/audit.md` and enforced by
`schemas/audit.schema.json`.

For an initial audit, this file should contain the full proposed denominator. For
an update, it may contain only the proposed additions or edits. Existing reviewed
`audit.md` items remain the source of truth in reconcile mode.

Capabilities that do not need tools, such as policy refusals or out-of-scope
handling, should use `required_tools: []`. Failure cases attach to capability
names through `applies_to`; tool-level failure expectations stay on the tool item
as `expected_failure_behavior`.

For failure cases, make the trigger and safe response explicit in
`evidence_required`. Include prohibited output classes in an `output` evidence
description when their absence must gate coverage. Measurement uses
`prohibited_tools` as a deterministic gate; `applies_to`, `expected_tools`,
`trigger`, `expected_behavior`, and `prohibited_outputs` otherwise provide the
rubric and authoring context rather than separate hidden checks.

## Step 2: Generate Or Reconcile Audit.md

Generate from `<ethos_path>` and reviewed item proposals:

```bash
uv run --with pyyaml --with jsonschema \
  <skill_dir>/scripts/audit_spec/generate.py \
  --ethos <ethos_path> \
  --items .eval-author/audit-items.yaml \
  --out .eval-author/audit.md
```

The default `--mode reconcile` creates a missing file or updates the existing
marked block. It refreshes source metadata, preserves reviewed item bodies by
stable `name` and prose outside the block, appends new items, and reports proposed
edits without applying them. Choose other modes only for the requested scope:

| Option added to the command | Behavior |
|---|---|
| `--mode suggest` | Same comparison as reconcile; writes nothing |
| `--items-mode full` | Treat proposals as the complete denominator; report omitted existing items as `possibly_stale_items` |
| `--mode replace` | Rewrite the whole file, including outside prose; only when the user wants to discard the existing generated file |

Without `--items-mode full`, proposals are partial: omitted existing items are
not stale. Inspect the JSON summary's `written`, `added_items`,
`conflicting_items`, `conflicting_items_applied`, and `possibly_stale_items`.
Reconcile preserves conflicting reviewed items and returns
`conflicting_items_applied: false`; accepted changes need manual editing or a
future editor. Additions, conflicts, stale items in full mode, or an agent-name
change demote an approved audit to `status: draft` unless explicitly overridden
with `--status approved`.

The generator records an Ethos `sources` entry with `name: ethos`, a path
relative to `audit.md`, and a real `sha256` digest. Without `--agent`, it infers
the name from Ethos frontmatter; if that differs from an existing audit, reconcile
preserves the reviewed name and reports `agent_change`. Explicit `--agent`
overrides it. `source_refs` remain advisory provenance: v1 preserves them but
does not resolve them against `sources`.

## Step 3: Validate

Run validation after every generated or hand-edited audit file:

```bash
uv run --with pyyaml --with jsonschema \
  <skill_dir>/scripts/audit_spec/validate.py --audit .eval-author/audit.md
```

`schemas/audit.schema.json` is the canonical structural schema. The Python
validator applies that schema first, then checks any source digests that are
provided and cross-item references such as `required_tools` and `applies_to`.

Validation proves only structure and references, not that the denominator is
complete or correct.

## Step 4: Measure One ATIF Trace

After validation and, for a guided audit, specification review, measure one
completed trial or ATIF file from the user-confirmed source. If it is missing or
unusable, follow the guided audit's unavailable-evidence guidance; do not search
another source without user selection. Read the measurement assumptions and
method contracts in [the script README](scripts/audit_spec/README.md).

```bash
uv run --with-requirements <skill_dir>/requirements.txt \
  <skill_dir>/scripts/audit_spec/measure.py \
  --audit .eval-author/audit.md \
  --trial-dir <harbor-job-dir>/<trial-dir> \
  --measure tool_calls \
  --out-dir .eval-author/audit-measurements
```

`--trial-dir` expects `agent/trajectory.json`, which not every agent emits.
For a known ATIF file, replace it with `--trace <path-to>/trajectory.json
--task-id <task-id> --run-id <run-id>`. The default method is `tool_calls`;
`--measure` accepts repeated flags or CSV such as
`tool_calls,capabilities,failure_cases`. Select the other methods when those
item kinds should be measured. The trace is parsed once for all methods;
unknown methods fail before loading it.

For non-tool `evidence_required` (such as `user_intent`, `output`, `outcome`,
`policy_boundary`, or `verifier`), inspect the selected trace and write judgment
sidecars under `.eval-author/`:

| Method | Schema | Additional measurement argument |
|---|---|---|
| `capabilities` | `schemas/audit_capability_judgments.schema.json` | `--capability-judgments .eval-author/capability-judgments.json` |
| `failure_cases` | `schemas/audit_failure_case_judgments.schema.json` | `--failure-case-judgments .eval-author/failure-case-judgments.json` |

Target each judgment by item `name` and zero-based evidence index; copy its
`kind` and `description` exactly. Set `trace_sha256` to `sha256:` plus the
lowercase digest of the exact inspected ATIF bytes. Judge only non-tool evidence:
`satisfied` requires clear demonstration, `missing` clear absence, and `unclear`
ambiguous or insufficient evidence. Include rationale and trace references.
Use capability descriptions or failure triggers, expected behavior, and
prohibited outputs as rubric context; judge what `evidence_required` states.

Coverage is conjunctive: all deterministic and judged requirements must hold.
Judgments cannot override missing required tools or `tool_call` evidence;
failure cases also require every `prohibited_tools` value to be absent from the
whole trace. Missing judgments leave items uncovered. Stale trace digests or
evidence targets fail before report writes; never relabel stale evidence.

Each task/run/method writes schema-validated `coverage.json` and `details.json`
under `.eval-author/audit-measurements/task=<encoded-task-id>/run=<encoded-run-id>/<method>/`.
IDs are encoded as single path components. The script README defines coverage
identity fields and method-specific details. Aggregate coverage files, not debug
details, in the next step.

## Step 5: Aggregate Coverage Reports

After measuring one or more traces, aggregate the per-trace `coverage.json`
files into a coverage report. For a guided audit, include only measurements from
the selected trace set, using explicit `--coverage` files or a dedicated directory.
The directory example below assumes it contains only the intended measurements:

```bash
uv run --with-requirements <skill_dir>/requirements.txt \
  <skill_dir>/scripts/audit_spec/report.py \
  --audit .eval-author/audit.md \
  --coverage-dir .eval-author/audit-measurements \
  --out .eval-author/audit-coverage-report.json
```

Use `--coverage <path-to-coverage.json>` for explicit files, or repeat
`--coverage-dir` and `--coverage` when the inputs are split across directories.
The script scans coverage directories recursively for files named
`coverage.json`, validates every input against
`schemas/audit_coverage.schema.json`, and rejects inputs whose audit metadata no
longer matches the current `audit.md`. A status-only mismatch, such as
measurements produced while the audit was `draft` and aggregated after it became
`approved`, is reported as a warning instead of forcing a re-measure.

The aggregate report uses `schemas/audit_coverage_report.schema.json`. It
contains overall and per-kind count summaries, the union of covered item names,
warnings, the measured item kinds, and `uncovered_items`. Each uncovered item
includes the original audit item plus generation-oriented context: a stable
`reason`, a one-sentence `focus`, likely `needed_tools`, and the item's
`evidence_required`.
Use `reason: not_measured_by_any_method` to distinguish gaps that no included
measurement method could close from `reason: not_covered_by_any_input_report`,
which means the item kind was measured but no input report covered that item.
Treat that list as evidence for the proposal step in `eval-author-task-create`.
The aggregate report unions coverage; it does not establish why an item is
uncovered or whether an existing task already exposes an agent failure.

## Next Steps

- For audit-generation inputs and reconciliation modes, return to
  [Step 2: Generate Or Reconcile Audit.md](#step-2-generate-or-reconcile-auditmd).
- After the report review, offer new or improved eval task proposals using the
  [guided handoff](references/guided-audit.md#after-review-offer-the-next-step).
  End the turn and wait for acceptance before entering the proposal step in
  [`eval-author-task-create`](../eval-author-task-create/SKILL.md) with the current
  report and evidence. Proposal acceptance does not authorize task execution.
- The proposal step considers tools, capabilities, and failure cases. Automatic
  task creation still accepts only uncovered tool items with
  `reason: not_covered_by_any_input_report`. Items with
  `reason: not_measured_by_any_method` remain unmeasured, even when the proposal
  step suggests a candidate scenario for them.

## Prerequisites

Establish Ethos and review audit items first. Generation/validation need Python
3.11+, PyYAML, and jsonschema. Measurement needs Python 3.12+ and Harbor's
trajectory model; use `requirements.txt`. Commands read local files, not services.

## Limitations

Validation proves structure, not denominator completeness. Coverage applies
only to supplied traces and selected methods; missing judgments leave items
uncovered. It does not establish task quality, agent correctness, or absent scenarios.

## Troubleshooting

- Invalid tool or capability reference: match the declared stable `name`, repair
  the audit item, and rerun `validate.py` before measurement.
- Missing or invalid ATIF: obtain the original trajectory or a supported
  conversion; a reward alone cannot substitute for interaction evidence.
- Stale judgment digest or target: inspect the current trace and evidence
  requirement, regenerate the judgment, and remeasure; never relabel old evidence.
- Aggregate metadata mismatch: remeasure against the current audit. A status-only
  draft-to-approved change is a warning, not a reason to rewrite coverage JSON.

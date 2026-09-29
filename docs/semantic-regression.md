<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Semantic regression pilot

The advisory **Semantic regression** workflow measures retained findings and
run-to-run consistency in narrative reports over frozen evidence. The initial
suite covers audit interpretation and trace-proof limitations. It supplies the
listed skill Markdown files as context to a stateless model call, with no tools.
It does not evaluate full skill execution, task correctness, coverage arithmetic,
or environment fidelity. Existing deterministic tests and Tier 2/3 remain separate.

Ratchet (`semantic-regression-tests`, tested with version 3.3.0) supplies the
claim prompts, clustering helpers, calibration, self-test and two-mode gate.
Its source is provisioned separately; it is not redistributed in this repository.
The adapter was verified against source revision
`59fd412e69fe734e34c9caa2d47ffc70dc5e2108`.

## Prepare a reviewed baseline

Use a private directory outside Git. Copy `evals/semantic/pilot.json` into it and
replace the three placeholder model IDs with immutable provider deployment/version
identifiers. The pilot proposes ten independent runs per case. The same run count
is required for candidate consistency checks. Budget for roughly two model calls
per run plus clustering and retention matching; calls have 120-second timeouts
and 8,192 output-token limits, with no automatic retries. These are work bounds,
not a monetary budget. The suite accepts 5–20 runs and at most ten cases.

Set `INFERENCE_HUB_API_KEY`. The default endpoint is the existing Inference Hub
chat-completions endpoint; local execution may set `SEMANTIC_API_URL` to a compatible
HTTPS endpoint. Give `--runtime` the complete Ratchet skill directory.

```bash
python tools/semantic_regression.py --mode calibrate \
  --suite /private/semantic/suite.json --runtime /private/ratchet \
  --output /private/calibration
```

Calibration writes a private packet per case: raw reports, claim extractions,
cluster mapping, proposed baseline and a digest-bound receipt. It runs Ratchet's
damage self-test. Its summary remains incomplete (`awaiting_baseline_review`),
with exit 2: a proposal is not a locked baseline. Inspect each mapping and its
source evidence for erroneous claims or merges. Preserve uncertainty, negation,
and the distinction between uncovered and unmeasured. Only after accepting the
mapping, take its SHA-256 and explicitly lock that packet:

```bash
sha256sum /private/calibration/audit-evidence-boundaries/mapping.md
python tools/semantic_regression.py --mode lock \
  --packet /private/calibration/audit-evidence-boundaries \
  --reviewed-mapping-sha256 REVIEWED_SHA256 --runtime /private/ratchet \
  --output /private/semantic/baselines/audit-evidence-boundaries
```

Repeat for each case. Add `"baseline": "baselines/CASE/lock.json"` to each suite
case. The lock refuses an existing output directory, changed packet, changed
runtime or failed damage self-test. The supplied mapping hash records the
operator's review attestation; it is not a cryptographic reviewer identity.
A new baseline is a deliberate reviewed replacement, never a side effect of CI.
Test candidate revisions against the old lock before accepting changed behavior.

```bash
python tools/semantic_regression.py --mode check \
  --suite /private/semantic/suite.json --runtime /private/ratchet \
  --output /private/candidate-check
```

Inputs, N, extractor/judge IDs, runtime and measurement adapter digests bind the
comparison. Skill content and author model may change: those are the subjects
under test. Changes to the measurement adapter require a new reviewed calibration;
do not compare different measurement systems as one trend. Retention always uses
`r1`, selected before execution. Empty reports remain in the denominator. Invalid
JSON, dropped/duplicated matches, provider failures, weak gates and missing baselines
cannot produce an unqualified pass. Exit codes: 0 measured pass, 1 regression,
2 incomplete evidence. Public reports contain identifiers and aggregate metrics,
never raw claims, prompts, responses or provider diagnostics.

## Enable CI

Prepare a ZIP with `suite.json`, `baselines/CASE/{lock,baseline}.json`, and the
complete Ratchet directory at `ratchet/`. Exclude caches and private files not
needed for this run. Store it in approved private storage with an HTTPS download
URL. Record its SHA-256. The reviewed archive is executable trusted input: it
contains Ratchet Python code. Do not accept an unreviewed bundle or floating hash.

In the existing protected `skill-evaluator` environment configure:

- secret `SEMANTIC_BUNDLE_URL`: private HTTPS download URL (a signed URL is supported);
- variable `SEMANTIC_BUNDLE_SHA256`: exact archive hash;
- existing secret `INFERENCE_HUB_API_KEY`;
- repository variable `SEMANTIC_REGRESSION_ENABLED=true` after baseline review.

Retain the existing main-only environment approval protections. PRs run only the
credential-free pilot plan. Enabled pushes to main and explicitly requested
manual main runs compare against the supplied locks. CI never calibrates or locks.
The live job is advisory and retains JSON/Markdown summaries for 30 days even
when comparison fails. If provisioning fails, the fallback report is explicitly
plan-only and has no measurements. A killed job may have only a checkpoint report
or no artifact; neither is a pass. Raw run evidence is local to the runner and is
not uploaded from this public repository. Reproduce locally in private storage
when detailed diagnosis is needed.

The fixtures dashboard consumes `semantic-regression-RUN-ATTEMPT`, validates the
source workflow, main branch, commit, run and attempt, and imports only aggregate
fields. The report schema is `nemo.eval_author.semantic_regression.v1`; its scope
is `frozen-evidence-narrative-v1`. No measured baseline or dashboard scores are
shipped with this integration.

<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Offline support-response evaluations

This repository has an existing Python evaluation suite; it does not use Harbor.
The suite grades stored structured support-agent responses. It checks a refund
eligibility decision for a purchase within 30 days and a request for information
when the purchase date is missing.

From this repository root, run:

```bash
python3 scripts/run_evals.py --cases evals/cases.jsonl --responses evals/responses.jsonl --output results.json
```

The runner uses only Python 3.11+ standard-library modules. It needs no Harbor,
Docker, API key, network access, or model credentials. `evals/cases.jsonl` contains
the cases and expected structured behavior; `evals/responses.jsonl` contains
synthetic recorded responses with matching IDs. Replace the responses file to
evaluate another recorded set. This command does not call the live support agent.

A run writes per-case results and the pass count to `results.json`, and records
that execution occurred in `.suite-was-run` at the repository root. Exit status
0 means every case passed; 1 means at least one failed; invalid inputs produce a
nonzero error. The runner checks missing and duplicate response IDs explicitly.

The checks compare decisions and required missing fields; they do not grade
natural-language explanation quality or real payment operations. No completed
run result is included in this checkout.

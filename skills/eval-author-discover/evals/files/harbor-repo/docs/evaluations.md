<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Evaluation guide

Run each command from the repository root, the directory containing the top-level
`README.md` and `evals/`. Use Harbor 0.20.0 and an accessible Docker backend. Image creation
may need access to the Python base image. The configurations select the `oracle`
agent and require no model credentials. A real model configuration would have
its own access requirements; none is configured here.

| Suite | Configuration | Dataset and behavior |
| --- | --- | --- |
| Refund eligibility | `evals/refund.json` | `evals/datasets/refund/`: determine that a purchase 18 days ago is eligible under the 30-day policy. |
| Missing purchase date | `evals/missing-date.json` | `evals/datasets/missing-date/`: ask for the absent purchase date and withhold a refund decision. |

Refund eligibility:

```bash
harbor job start -c evals/refund.json
```

Missing purchase date:

```bash
harbor job start -c evals/missing-date.json
```

Each configuration selects one task and one attempt. Results are written beneath
`jobs/refund/` or `jobs/missing-date/`, respectively. Inspect the trial verifier's
reward and any exception before interpreting a run.

The task verifiers check structured responses in `/app/response.json`; they do
not assess open-ended conversational quality or actual payment operations.
Finding these files and commands alone does not establish runtime readiness or
that a run has succeeded. No completed run results are included.

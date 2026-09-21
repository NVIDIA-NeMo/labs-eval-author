<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# refund-eligibility

Apply the documented 30-day refund policy to a dated request.

The environment supplies a synthetic request and the shop policy. The agent
writes `/app/response.json`. `tests/check_response.py` checks the declared
structured outcome and writes a reward of 1 for a correct response or 0
otherwise. A missing or invalid response receives 0. `solution/solve.sh` supplies
a reference solution to check with Harbor's Oracle.

The verifier covers this single fixture; it does not establish general policy
reasoning or natural-language quality. The task was scaffolded with Harbor 0.20.0.
Structure validation is separate from execution; no successful run is claimed.

From the repository root, use the documented `refund` suite command in
`docs/evaluations.md`. The task requires a Docker environment able to build the
provided Python image. It uses no inference credentials with the Oracle agent.

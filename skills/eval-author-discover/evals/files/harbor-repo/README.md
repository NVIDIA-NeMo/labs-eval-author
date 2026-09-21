<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Support agent

This local support agent explains the shop's refund policy. For a request made
within 30 calendar days of purchase, it should confirm eligibility. If the
purchase date is missing, it should ask for that date before deciding. It must
not promise a refund without enough information, invent a date, or change the
policy. Requests outside the stated policy should be referred to a human.

The intended users are customers asking about a single purchase. These examples
use synthetic requests; payment processing and customer-account access are not
part of this repository. No formal Ethos has been written yet.

The existing evaluations are Harbor tasks documented in
[the evaluation guide](docs/evaluations.md). They cover refund eligibility and
missing purchase dates. The checked-in configurations use Harbor's `oracle`
reference-solution agent for task sanity runs, not a production support agent.
Agent quality would need a separate real-agent configuration and run evidence.

A retained historical note is at `.eval-author/readiness-before.json`. It records
an earlier incomplete readiness check, not proof that these suites can run.

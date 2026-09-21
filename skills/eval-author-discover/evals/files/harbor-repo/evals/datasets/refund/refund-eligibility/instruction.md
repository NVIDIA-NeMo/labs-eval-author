<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Refund eligibility

Read `/app/request.json` and `/app/policy.md`. Decide whether this purchase is
eligible under the documented policy. Write `/app/response.json` with exactly
these fields: `decision` (`eligible` or `ineligible`), `days_since_purchase`
(an integer), and `reason` (`within_30_days` or `outside_30_days`). Do not perform
any payment operation. Dates use ISO 8601 calendar dates.

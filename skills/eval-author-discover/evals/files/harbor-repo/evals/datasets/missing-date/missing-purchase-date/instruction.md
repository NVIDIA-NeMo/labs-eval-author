<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Missing purchase date

Read `/app/request.json` and `/app/policy.md`. Reply to the customer without
inventing missing information or prematurely deciding refund eligibility.
Write `/app/response.json` with exactly these fields: `decision`
(`needs_information`, `eligible`, or `ineligible`), `missing_fields` (a list of
field names), and `message` (the question to ask the customer). Do not perform
any payment operation.

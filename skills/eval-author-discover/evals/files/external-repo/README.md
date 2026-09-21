<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Support agent source checkout

This agent handles refund-policy questions. Its behavioral evaluations live in
a separate checkout maintained at `../support-agent-private-evals` relative to
this repository. That checkout is not included here. The maintainers keep the
scenario dataset, grading rubric, and run instructions there; this repository
contains none of those files and does not document an evaluation command.

Use an accessible checkout of that evaluation repository to inspect its cases
and runner. The missing sibling directory does not establish that evaluations
have not been written. No Harbor setup or suite-readiness result is recorded in
this repository.

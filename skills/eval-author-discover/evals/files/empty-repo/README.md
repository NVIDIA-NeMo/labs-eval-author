<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Support agent starter

This project is preparing a support agent that answers questions about a shop's
30-day refund policy. It should ask for a missing purchase date rather than
inventing one. No agent evaluation suite, behavioral dataset, or grading rubric
has been created.

`support_utils.py` contains a text-normalization helper. Its unit tests in
`tests/test_support_utils.py` check only that helper; they do not invoke an agent,
assess a customer conversation, or grade a refund decision.

The helper tests can be run from this repository root with Python 3.11 or later:

```bash
python3 -m unittest discover -s tests
```

No third-party packages or credentials are required for those helper tests.

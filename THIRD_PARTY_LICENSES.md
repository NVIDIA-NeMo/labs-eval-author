<!-- SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Third-Party Software Licenses

This repository uses the dependencies listed below. Each package link identifies the exact
version resolved in `uv.lock`. Complete collected license and attribution texts are
preserved in [third_party/NOTICES.txt](third_party/NOTICES.txt), grouped by package and
version, with the original archive URLs, checksums, and file paths. SPDX expressions
are inventory metadata only; upstream texts retain their own terms and notices.
Shared standard license texts are also included under `third_party/license_texts/`.

The inventory covers runtime dependencies and all optional extras, including transitive
and platform-specific dependencies. Bundled JSON examples and synthetic test fixtures
are NVIDIA-authored and covered by the root [LICENSE](LICENSE).

Run `make update-licenses` after changing dependencies to collect texts automatically.
`make check-licenses` verifies the generated inventory and collected texts.
See DEVELOPMENT.md for collection scope and exception handling.

| Package | SPDX license expression | License and attribution documents |
| --- | --- | --- |
| [`attrs 26.1.0`](https://pypi.org/project/attrs/26.1.0/) | `MIT` | [NOTICES.txt](third_party/NOTICES.txt), [MIT.txt](third_party/license_texts/MIT.txt) |
| [`jsonschema 4.26.0`](https://pypi.org/project/jsonschema/4.26.0/) | `MIT` | [NOTICES.txt](third_party/NOTICES.txt), [MIT.txt](third_party/license_texts/MIT.txt) |
| [`jsonschema-specifications 2025.9.1`](https://pypi.org/project/jsonschema-specifications/2025.9.1/) | `MIT` | [NOTICES.txt](third_party/NOTICES.txt), [MIT.txt](third_party/license_texts/MIT.txt) |
| [`referencing 0.37.0`](https://pypi.org/project/referencing/0.37.0/) | `MIT` | [NOTICES.txt](third_party/NOTICES.txt), [MIT.txt](third_party/license_texts/MIT.txt) |
| [`rpds-py 2026.6.3`](https://pypi.org/project/rpds-py/2026.6.3/) | `MIT` | [NOTICES.txt](third_party/NOTICES.txt), [MIT.txt](third_party/license_texts/MIT.txt) |
| [`typing-extensions 4.16.0`](https://pypi.org/project/typing-extensions/4.16.0/) | `PSF-2.0` | [NOTICES.txt](third_party/NOTICES.txt), [PSF-2.0.txt](third_party/license_texts/PSF-2.0.txt) |

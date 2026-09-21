#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail
python3 - <<'PYTHON'
import json
from pathlib import Path
request = json.loads(Path('/app/request.json').read_text())
if 'purchase_date' in request:
    raise ValueError('This scenario expects a missing purchase date')
response = {
    'decision': 'needs_information',
    'missing_fields': ['purchase_date'],
    'message': 'What was the purchase date?',
}
Path('/app/response.json').write_text(json.dumps(response) + '\n')
PYTHON

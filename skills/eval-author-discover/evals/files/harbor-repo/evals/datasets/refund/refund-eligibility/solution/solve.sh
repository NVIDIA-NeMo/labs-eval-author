#!/usr/bin/env bash
# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail
python3 - <<'PYTHON'
import json
from datetime import date
from pathlib import Path
request = json.loads(Path('/app/request.json').read_text())
days = (date.fromisoformat(request['request_date']) - date.fromisoformat(request['purchase_date'])).days
eligible = 0 <= days <= 30
response = {
    'decision': 'eligible' if eligible else 'ineligible',
    'days_since_purchase': days,
    'reason': 'within_30_days' if eligible else 'outside_30_days',
}
Path('/app/response.json').write_text(json.dumps(response) + '\n')
PYTHON

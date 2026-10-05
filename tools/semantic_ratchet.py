# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Process-isolated adapter to the externally provisioned Ratchet runtime."""

import argparse
import contextlib
import importlib
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--retention", type=Path, required=True)
    parser.add_argument("--consistency", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.runtime / "scripts"))
    cli = importlib.import_module("cli")
    claimset = importlib.import_module("claimset")
    gate = importlib.import_module("gate")
    log = io.StringIO()
    with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            cli.check(
                SimpleNamespace(
                    baseline=str(args.baseline),
                    config=str(args.config),
                    retention_clusters=str(args.retention),
                    consistency_clusters=str(args.consistency),
                    accept_provenance_change=False,
                    accept_artifact_mismatch=False,
                    show_unmatched=False,
                )
            )
        except SystemExit as exc:
            code = exc.code
    report = {"exit_code": code, "metrics": None, "status": "incomplete"}
    if code in (0, 1):
        baseline = json.loads(args.baseline.read_text())
        retention, ids, _ = claimset.load_clusters(str(args.retention))
        consistency, _, _ = claimset.load_clusters(str(args.consistency))
        result = gate.run_gate(baseline, retention_run=retention[ids[0]], consistency_runs=consistency)
        r, c = result["retention"], result["consistency"]
        report["metrics"] = {
            "retention": r["core_recall"],
            "retention_threshold": r["th1"],
            "consistency": c["jac2"],
            "baseline_consistency": c["jac1"],
            "allowed_drop": c["th2"],
            "presence_passed": c["presence_ok"],
        }
        qualified = baseline["th1"] <= 0 or baseline["jac1"] - baseline["th2"] <= 0
        qualified |= baseline["th1"] < 1 / len(baseline["core_cluster_ids"])
        report["status"] = "regression" if code == 1 else "incomplete" if qualified else "passed"
    print(json.dumps(report, allow_nan=False))


if __name__ == "__main__":
    main()

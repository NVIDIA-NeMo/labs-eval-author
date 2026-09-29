# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Bounded narrative regression pilot; Ratchet is provisioned separately, never vendored.

calibrate produces a review packet; lock consumes an explicitly reviewed mapping
hash; check can only compare against a lock. CI invokes check, never lock.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "nemo.eval_author.semantic_regression.v1"
SCOPE = "frozen-evidence-narrative-v1"
DOMAIN = (
    "Preserve distinctions between uncovered, unmeasured, unsupported, rejected, and proven. "
    "Preserve negation, uncertainty, scope, and recommended actions. Do not normalize these away. "
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def load(path):
    return json.loads(path.read_text())


def digest(value):
    return sha(json.dumps(value, sort_keys=True, allow_nan=False).encode())


def tree_digest(root):
    return digest(
        {
            p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts and p.suffix in (".py", ".md")
        }
    )


def contained(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("invalid input path")
    return path


def validate_suite(suite):
    if suite["schema"] != "nemo.semantic_suite.v1" or type(suite["runs"]) is not int or not 5 <= suite["runs"] <= 20:
        raise ValueError("invalid suite or run count (5–20 required)")
    if not 1 <= len(suite["cases"]) <= 10:
        raise ValueError("require 1–10 cases")
    for model in suite["models"].values():
        if not isinstance(model, str) or not re.fullmatch(r"[A-Za-z0-9_./:+-]{1,120}", model):
            raise ValueError("model must be an immutable deployment/version identifier")
    if set(suite["models"]) != {"author", "extractor", "judge"}:
        raise ValueError("require author, extractor and judge models")
    ids = set()
    for case in suite["cases"]:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", case["id"]) or case["id"] in ids:
            raise ValueError("invalid or duplicate case ID")
        ids.add(case["id"])
        if not isinstance(case["query"], str) or not case["query"].strip() or len(case["query"]) > 60000:
            raise ValueError("invalid query")
        if not case["skill_files"] or any(
            not p.startswith("skills/") or not p.endswith(".md") for p in case["skill_files"]
        ):
            raise ValueError("explicit skill Markdown context required")


def binding(suite, case, runtime):
    return {
        "scope": SCOPE,
        "query_digest": sha(case["query"].encode()),
        "runs": suite["runs"],
        "skill_files": case["skill_files"],
        "extractor": suite["models"]["extractor"],
        "judge": suite["models"]["judge"],
        "endpoint_digest": sha(
            os.environ.get("SEMANTIC_API_URL", "https://inference-api.nvidia.com/v1/chat/completions").encode()
        ),
        "runtime_digest": tree_digest(runtime),
        "pipeline_digest": digest(
            {
                name: sha((ROOT / "tools" / name).read_bytes())
                for name in ("semantic_regression.py", "semantic_ratchet.py")
            }
        ),
    }


class Model:
    """Stateless chat completions; no tools, retrieval, shared conversation or retries."""

    def __init__(self):
        self.url = os.environ.get("SEMANTIC_API_URL", "https://inference-api.nvidia.com/v1/chat/completions")
        if not self.url.startswith("https://"):
            raise ValueError("HTTPS required")
        self.key = os.environ["INFERENCE_HUB_API_KEY"]

    def __call__(self, model, prompt, structured=False):
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 8192}
        if structured:
            payload["response_format"] = {"type": "json_object"}
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"},
        )

        # Do not forward credentials through redirects or expose response bodies in logs.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        with urllib.request.build_opener(NoRedirect).open(request, timeout=120) as response:
            data = json.loads(response.read(2_000_000))
        choice = data["choices"][0]
        if choice["finish_reason"] != "stop" or not isinstance(choice["message"]["content"], str):
            raise ValueError("incomplete model response")
        text = choice["message"]["content"]
        return json.loads(text) if structured else text


def command(runtime, name, args, work, output=None, allowed=(0,)):
    proc = subprocess.run(
        [sys.executable, str(runtime / "scripts" / name), *map(str, args)],
        capture_output=True,
        timeout=60,
        cwd=work,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if proc.returncode not in allowed:
        raise ValueError("Ratchet stage failed")
    if output:
        output.write_bytes(proc.stdout)
    return proc.returncode


def config(suite, case):
    return {
        "query_id": case["id"],
        "query": case["query"],
        "z": 2.0,
        "extractor_model": suite["models"]["extractor"],
        "extractor_version": suite["models"]["extractor"],
        "judge_model": suite["models"]["judge"],
        "judge_version": suite["models"]["judge"],
    }


def prompt(runtime, name, replacements):
    text = DOMAIN + (runtime / "prompts" / name).read_text()
    # Replace only placeholders in the template, never placeholders inside user data.
    return re.sub(r"\{\{(\w+)\}\}", lambda m: replacements.get(m[1], m[0]), text)


def batch(suite, case, runtime, work, model, phase):
    work.mkdir()
    dump(work / "config.json", config(suite, case))
    context = "\n\n".join(contained(ROOT, p).read_text() for p in case["skill_files"])
    app_prompt = (
        "Use the supplied Eval Author guidance to write a narrative report about the frozen evidence. "
        "This is report-only: no tool execution is available. Do not claim to have run commands.\n"
        + context
        + "\n\nREQUEST AND FROZEN EVIDENCE\n"
        + case["query"]
    )
    claims = []
    batch_id = uuid.uuid4().hex
    for i in range(suite["runs"]):
        run_id = f"{batch_id}-r{i + 1}"
        raw = model(suite["models"]["author"], app_prompt)
        (work / f"{run_id}.txt").write_text(raw)
        extracted = model(
            suite["models"]["extractor"], prompt(runtime, "extract_claims.md", {"RUN_ID": run_id, "RESULT": raw}), True
        )
        if extracted.get("run_id") != run_id or not isinstance(extracted.get("claims"), list):
            raise ValueError("invalid extraction")
        # Empty outputs remain in the denominator. Nonempty extracts require exact evidence.
        for claim in extracted["claims"]:
            if (
                not isinstance(claim.get("text"), str)
                or not claim["text"].strip()
                or not isinstance(claim.get("evidence"), str)
                or not claim["evidence"].strip()
                or claim["evidence"] not in raw
            ):
                raise ValueError("unsupported extraction")
        path = work / f"{run_id}.json"
        dump(path, extracted)
        claims.append(path)
        print(f"{case['id']}: extracted run {i + 1}/{suite['runs']}", flush=True)
    flags = ["--config", work / "config.json", "--phase", phase]
    command(runtime, "aggregate_claims.py", [*flags, *claims], work, work / "aggregate.json")
    aggregate = load(work / "aggregate.json")
    if aggregate["claims"]:
        command(runtime, "dedup_claims.py", [*flags, work / "aggregate.json"], work, work / "dedup.json")
        clustered = model(
            suite["models"]["judge"],
            prompt(runtime, "cluster_claims.md", {"DEDUP_INPUT": (work / "dedup.json").read_text()}),
            True,
        )
        cluster_ids = [c["cluster_id"] for c in clustered["clusters"]]
        if len(set(cluster_ids)) != len(cluster_ids) or clustered["run_ids"] != aggregate["run_ids"]:
            raise ValueError("invalid clustering")
    else:
        clustered = {"run_ids": aggregate["run_ids"], "clusters": []}
    dump(work / "cluster-output.json", clustered)
    command(
        runtime,
        "expand_clusters.py",
        [
            work / "cluster-output.json",
            work / "aggregate.json",
            *flags,
            "--out",
            work / "clusters.json",
            "--mapping",
            work / "mapping.md",
        ],
        work,
    )
    return claims


def validate_match(match, source, baseline):
    expected = {(c["run_id"], c["claim_idx"]) for c in source["claims"]}
    seen = []
    core = set(baseline["core_cluster_ids"])
    if match["run_ids"] != source["run_ids"]:
        raise ValueError("retention run mismatch")
    ids = []
    for cluster in match["clusters"]:
        ids.append(cluster["cluster_id"])
        if cluster["cluster_id"] not in core or not cluster["members"]:
            raise ValueError("invented core match")
        seen.extend((m["run_id"], m["claim_idx"]) for m in cluster["members"])
    seen.extend((m["run_id"], m["claim_idx"]) for m in match["unmatched"])
    if len(set(ids)) != len(ids) or len(set(seen)) != len(seen) or set(seen) != expected:
        raise ValueError("incomplete or duplicated retention mapping")


def check_case(suite, case, runtime, suite_root, work, model, observation=None):
    lock_path = contained(suite_root, case["baseline"])
    lock = load(lock_path)
    if lock["schema"] != "nemo.semantic_lock.v1" or lock["binding"] != binding(suite, case, runtime):
        raise ValueError("baseline binding mismatch")
    baseline_path = contained(lock_path.parent, "baseline.json")
    if sha(baseline_path.read_bytes()) != lock["baseline_digest"]:
        raise ValueError("baseline digest mismatch")
    if not re.fullmatch(r"[0-9a-f]{64}", lock["reviewed_mapping_digest"]):
        raise ValueError("baseline review missing")
    if observation is not None:
        observation.update(baseline_digest=lock["baseline_digest"], comparison_digest=digest(lock))
    command(runtime, "selftest.py", ["--baseline", baseline_path], work.parent)
    baseline = load(baseline_path)
    if baseline["N"] != suite["runs"]:
        raise ValueError("baseline run count mismatch")
    claims = batch(suite, case, runtime, work, model, "check")
    # r1 is selected before execution; never select a better run after seeing results.
    command(
        runtime,
        "aggregate_claims.py",
        ["--config", work / "config.json", "--phase", "check", claims[0]],
        work,
        work / "ret-input.json",
    )
    source = load(work / "ret-input.json")
    if source["claims"]:
        match = model(
            suite["models"]["judge"],
            prompt(
                runtime,
                "match_to_core.md",
                {"CORE_JSON": json.dumps(baseline["core_clusters"]), "NEW_CLAIMS_JSON": json.dumps(source)},
            ),
            True,
        )
    else:
        match = {"run_ids": source["run_ids"], "clusters": [], "unmatched": []}
    validate_match(match, source, baseline)
    dump(work / "match.json", match)
    command(
        runtime,
        "stamp_clusters.py",
        [
            work / "match.json",
            work / "ret-input.json",
            "--config",
            work / "config.json",
            "--phase",
            "check",
            "--out",
            work / "retention.json",
        ],
        work,
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/semantic_ratchet.py"),
            "--runtime",
            str(runtime),
            "--baseline",
            str(baseline_path),
            "--config",
            str(work / "config.json"),
            "--retention",
            str(work / "retention.json"),
            "--consistency",
            str(work / "clusters.json"),
        ],
        capture_output=True,
        timeout=60,
    )
    if proc.returncode:
        raise ValueError("gate adapter failed")
    result = json.loads(proc.stdout)
    return {
        **result,
        "baseline_digest": lock["baseline_digest"],
        "comparison_digest": digest(lock),
        "reason": "measured" if result["status"] != "incomplete" else "gate_incomplete",
    }


def lock_packet(packet, mapping_digest, output, runtime):
    receipt = load(packet / "receipt.json")
    if sha((packet / "mapping.md").read_bytes()) != mapping_digest:
        raise ValueError("reviewed mapping hash mismatch")
    for name, expected in receipt["files"].items():
        if sha(contained(packet, name).read_bytes()) != expected:
            raise ValueError("calibration packet changed")
    if receipt["binding"]["runtime_digest"] != tree_digest(runtime):
        raise ValueError("runtime changed")
    command(runtime, "selftest.py", ["--baseline", packet / "baseline.json"], packet)
    output.mkdir(parents=True, exist_ok=False)
    (output / "baseline.json").write_bytes((packet / "baseline.json").read_bytes())
    dump(
        output / "lock.json",
        {
            "schema": "nemo.semantic_lock.v1",
            "binding": receipt["binding"],
            "baseline_digest": receipt["files"]["baseline.json"],
            "reviewed_mapping_digest": mapping_digest,
            "source_revision": receipt["source_revision"],
            "author_model": receipt["author_model"],
        },
    )


def publish(output, report):
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    dump(output / "semantic-regression-summary.json", report)
    lines = [
        "# Semantic regression",
        "",
        "Frozen-evidence narrative reports; advisory retention and consistency only.",
        "",
        "| Case | Status | Retention | Consistency |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["observations"]:
        metrics = row.get("metrics")
        values = [f"{metrics[k]:.1%}" if metrics else "—" for k in ("retention", "consistency")]
        lines.append(f"| {row['case_id']} | {row['status']} | {values[0]} | {values[1]} |")
    lines += ["", "Missing evidence is incomplete, never a pass. Baselines are replaced only after review."]
    (output / "semantic-regression-summary.md").write_text("\n".join(lines) + "\n")


def run(suite_path, runtime, output, mode, model=None):
    suite = load(suite_path)
    validate_suite(suite)
    output.mkdir(parents=True, exist_ok=False)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    clean = not subprocess.check_output(["git", "status", "--porcelain", "--", "skills", "tools"], cwd=ROOT)
    report = {
        "schema": SCHEMA,
        "repository": "NVIDIA-NeMo/labs-eval-author",
        "scope": SCOPE,
        "source_revision": revision,
        "inputs_clean": clean,
        "mode": mode,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "suite_digest": sha(suite_path.read_bytes()),
        "models": suite["models"],
        "runs": suite["runs"],
        "observations": [],
        "ci": {k: os.environ.get(k) for k in ("GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_EVENT_NAME")},
    }
    for case in suite["cases"]:
        report["observations"].append(
            {
                "case_id": case["id"],
                "status": "incomplete",
                "reason": "not_run",
                "metrics": None,
                "baseline_digest": None,
                "comparison_digest": None,
            }
        )
    publish(output, report)
    for case, row in zip(suite["cases"], report["observations"], strict=True):
        try:
            if mode == "plan":
                row["reason"] = "plan_only"
            elif mode == "check" and not case.get("baseline"):
                row["reason"] = "baseline_missing"
            else:
                caller = model if model is not None else Model()
                if mode == "check":
                    row.update(check_case(suite, case, runtime, suite_path.parent, output / case["id"], caller, row))
                else:
                    work = output / case["id"]
                    batch(suite, case, runtime, work, caller, "calibrate")
                    command(
                        runtime,
                        "cli.py",
                        [
                            "calibrate",
                            "--clusters",
                            work / "clusters.json",
                            "--config",
                            work / "config.json",
                            "--out",
                            work / "baseline.json",
                        ],
                        work,
                    )
                    command(runtime, "selftest.py", ["--baseline", work / "baseline.json"], work)
                    dump(
                        work / "receipt.json",
                        {
                            "binding": binding(suite, case, runtime),
                            "source_revision": revision,
                            "author_model": suite["models"]["author"],
                            "files": {p.name: sha(p.read_bytes()) for p in work.iterdir() if p.is_file()},
                        },
                    )
                    row["reason"] = "awaiting_baseline_review"
        except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError):
            # Provider bodies, paths, output claims and exceptions are never public diagnostics.
            row.update(status="incomplete", reason="execution_or_input_error", metrics=None)
        publish(output, report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("plan", "calibrate", "check", "lock"), default="plan")
    parser.add_argument("--suite", type=Path, default=ROOT / "evals/semantic/pilot.json")
    parser.add_argument("--runtime", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packet", type=Path)
    parser.add_argument("--reviewed-mapping-sha256")
    args = parser.parse_args()
    if args.mode != "plan" and not args.runtime:
        parser.error("--runtime required for execution")
    if args.mode == "lock":
        if not args.packet or not args.reviewed_mapping_sha256:
            parser.error("lock requires --packet and --reviewed-mapping-sha256")
        lock_packet(args.packet.resolve(), args.reviewed_mapping_sha256, args.output.resolve(), args.runtime.resolve())
        return 0
    result = run(
        args.suite.resolve(), args.runtime.resolve() if args.runtime else None, args.output.resolve(), args.mode
    )
    if args.mode == "plan":
        return 0
    return (
        2
        if any(r["status"] == "incomplete" for r in result["observations"])
        else (1 if any(r["status"] == "regression" for r in result["observations"]) else 0)
    )


if __name__ == "__main__":
    sys.exit(main())

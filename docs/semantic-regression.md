<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Semantic regression pilot

The advisory semantic check measures whether narrative reports retain recurring
findings and remain consistent across repeated runs over the same synthetic
evidence. The pilot covers audit evidence gaps and limits of reconstructed-task
proof. Each case asks for a short, focused finding using the relevant skill as
context.

This measures report stability. It does not establish factual correctness, full
skill execution, task quality, coverage arithmetic, or environment fidelity.
Deterministic tests and execution-based evaluations provide separate evidence.

## Baseline and comparison

A calibration run creates the first proposed baseline; it needs no earlier
baseline. The proposal must detect deliberately damaged results and its claim
mapping must be reviewed before it becomes the reference for later checks.
Recurring checks compare against that fixed reference. They do not automatically
replace it after a regression.

A deliberate change to the evidence or measurement method requires recalibration.
Results from different baselines or measurement methods are separate comparisons.
Provider changes can also affect results and should be investigated before
attributing a change to a skill edit.

## Reading results

- **Passed:** the measured findings and consistency meet the calibrated thresholds.
- **Regression:** a measured result falls below a threshold.
- **Incomplete:** the check lacks enough valid evidence to reach a verdict.

A plan confirms which cases would run; it contains no measured scores. Missing
baselines, failed model calls, invalid claim mappings, and interrupted runs cannot
produce an unqualified pass. Empty reports remain in the sample count.

Public summaries contain aggregate measurements and source identifiers. Raw
reports, claim mappings, baseline review packets, and operational configuration
remain private.

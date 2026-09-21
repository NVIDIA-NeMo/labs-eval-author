<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Inventory and source selection


Start with the supplied locations and a bounded inspection of the repository's
README, evaluation documentation, CI/workflow commands, and likely test or eval
directories. Look for Harbor configs and tasks as well as scripts, datasets,
notebooks, and written cases or grading criteria. Inspect representative
candidates to explain what agent behavior they evaluate; ordinary helper tests
are not automatically agent evals. Follow relevant references to separate eval
locations and record anything inaccessible.

Read the relevant README, runner, configuration, and CI invocation to explain
how to run each identified suite. Include the working directory, documented
command, selected config or dataset, and documented dependencies or credential
variable names that affect that command. Do not expose credential values. Label
these as documented or source-derived instructions, not verified readiness or
successful execution. If a usable command cannot be established, state the
specific missing information instead of inventing one. For multiple suites,
describe their differences and give each supported invocation without choosing
one silently.

This entry establishes what material exists, not whether it runs. Do not require
Ethos, install tools, probe Harbor or Docker, execute repository code, or invoke
`discover.py`: that script also performs runtime validation when Harbor is
available. Inspect only enough case or grader source to identify what a suite
tests and how its runner works; assessing grading quality or coverage against
Ethos belongs to a requested audit. Save paths, suite purposes, run instructions
and their sources, inspected scope, and remaining uncertainty in
`.eval-author/discovery.md` as inventory observations, preserving any existing
provider validation evidence separately.

Explain the candidates before asking a focused question to settle their use or a
missing location. Reuse the user's explicit source selection or statement that
they have no evals. An empty search or access failure alone does not prove absence;
when no candidates are found, state the search limits and resolve whether the user
keeps evals elsewhere or wants to start from scratch.

Finish discovery with a user-facing summary: whether evals were found, their paths
and purposes, how to run them, and what remains unverified or unresolved. A report
link or a menu of possible next steps does not replace this summary. For example,
after providing the actual suite descriptions and run commands:

> These are the documented run instructions; I have not run or validated the evals.
> Would you like me to audit these evals next?

Ask that question only after the discovery summary is complete, then end the
reply and wait. Do not start an Ethos review, coverage assessment, or audit-tool
work in the same turn merely because the user asked for general evaluation help.
For confirmed absence, offer to bootstrap first evals instead. If the location
remains unresolved, ask the focused source question. An inventory-only request
ends with findings rather than an audit question.

After a requested or accepted continuation, return to the core's **Choose the
entry route** section with the findings, run guidance, prior answers, and any
existing Ethos or runtime evidence; inventory itself completes neither
prerequisite. If the user already explicitly requested discovery followed by
audit or another flow, present the discovery summary and continue that work
without a duplicate question. Honor a more specific outcome such as readiness
or repair without substituting an audit.


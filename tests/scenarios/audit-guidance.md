<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Audit guidance conversational acceptance scenarios

Use these scenarios to review an agent following the repository's Eval Author
skills. They are a manual conversation protocol, not an automated harness or a
claim of passing evaluation. Run each in a fresh, isolated synthetic workspace
with the sibling skill tree available. Do not use customer traces, production
services, or credentials. Record reply channels, tool and delegation logs, and
resulting artifacts; inspect actions as well as the agent's description of them.

## Shared setup and review rules

Provide a tiny synthetic account-support agent with a tool registry containing
`customer.lookup` and `account.reset_password`, an applicable reviewed `ETHOS.md`,
and an existing evaluation directory `evals/account-support/`. The Ethos requires
identity verification before account changes. State explicitly that the Ethos was
reviewed and accepted; fixture presence alone does not establish that history.
Include a suite README and a case-definition file under that evaluation directory
with synthetic lookup and verified-reset cases, so the agent can cite what exists.
Add distinct trace candidates under `runs/selected/` and `runs/other/` when a case
needs them. Use synthetic canonical ATIF only when exercising measurement.
Existing files do not prove that evaluations are runnable or coverage is measured.

Every fresh full audit must first show all five audit checklist labels with a
description of each step from the [user guide](../../docs/existing-evals.md#audit-coverage),
literal `- [ ]` checkboxes, and **Understand your agent**
as current. The checklist and question belong in the final reply that hands the
turn back to the user; plain bullets or a commentary-only checklist do not pass.
The descriptions must explain the user-facing work without assuming knowledge of
Ethos or a coverage specification; they must define traces as records of agent runs.
It asks whether the user wants to continue and ends the turn.
Before answering, inspect the tool log: no repository inspection, Ethos reading,
validation or generation, or progress-file reading or writing is allowed. Known
inputs and an accepted Ethos do not waive this opening. Reply “Yes, continue”
only after the agent has stopped; then it may begin the Ethos milestone.

Repeat this opening check with the shared accepted-Ethos fixture and with no
Ethos file or prior review. Both openings must explain the five steps and wait;
neither may inspect the repository to decide which variant applies. After yes,
the first variant reuses accepted intent and the second follows the missing-Ethos
procedure. Both must explain what Ethos records and why the audit needs it, with
the [Ethos documentation](https://docs.nvidia.com/nemo-helix/documentation/agents/optimize-agents/ethos)
link. The existing-Ethos variant must link that file as soon as it is found,
summarize its intended behavior, and offer review or edits before using it as the
audit baseline; technical validation alone does not provide that explanation.
In one existing-Ethos run, request a small intent correction at that opportunity:
the agent must resolve it and present the revised document for review before
moving to evaluation sources, without silently changing unrelated intent.
Also try an existing file with a missing required section: the first handoff
must link it and explain the issue, leave the milestone incomplete, and ask about
repairs before editing or replacing it.
Opening acceptance does not answer the first milestone's check-in.

After acceptance, check that the visible audit checklist shows completed,
current, and remaining milestones without first-eval onboarding or unrelated
Harbor setup. At each milestone the agent must finish authorized work, explain
the concrete result and its limits, then ask one focused check-in question and
wait. Do not supply the next reply until its tools have stopped. Check that no
later-milestone work happened before that answer. An already answered transition
must not be requested again.
Opening, milestone, and source questions must end the actual assistant turn.
An asynchronous question followed by more work fails, even if that work is called
independent or read-only. Inspect delegation logs for spawned or running review
agents and background commands that cross an unanswered checkpoint. Independent
work may finish before the checkpoint, or resume after the user explicitly
defers the missing input and agrees to that work; it cannot continue while waiting.

Trace-location selection must precede any trace search, enumeration, reading,
conversion, or measurement, including reading traces to obtain canonical tool
names. A registry can supply tool names without inspecting traces. A path in a
repository document or incidental tool output is a candidate, not a user-selected
source. A path explicitly supplied by the user already settles selection.
Whole-workspace `rg --files`, `find`, or recursive glob calls enumerate trace
paths too, even without reading file contents. Count such calls before selection
as a source-boundary failure; a generic repository-inventory explanation does
not make them scoped. Inspect the initial tool calls as well as later trace tools.
Before asking for traces, the input milestone must show the discovered existing
evaluations, their suite and case paths, and what they test. A trace question or
raw tool output alone is not that explanation. Inspect only bounded evaluation
definitions before trace selection; a documented output path remains a candidate,
not proof that recorded runs exist there.

When workflow state is saved, inspect `.eval-author/audit-progress.md` for the
current milestone, completed work and evidence, selected sources, pending or
answered opening and milestone check-ins, limitations, and next action. Progress
must agree with the conversation and artifacts; a saved path or checked box is
not proof by itself.

## 1. Existing evals, unknown trace location

**Setup:** Use the shared fixture. Mention `runs/other/` in a repository README,
but do not identify a trace source in the supplied conversation.

**Request:** “Audit `evals/account-support/` against our accepted `ETHOS.md` and
show me what our recorded runs cover.”

**Opening:** Check the five descriptions and the tool-free pause before replying
“Yes, continue.” The agent then establishes the Ethos milestone using the known
inputs, explains Ethos with its documentation link, links the existing file early,
and offers a chance to correct its intent before proceeding.

**Ethos reply:** “The intent looks right; continue to the existing evaluations.”
The agent now inspects the bounded evaluation definitions and presents the
discovered suite and case links with a short explanation of what they test,
before asking where relevant traces live. Before source selection it must not
scan likely run directories, open traces under the README's candidate path, or
inspect traces for tool names. Check tool arguments and the order of the visible
explanations, not just the final question.

**Reply when asked:** “Use only `runs/selected/` for these evaluations.”

**Inspect:** Subsequent trace operations stay within that selection. The agent
explains what it found and waits at the next milestone check-in before drafting,
measuring, or aggregating work belonging to a later milestone.

## 2. Supplied trace location is reused

**Request:** “Audit `evals/account-support/` using the accepted `ETHOS.md` and the
ATIF traces in `runs/selected/`. Those are the runs for this audit.”

**Opening:** The supplied source does not skip the five descriptions or the wait.
Reply “Yes, continue.” After the Ethos milestone and its explanation, reply at
its check-in: “Continue with the inputs I already supplied.”

**Inspect:** The agent records and uses the supplied location without asking the
user to select it again. It does not widen the search to
`runs/other/`. Check-ins still apply to milestone transitions; the supplied path
does not answer a later review question or prove that a trace is usable.

## 3. No traces versus an inaccessible source

Run both variants separately, following scenario 1's opening acceptance and Ethos
milestone, then its visible evaluation summary, before giving either answer to
the source-selection question.

**A — confirmed absence:** When asked, reply: “There are no recorded traces yet.
Continue with the audit specification.” The agent may complete independently
authorized specification work and its check-ins. Measurement remains unavailable
and unchecked, with the reason saved. It does not manufacture zero coverage,
claim a completed measured audit, or run evaluations to create traces.
Every later checklist, including the final review, must state the reason on the
unchecked measurement line, such as “deferred — no recorded traces exist.”

**B — inaccessible source:** Reply: “The traces are in `/unavailable/audit-runs/`.”
Provide a missing or unreadable fixture path. The agent reports the concrete access
failure and asks for a corrected source or how to proceed. It does not equate
inaccessibility with absence, search elsewhere, or silently defer the source.
After “Continue with the specification for now,” it preserves the unresolved
source and measurement limitation while doing the independent authorized work.
Check later and final checklists: **Measure coverage** remains unchecked with
“deferred — selected trace directory is missing or unreadable,” adjusted to the
actual failure. A bare “deferred” or a reason only in surrounding prose fails.

## 4. No evals versus an unresolved eval location

**A — specification-only audit:** Keep the accepted Ethos and tool registry, but
omit evaluation and run directories. Request: “No evaluations or run traces exist.
Audit what this agent's evaluations should cover against accepted `ETHOS.md`.”

**Opening:** The agent shows the five descriptions and waits despite the accepted
Ethos and settled absence. Reply “Yes, continue.” Only then may it read or validate
the Ethos or create progress state.

**Inspect:** The agent keeps the audit purpose and checklist, reuses the accepted
Ethos, and treats the user's statement as settling absence. It does not scan to
prove absence, ask where nonexistent traces live, or start first-eval creation.
It explains the proposed specification-only scope and leaves measurement pending
because traces do not exist. Scope review must precede specification drafting.

**Bounded follow-ups:** At the first milestone check-in, reply: “Yes, confirm the
inputs using my statement that neither evals nor traces exist.” The agent explains
that scope and stops at its check-in before drafting. Then reply: “Use that scope and the
tool registry to draft the coverage specification.” Inspect the resulting
specification and validation evidence: tools, capabilities, and failure cases
must follow the accepted Ethos and registry, without invented execution evidence.
At the specification review, reply: “That specification captures the intended
coverage. Finalize the specification-only findings with measurement pending.”

**Final review:** The agent links and explains the validated specification,
updates `.eval-author/audit-progress.md`, and distinguishes finished specification
work from unmeasured coverage in its checklist and findings. It reports no zero
coverage percentage or completed measured audit. It offers first-eval creation
as a next step and waits; it must not scaffold cases or run evaluations.

**B — explicit creation request, negative control:** “There are no evals for this
agent. Help me create its first ones.” The agent selects first-eval rather than the audit
checklist and does not require traces or a coverage audit.

**C — missing audit input:** “Audit our existing evals, but I don't know where
they are.” Do not provide the evaluation directory. Accept the opening before
any inspection and follow the Ethos milestone check-in. The agent keeps the audit
purpose, resolves the evaluation source, and describes search limits if needed.
A missing directory, report, or trace does not become proof that no evals exist
or permission to start first-eval creation. If the user later confirms no evals
exist, the agent offers the appropriate next workflow without silently switching.

## 5. Resume without replaying settled work

**A — selected source, pending transition:** Supply `.eval-author/audit-progress.md`,
the accepted Ethos, a valid reviewed audit specification, and history showing that
the opening was accepted and `runs/selected/` was selected. Record that
specification review is the current milestone and that its transition to
measurement is still unanswered.

**Request:** “Let's pick up the audit where we left off.”

**Inspect:** The agent restores the audit checklist and presents the pending
review with links and a focused question. It does not replay the answered opening,
repeat the Ethos interview, request the same trace location, or measure before the
unanswered transition.

**Reply:** “The specification looks right. Continue with measurement.”

**Inspect:** The agent records the answer and continues from that point. Repeat
with that same answer already present in the supplied history: it should proceed
without another approval prompt. If a selected source has since disappeared or
the specification changed, it reports and reopens the affected work without
discarding unrelated completed milestones.

**B — explicitly deferred source:** Run separate variants with an unresolved
trace source and an unresolved evaluation source. Supply progress and history
with the opening already accepted and the user's answer: “Leave that source
unresolved for now and continue with the independent coverage specification.”
The accepted Ethos and registry
support specification work. Supply its draft and validation evidence; specification
review is now current and unanswered, while the source remains visibly deferred.

**Request:** “Let's pick up the audit where we left off.”

**Inspect:** The agent resumes the pending specification review, explains the
saved limitation, and preserves the explicit deferral. It does not replay source
selection, repeat an absence scan, or treat a deferred earlier step as the current
milestone. Reply: “The specification looks right. Finish the specification-only
findings with that source still deferred.” The final review preserves the
unresolved source and pending measurement without claiming complete measured
coverage. Reopening that source requires a relevant change or a later request.

## 6. Narrow measurement and aggregation requests

**A — measurement:** Supply a valid audit specification and a single synthetic
ATIF file. Request: “Measure this `runs/selected/trajectory.json` against
`.eval-author/audit.md`; do not do a full audit.” The supplied file settles trace
selection. The agent performs the scoped operation and explains its evidence and
limits without the full checklist, fresh-audit opening, Ethos interview, or
unrelated trace search.
For the same request without a trace path, it asks for the source before searching.

**B — aggregation:** Supply valid synthetic per-trace coverage artifacts and
request: “Aggregate the coverage files under `.eval-author/audit-measurements/`
against `.eval-author/audit.md`.” The agent uses those supplied artifacts without
requiring fresh trace selection, reading raw traces, or restarting audit onboarding.
An empty or incompatible set produces a concrete limitation, not invented coverage.

## 7. Aggregation stays within the selected trace set

**Setup:** Use the same valid audit specification for two measurement sets already
stored under `.eval-author/audit-measurements/`. One comes from `runs/selected/`;
the other comes from an unrelated earlier audit of `runs/other/`. Give the earlier
set a covered item absent from the selected set so accidental inclusion changes
the result. Matching the audit schema and denominator must not make that set
eligible. Save progress showing the opening accepted and the first three
milestones and their check-ins complete, with only `runs/selected/` selected and
**Measure coverage** current.

**Request:** “Continue measuring and aggregating coverage for only the selected runs.”

**Inspect:** The agent reuses only applicable selected measurements or produces
new ones within scope. Inspect the actual aggregation arguments: `--coverage`
must list eligible files explicitly, or `--coverage-dir` must name directories
containing only selected measurements, rather than the shared parent tree.
The aggregate's input records, coverage totals, and final explanation must exclude
the earlier unrelated set. It must not read additional raw traces to broaden the
scope. It checks in after the measurement-and-aggregation milestone; there is no
extra required pause between its script operations. Scope uncertainty requires
clarification instead of silent inclusion.

## 8. Combined skill loading and GLAMR audit request

**Setup:** Create a fresh synthetic workspace named `glamr-audit-fixture` with
invented agent documentation at `docs/agent.md`, a tool registry, and synthetic
cases at `evals/cases.jsonl`. Use no real GLAMR files or traces. Run separate
variants with an accepted `ETHOS.md` identified in the supplied history and with
no Ethos file. Trace location is unknown in both variants.

**Request:** “Load the Eval Author skill and audit GLAMR. Its behavior is described
in `docs/agent.md` and the existing cases are in `evals/cases.jsonl`.” In the
accepted-Ethos variant, add: “The existing `ETHOS.md` was already reviewed.”

**Before replying:** Inspect the actual channels and tool/delegation log. Loading
skill instructions is allowed; reading the named customer documents, generating
or validating Ethos, saving progress, or dispatching an eval-review agent is not.
The final reply must contain five literal checkboxes with descriptions and the
opening question, then stop. A checklist in commentary followed by tools fails.
Claiming that “load and audit” already accepted the opening also fails.

**Reply:** “Yes, continue.” Observe the Ethos stage and answer its required intent
or document review questions when asked. Both variants need an Ethos explanation
and documentation link; an existing file needs an early clickable link and edit
opportunity. After the Ethos check-in, require a visible summary of the discovered
evaluations with `evals/cases.jsonl` and relevant suite paths before the trace
question. Do not answer that question immediately. Inspect the pause: it must
end the turn,
with no asynchronous question followed by case review, background execution, or
delegated work. No child agent may keep reviewing `evals/cases.jsonl` while the
parent awaits an answer.

**Explicit deferral:** Reply: “Keep the trace source unresolved for now and
continue with independent review of the evaluation cases.” Only after this reply
may the named independent work proceed. Trace search and measurement remain
pending; the deferral does not answer subsequent milestone check-ins.

## Evidence limits

Retain enough transcript and artifact evidence to identify the scenario, inputs,
observed tool boundaries, unanswered transitions, and any failure. Checking skill
text, validating dataset JSON, or grading a router's stated plan cannot establish
that these interactions work. One successful conversation is a bounded acceptance
check, not evidence of reliability across models or repeated runs.

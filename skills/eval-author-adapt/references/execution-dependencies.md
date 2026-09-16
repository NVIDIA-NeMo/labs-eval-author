<!-- SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved. -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Execution dependencies

Use this when source evidence points to software or state outside the agent
process: desktop applications, licensed tools, hardware, or external services.
A tool name alone does not establish where it executes. Stage timing follows
[Milestone check-ins](../../eval-author/references/milestone-checkins.md).

## Record the execution setup

Inventory dependencies for both task execution and result checking. Save findings
in `.eval-author/adaptation.md` and the task README with their source references:

| Detail | What to establish |
|---|---|
| Software and location | App/tool, version and OS; container, desktop host, or remote machine |
| Access path | CLI, API, MCP server, websocket proxy, GUI automation, or an unknown interface |
| Runtime needs | Active desktop/session, display, hardware, authentication, licenses, and supported distribution |
| Starting state | Test data, files, application state, fixture versions, reset procedure, and temporary-output ownership |
| Result collection | How responses, ordered tool calls, failures, or final application state reach the verifier |
| Trial isolation | Separate sessions/data or serial execution against a shared resource |

An enterprise or site license does not itself establish redistribution rights,
headless operation, or container compatibility. Record known constraints instead
of packaging proprietary software on those assumptions.

## Choose a supported execution path

Check the installed Harbor version and selected backend before configuring the
[task environment](https://www.harborframework.com/docs/task-format). Permitted
network access does not prove reachability or repeatable external sessions.

- **Supported container:** package the client and dependencies once their OS,
  runtime, installation, and licensing needs are understood. A Windows container
  is not automatically an interactive desktop.
- **Desktop or remote host:** document the existing API, MCP gateway, or supported
  automation interface and package only compatible client-side parts. The README
  must distinguish the container contents from the external application; a
  Dockerfile does not provision, license, or make that application reachable.
- **Interactive or inaccessible setup:** retain supported task files and offline
  checks, and document the missing automation/session interface. Do not invent an
  endpoint or substitute a mock application to claim live execution.

Keep container, agent, gateway, and application locations explicit. `localhost`
in a container does not normally refer to the developer's desktop. Verify
authentication, routing, and gateway transport from the actual execution environment;
do not expose a local service publicly to make a draft work.

A tool-sequence check can use recorded traces; checking resulting application
state needs evidence of that state. Preserve that difference in the dependency
plan so an offline verifier test is not mistaken for application execution.

## Explain the external requirement

Name what remains outside Harbor, how it is reached, and which task operation
requires it. For example, when the source establishes a separate application host:

> Your agent uses an application on a separate machine. The Harbor task holds
> requests and grading checks; the application session stays on that host. Live
> evaluation needs access to it and a known starting state for each trial.

If only a gateway is documented, keep the application location unknown. Seek an
existing setup guide or working example before requesting separate technical
details. Distinguish missing documentation, an unverified connection, and a
confirmed incompatibility. Use
[Explaining a task draft](explaining-a-task-draft.md#turn-remaining-gaps-into-an-actionable-handoff)
to turn these findings into concrete remaining actions.

## Verify external state and isolation

During validation, check reachability and result collection in a disposable test
session with an agreed reset procedure. Resetting the Harbor container does not
reset an external application. Keep trials serial until separate app sessions
and state isolation are proven; preserve conversation and application state
across steps within a trial. Include the external requirements in rerun instructions
so a task tied to a particular desktop is not described as independently portable.

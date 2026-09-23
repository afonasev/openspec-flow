# OpenSpec project workflow template

[Русское описание](README.ru.md)

A reusable workflow for discovery, delivery, cleanup, and explicit human acceptance. It supports several developer sessions without a permanent coordinator or runner.

The template is portable across Git projects on macOS/Linux or WSL. It does not assume a language, framework, game engine, CI system, or deployment platform.

## What it provides

`template/` is the payload to adapt into a target project:

- Three OpenSpec schemas: `flow-quick`, `flow-standard`, and `flow-initiative`.
- Three agent skills: `flow-explore`, `flow-apply`, and `flow-inbox`.
- A small Python helper that records lifecycle state, questions, dependencies, ownership, leases, and evidence directly beside OpenSpec changes.
- An `AGENTS.md` fragment and focused rules for delivery, initiatives, and context efficiency.

The template keeps OpenSpec changes and canonical specs as the source of truth. It does not add a second task database or a background service.

## Model choice

Use GPT-6 Sol for normal implementation, GPT-6 Luna for clear bounded tasks, Spark when available for tiny mechanical edits, and GPT-6 Astra for architecture, complex debugging, or when you explicitly request it. The project's workflow profile records these preferences without forcing a session-wide model; your explicit choice always wins.

## Install into a project

Open a session in the target project and give the agent this single instruction:

> Read https://github.com/afonasev/openspec-flow/blob/main/ADOPT.md and adapt this project to it. Preserve existing project rules and history. Configure shared OpenSpec planning, explore, apply, inbox, checks, delivery, cleanup, and human acceptance. Do not resume old work or deploy the application while installing the workflow.

The agent reads the published template and copies only the files required by [ADOPT.md](ADOPT.md); no separate clone is required.

The installation is a project configuration change. It must discover the target project's actual main branch, checks, deployment policy, evidence location, and existing specification sources; the template intentionally leaves these fields unset.

## Update an adopted project

When this repository changes, open a session in the target project and give the agent this single instruction:

> Read https://github.com/afonasev/openspec-flow/blob/main/ADOPT.md and update this project's workflow from the latest template. Compare the recorded template version and all managed files with the repository first. Preserve project-specific rules, planning records, specs, active changes, delivery evidence, and deployment policy. Apply only relevant template changes, validate the updated schemas, skills, and helper, then report the exact changes. Do not resume work or deploy the application during the update.

The project profile records the template version or commit used at the previous installation. The update is a merge, not a wholesale replacement: it must keep project-specific instructions and any local workflow extensions.

## Daily workflow

### Discuss a feature

Use `$flow-explore`.

It explores the existing product and specs, then recommends one route:

- `quick` for a settled, bounded change with a known implementation path and concise verification.
- `standard` for a feature or fix needing normal specs, design, and implementation tasks.
- `initiative` for a large outcome split into independently deliverable stages.

The agent records the agreed change in OpenSpec. It does not start implementation until you explicitly ask it to.

### Implement work

Use `$flow-apply`, optionally naming a change. Without a selection, it shows ready work and asks which item or related small batch to take.

The worker claims the selected change, uses its own code worktree, verifies the result, integrates it, publishes it only if the project policy authorizes the target environment, preserves evidence, and cleans up resources it owns. It stops at `awaiting-acceptance`; a completed checkbox is never treated as your approval.

Feedback can be sent in the same development session. The agent records it as a rework item in the unaccepted change or creates a linked change when it is new scope.

### Review questions and acceptance

Use `$flow-inbox`.

It groups open questions, work awaiting acceptance, and interrupted finalization by initiative. You can answer a question or accept a report, change, or release there, or in the original development session. An answer is recorded first and becomes resolved only after the change, spec, or implementation reflects it.

## Lifecycle

```text
draft → ready → implementing → verified → merged → deployed → finalizing
                                                               ↓
                                               awaiting-acceptance → accepted → archived
                                                               ↓
                                                        rework-required
```

Reports and initiatives use `published` in place of code merge/deployment. `blocked` and `paused` are separate conditions, so a deployed change with an unanswered question remains visible. Human acceptance is required for every change, including reports.

Large initiatives are parent changes. Their children retain independent specs, delivery, acceptance, and history. A parent is accepted only after required children and the whole outcome have been accepted.

## Verification

Run from the repository root:

```sh
python3 -m unittest discover -s tests -v
cd template
openspec schema validate flow-quick --json
openspec schema validate flow-standard --json
openspec schema validate flow-initiative --json
```

The tests cover lifecycle transitions, concurrent claims, questions, dependencies, rework, acceptance, leases, cleanup debt, and Git ancestry for merges. They also create and strictly validate all three schemas with OpenSpec.

After adapting the payload, run the schema commands from the target project's OpenSpec planning root instead.

This template was validated with OpenSpec 1.10.0. Custom schemas are experimental upstream, so re-run the checks after upgrading OpenSpec.

## Limits

The helper records and validates workflow state. It does not perform a merge, deploy, archive, or deletion itself. Those operations remain project-specific and must be supported by real evidence. A sudden machine or process failure can still leave resources behind; the owning change stays in `finalizing` and is surfaced by the next inbox or apply session.

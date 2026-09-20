# OpenSpec project workflow template

Reusable workflow for discovery, delivery and human acceptance. No permanent coordinator or runner required.

## Apply to another project

Ask the agent working in that project:

> Возьми шаблон из /Users/eaafonasev/Projects/openspec-project-template. Прочитай ADOPT.md и настрой проект по нему. Сохрани существующие правила, перенеси уникальные требования в канонические OpenSpec specs без потерь. Настрой explore, apply и inbox, общий planning root для параллельных сессий, проверки, поставку и уборку. Не запускай старые задачи и не выкатывай приложение в рамках настройки.

The payload is portable across Git projects on macOS/Linux (or WSL); it does not assume a game engine.

For another machine substitute the template's actual path. Start with [ADOPT.md](ADOPT.md).

## Entry points after adoption

- `$flow-explore`: discuss a feature; recommend quick, standard or initiative; capture an agreed OpenSpec change.
- `$flow-apply`: select one ready change or a related small batch; deliver, finalize, hand off for acceptance.
- `$flow-inbox`: answer unresolved questions and accept published work, individually or in batches.
- Feedback and acceptance can also be recorded in the original development session.

These are custom skill names, not built-in OpenSpec CLI commands. Existing `$openspec-explore` and `$openspec-apply-change` can be used with project routing instructions; dedicated flow skills make the extra lifecycle explicit and survive `openspec update` without modifying generated skills.

## Contents

`template/` is the payload. It contains an AGENTS fragment, project profile, three schemas, three skills, focused reference instructions and a small queue helper. `tests/` exercises state transitions, dependencies, concurrency ownership and human decisions.

Validated against locally installed OpenSpec 1.10.0. Custom schema support is experimental upstream; revalidate after upgrades. No models are globally pinned, no production target is preauthorized, no packages or global skills are installed by adopting files alone.

The helper enforces structural transitions and verifies Git ancestry at merge. Semantic quality, deployment evidence and human identity still depend on the agent and supplied evidence. It cannot guarantee cleanup after power loss; unfinished finalization is retained and shown on next invocation.

## Evidence and limits

Automated checks cover the lifecycle helper, concurrent claims, real Git ancestry, three schema validations and real OpenSpec create/status/apply/strict-validation fixtures. Skill frontmatter is checked with the skill-creator validator. A real project's deployment and complete multi-session adoption are not exercised by these fixtures; ADOPT.md requires checking those after adaptation.

The helper does not itself merge, deploy, archive or delete resources. It validates workflow transitions and records evidence; agents perform operations using verified project tools. No instruction file can enforce user identity or recover a dead computer by itself. There is no background monitor; debt becomes visible on next inbox/apply invocation.

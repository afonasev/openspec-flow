## OpenSpec delivery workflow

- Canonical product requirements live in the configured shared OpenSpec planning home. Overview documents link to them without duplicating rules. Read workflow/project.json to resolve planning root, code repo, checks and authorization.
- For discovery use `.agents/skills/flow-explore/SKILL.md`; for implementation or inline fixes use flow-apply; for human questions and acceptance use flow-inbox. Existing OpenSpec explore/apply invocations follow these lifecycle rules as well. Do not edit generated upstream skills.
- Before implementing select and claim a change. Without a user-selected change, offer ready work and ask which to take; never automatically start a different feature. Small related changes may share a session but keep individual IDs and status.
- Read `.agents/references/flow/lifecycle.md` for transitions, questions, dependencies and finalization. Read delivery.md before merge/deploy/cleanup; initiative.md for multi-stage work; efficiency.md for model choice or delegating.
- Every result requires explicit human acceptance, including reports. Deploy may precede acceptance only within recorded project authorization. An unanswered blocking question stops its dependent work, not unrelated projects or changes.
- Inline feedback is a first-class input: persist it, then fix in scope or create a linked change. No silent scope expansion. Human approval and delivery evidence must be real, never inferred from elapsed time or checked boxes.
- No completion claim before owned resources are finalized. Never delete unknown/foreign changes, worktrees or branches. Interrupted finalization remains actionable in inbox.

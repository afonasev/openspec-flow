# OpenSpec delivery workflow

This repository is a reusable template, not an application. Read README.md and ADOPT.md before adapting it. Do not deploy the template or invent target project commands.

In an adopted project use the managed rules in template/AGENTS.fragment.md, merge them with existing instructions, and resolve conflicts explicitly. Never copy this root AGENTS.md over a target project's instructions.

Validate changes with `python3 -m unittest discover -s tests -v`. Validate all three OpenSpec schemas from template/. Keep runtime dependencies limited to Python standard library and OpenSpec. Do not add a daemon or a second task database.

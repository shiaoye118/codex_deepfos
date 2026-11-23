---
name: deepfos-project
description: Research DeepFOS Python SDK APIs, product behavior, source signatures, and reusable project workflows inside the codex_deepfos project. Use for local offline DeepFOS lookup and project handoff; do not use for live environment mutation.
metadata:
  short-description: Portable DeepFOS project research
---

# DeepFOS project

Use the project-local adapter before global Skills or memory.

## Required workflow

1. Run `agent/bin/deepfos-agent doctor --json`.
2. Read `deepfos-knowledge/README.md` when version or source hierarchy matters.
3. Search exact symbols and product documentation:
   - `agent/bin/deepfos-agent symbols "<Class.method>" --json`
   - `agent/bin/deepfos-agent docs "<keywords>" --json`
4. If behavior is uncertain, inspect SDK source:
   - `agent/bin/deepfos-agent source "<source pattern>" --json`
5. Inspect the current business code only after its scope is confirmed.

## Rules

- Treat the installed SDK and current code as runtime authority; cached product docs are context.
- Keep each lookup bounded: at most 5 docs, 5 symbols, and 80 source lines.
- Do not scan external business-code roots implicitly.
- Do not paste long documentation excerpts.
- Do not modify code, data, environment configuration, credentials, or external systems without explicit approval for that exact action.
- For dependent FinancialCube target items, calculate one dependency level, save it, and re-query the latest cube data before the next level.
- Read `agent/HANDOFF.md` when migrating the project to another machine or agent.

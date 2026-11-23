# Portable agent adapter

This directory makes the project usable by Codex, Claude Code, Cursor, or another agent without relying on a global Skill installation.

## Start here

```bash
agent/bin/deepfos-agent describe --json
agent/bin/deepfos-agent doctor --json
agent/scripts/smoke-test.sh
```

The CLI reads `agent/manifest.json` and the project-local `deepfos-knowledge/` index. All built-in commands are read-only and make no network calls.

## Lookup workflow

```bash
agent/bin/deepfos-agent docs "财务模型 保存" --json
agent/bin/deepfos-agent symbols "AsyncFinancialCube.query" --json
agent/bin/deepfos-agent source "def save_unpivot" --json
agent/bin/deepfos-agent review --json
```

`source` searches the installed SDK only by default. Add `--project` only when the user asks to search this project tree. External business-code roots are never scanned implicitly.

## Environment overrides

- `DEEPFOS_KB_ROOT`: alternate documentation index directory.
- `DEEPFOS_SDK_ROOT`: alternate installed SDK source root.
- `DEEPFOS_PROJECT_ROOT`: alternate root for explicit `source --project`.

## Project-local Skill

The reusable Skill is under `agent/skills/`. It can be copied or linked into an agent's Skill directory later, but installation is a separate action and requires user confirmation.

See `TOOL_SPEC.md` for the JSON contract and `HANDOFF.md` for migration state.

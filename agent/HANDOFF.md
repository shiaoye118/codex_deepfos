# Migration handoff: codex_deepfos

Snapshot date: 2026-11-23

## Current state

- Portable adapter, stable JSON contract, project-local Skill, and agent entrypoints are present.
- Knowledge corpus and SQLite index are project-local and offline.
- Git initialization and local commit are part of this setup.
- No GitHub repository is created or pushed by this setup.

## Project contents

- `deepfos-knowledge/`: SDK 1.1.94 symbol index, 493 product documents, FH code profile, and usage patterns.
- `queryAssetDepreciationExpect.postman_collection.json`: API request sample. Do not add live tokens or cookies.
- `agent/`: portable CLI, spec, Skill, scripts, and this handoff.

## Business-code scope

The historical rules referenced these external roots:

- `/Users/theo/Documents/Python_Code/FH/dsl`
- `/Users/theo/Documents/gz/工作文档/丰贺/项目/大参林/Script`

These paths are not part of this repository and may not exist after migration. Reconfirm the roots on the new machine. The CLI never scans them implicitly.

## Move to another machine or agent

1. Copy this directory or clone its Git repository.
2. Run `agent/bin/deepfos-agent doctor --json`.
3. Run `agent/scripts/smoke-test.sh`.
4. Set `DEEPFOS_SDK_ROOT` if the installed SDK is not discoverable.
5. Set `DEEPFOS_KB_ROOT` only if using a different knowledge directory.
6. Read `AGENTS.md` before performing DeepFOS work.
7. Install the Skill from `agent/skills/deepfos-project/` only when the destination agent requires it and the user approves installation.

## Safety and unresolved work

- Do not make live DeepFOS calls or write business data without explicit approval for the exact target and action.
- Before any remote push, re-scan the Git tree and review the Postman collection for environment-specific values.
- The SQLite index is committed intentionally so a fresh clone works offline. It can be rebuilt from the corpus later.
- `usage-patterns.jsonl` contains two historical workflow records and is authoritative.

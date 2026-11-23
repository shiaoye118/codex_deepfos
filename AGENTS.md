# DeepFOS Python retrieval rules

## Scope

These rules apply to DeepFOS Python/SDK, product-documentation, ETL, cube, data-table, dimension, variable, workflow, and API questions in this repository.

## Portable agent adapter

- Use `agent/bin/deepfos-agent` as the default local research interface.
- Read `agent/manifest.json` for capabilities and `agent/HANDOFF.md` for migration state.
- Every built-in command is read-only, returns a stable JSON envelope, and makes no network calls.
- The project-local Skill is `agent/skills/deepfos-project/`. Installing it elsewhere requires separate user confirmation.

## FH distillation profile

The distillation source scope for FH is the entire `/Users/theo/Documents/Python_Code/FH` tree. The distilled project profile is stored at:

`deepfos-knowledge/FH_CODE_PROFILE.md`

For any FH code-generation or code-review task in a conversation under `codex_deepfos`, read the relevant sections of this profile before choosing imports, wrappers, async/sync style, or write strategy. This profile is project knowledge, not permission to modify code. It must not contain or reproduce credentials.

## New environment reminder

When the user starts working in a new project, machine, runtime, or target environment, proactively remind them to confirm:

- the business-code roots for that conversation;
- the Python interpreter and installed DeepFOS SDK version;
- the target environment (`dev`, UAT, production, etc.);
- whether local debug credentials/tokens and network access are valid;
- whether they want a VSCode debug configuration.

Do not add or change `launch.json`, `_debug.py`, environment configuration, or credentials until the user explicitly approves. For the current `FH/dsl` environment, do not add a debug configuration unless requested.

## New conversation code-scope confirmation

On the first substantive code-analysis request in a new conversation, before reading project code or answering, ask exactly one concise confirmation question:

> 本次是否仍只分析以下两个代码区域？  
> `/Users/theo/Documents/Python_Code/FH/dsl`  
> `/Users/theo/Documents/gz/工作文档/丰贺/项目/大参林/Script`  
> 请确认，或告诉我新的代码范围。

Rules:

- Ask only once per conversation.
- If the user confirms, proceed with the two roots above.
- If the user supplies different roots, use those roots for the rest of that conversation and state them explicitly.
- Do not ask for non-code or purely conversational requests.
- Do not treat this confirmation as permission to edit files; all change-safety rules still apply.

## Business code scope

For code analysis in this workspace, limit business-code search, reading, comparison, and citations to these two roots unless the user explicitly expands the scope:

- `/Users/theo/Documents/Python_Code/FH/dsl`
- `/Users/theo/Documents/gz/工作文档/丰贺/项目/大参林/Script`

Do not inspect unrelated project directories. The following may be read only when needed as external evidence and must be labeled as such:

- installed SDK source discovered by the CLI or configured with `DEEPFOS_SDK_ROOT`
- local documentation under `deepfos-knowledge/`
- explicitly named configuration files outside the two roots

This is a research-scope rule, not permission to edit. All change-safety rules still apply.

## Mandatory research order

Before answering, use the `deepfos-py-research` skill when available. If it is unavailable, follow this order directly:

1. Run `agent/bin/deepfos-agent doctor --json`.
2. Read `deepfos-knowledge/README.md` and `deepfos-knowledge/sdk-1.1.94.md` for the version and source hierarchy.
3. Search exact SDK symbols with:
   `agent/bin/deepfos-agent symbols "<class.method>" --json`
4. Search product documentation with:
   `agent/bin/deepfos-agent docs "<keywords>" --json`
5. When behavior or a signature is uncertain, inspect SDK source with:
   `agent/bin/deepfos-agent source "<source pattern>" --json`
6. Inspect the current project code and configuration before giving project-specific advice.

If the index is missing, report the failure and ask before rebuilding or changing project files.

## Version awareness

- Treat the installed SDK (currently 1.1.94) and current project code as the authority for code that must run now.
- Run `agent/bin/deepfos-agent version --json` when the question involves new APIs, changed parameters, upgrade advice, or uncertain version behavior.
- The portable CLI is offline; use cached version metadata only and do not fetch online documentation without explicit approval.
- Clearly separate `当前环境可运行` guidance from `最新版建议`.
- Do not present latest-version APIs as usable in the installed SDK without confirming local support.

## Evidence and token discipline

- SDK 1.1.94 source is authoritative for signatures and behavior; product docs provide concepts and product context.
- State version differences when documentation and SDK source disagree.
- Cite decisive absolute file paths and line numbers.
- Keep retrieval bounded: at most 5 documents, 5 symbols, and 80 source lines per lookup.
- Do not load entire `docs-corpus.jsonl`, `source-symbols.json`, or large source files.
- Do not paste long documentation excerpts; summarize only the evidence needed.

## Change safety

- Do not modify business code, project configuration, database schemas, or data without explicit user approval.
- A request to analyze, diagnose, or suggest code is not permission to edit files.
- Before a requested edit, state the exact files and scope; after an approved edit, list every file changed.

## Data-chain dependency rule

- For DeepFOS financial-model calculations with dependent target items, do not flatten the entire dependency chain into one in-memory calculation.
- Calculate each dependency level separately, save it, then re-query the latest cube data before calculating the next level.
- Preserve the required execution order and point out the dependency explicitly in code comments and in the response.
- Before changing such code, proactively remind the user that sequential save-and-requery is required; performance optimizations must not bypass data consistency.

## Usage-based skill suggestions

After a substantive DeepFOS Python task, review reusable workflows with:

`agent/bin/deepfos-agent review --json`

To append a new pattern, first state the exact content and impact, then obtain user approval before editing `deepfos-knowledge/usage-patterns.jsonl`.

- At 3 occurrences, briefly suggest creating a dedicated skill; do not create it without approval.
- Do not log trivial, one-off, sensitive, or purely conversational requests.

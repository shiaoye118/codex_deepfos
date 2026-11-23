# DeepFOS agent CLI specification

## Contract

Executable: `agent/bin/deepfos-agent`

Every command returns one JSON object on stdout:

```json
{"ok":true,"data":{},"error":null}
```

```json
{"ok":false,"data":null,"error":{"code":"E_USAGE","message":"..."}}
```

`--json` is accepted for compatibility. `--pretty` pretty-prints without changing the schema.

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | Command completed and returned a success envelope |
| 1 | Unexpected internal failure |
| 2 | Invalid arguments |
| 3 | Permission denied |
| 4 | Local lookup or index failure |
| 5 | External dependency failure |
| 130 | Interrupted |

## Commands

### `describe`

Returns the project manifest and resolved runtime paths.

### `doctor`

Returns a `healthy` flag, critical/warning checks, and document/symbol counts. A missing SDK source is a warning, not a critical failure.

### `docs QUERY [--limit N]`

Searches the local product-document index. Returns title, route, path, and a bounded excerpt. Default limit is 5.

### `symbols QUERY [--limit N]`

Searches exact and lexical SDK symbol records. Returns kind, qualified name, module, arguments, async flag, and bounded documentation. Default limit is 5.

### `source QUERY [--limit N] [--max-per-file N] [--project]`

Searches installed SDK source. `--project` explicitly adds `DEEPFOS_PROJECT_ROOT`. Defaults: 80 result lines and 3 matches per file.

### `review`

Reads `deepfos-knowledge/usage-patterns.jsonl` and reports reusable patterns. A pattern at 3 occurrences is marked `suggest_skill: true`; it does not create a Skill.

### `version`

Returns installed SDK metadata and the locally cached documentation version. It makes no network request.

## Safety invariants

- No network calls.
- No writes to business data, configuration, knowledge files, or external systems.
- No implicit scan of business-code roots.
- No secrets or credentials are read intentionally.
- All paths resolve from the project first; environment variables are explicit overrides.
- Normal lookup output is bounded to avoid loading the full corpus.

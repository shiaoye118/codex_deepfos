# Project agent entry

Read `AGENTS.md` first. It is the canonical project instruction file.

Use the project-local read-only adapter for DeepFOS research:

```bash
agent/bin/deepfos-agent describe --json
agent/bin/deepfos-agent doctor --json
agent/bin/deepfos-agent docs "<keywords>" --json
agent/bin/deepfos-agent symbols "<Class.method>" --json
agent/bin/deepfos-agent source "<source pattern>" --json
agent/bin/deepfos-agent review --json
```

Do not depend on global Codex Skills or absolute home-directory paths. The adapter and `deepfos-knowledge/` are part of this project. Do not scan business-code roots or make external changes unless the user explicitly authorizes that exact action.

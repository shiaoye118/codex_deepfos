# codex_deepfos

DeepFOS Python SDK、产品文档、FH 历史代码画像和 API 参考资料的离线项目。

## 快速开始

```bash
agent/bin/deepfos-agent doctor --json
agent/bin/deepfos-agent docs "财务模型 保存" --json
agent/bin/deepfos-agent symbols "AsyncFinancialCube.query" --json
agent/scripts/smoke-test.sh
```

## 目录

- `AGENTS.md`：Codex 及兼容 agent 的规范入口。
- `agent/`：可迁移 CLI、JSON 工具规范、交接状态和本地 Skill。
- `deepfos-knowledge/`：DeepFOS SDK 1.1.94 与产品文档的本地索引。
- `queryAssetDepreciationExpect.postman_collection.json`：接口调研样例；变量值应为空。

## 代码范围

业务代码不存放在本项目内。分析代码前必须先确认准确根目录，不得默认扫描本机其他项目。`agent/bin/deepfos-agent source` 默认只查已安装 SDK；只有显式传入 `--project` 才查本项目源码。

## 迁移原则

所有普通查询应通过 `agent/bin/deepfos-agent`，并读取 `agent/HANDOFF.md` 获取当前迁移状态。内置命令只读、不联网、不修改业务数据或外部系统。

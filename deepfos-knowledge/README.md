# DeepFOS Knowledge Base

本目录保存对 DeepFOS Python SDK 1.1.94 源码及 `docs.deepfos.com` 公共文档的持久化学习索引。

## 来源

- SDK 包：`/Users/theo/Documents/Python_Sdk/deepfos-1.1.94.tar.gz`
- SHA-256：`dec08b577646db4f5ff00d94c55688a94981a04a9c2e36279462aaab42a26f5c`
- 官网：[docs.deepfos.com](https://docs.deepfos.com/)
- Python SDK 在线文档：[py.deepfos.com](http://py.deepfos.com)

## 文件

- `sdk-1.1.94.md`：SDK 架构、核心模式、主要元素和版本兼容性。
- `product-docs-overview.md`：DeepFOS 产品及开发者文档知识地图。
- `source-symbols.json`：从 1.1.94 源码 AST 提取的类、函数、方法及签名索引。
- `docs-catalog.json`：493 个新版产品/开发者页面的标题、路径、章节和正文长度索引。
- `docs-routes.json`：文档 URL 到本地 slug 的映射。
- `docs-corpus.jsonl`：493 个文档页面的结构化正文，每行一个 JSON 文档。

## 使用原则

1. SDK 1.1.94 的源码是代码签名和行为的最终依据。
2. `docs.deepfos.com` 用于理解当前产品能力、组件协同配置和推荐实践。
3. 当官网示例与 1.1.94 源码不一致时，优先使用 1.1.94 源码，并在代码中说明版本差异。
4. `docs-corpus.jsonl` 是抓取时快照，不代表文档永远最新。

## 本地检索工具

`deepfos-index.sqlite` 是对上述文档和 SDK 符号索引生成的本地 SQLite FTS5 索引。它用于按关键词检索文档、按方法名查询签名，避免每次加载整份 JSON/JSONL。

```bash
# 查询产品文档
agent/bin/deepfos-agent docs "财务模型 保存" --json

# 查询 SDK 符号和方法签名
agent/bin/deepfos-agent symbols "AsyncFinancialCube.query" --json

# 查询已安装 SDK 源码
agent/bin/deepfos-agent source "def save_unpivot" --json
```

索引已随项目提交。缺少索引时先报告问题，不要自动重建或修改知识库。

## 使用模式与 Skill 建议

可复用工作流记录在 `usage-patterns.jsonl`：

```bash
agent/bin/deepfos-agent review --json
```

同一模式出现 3 次及以上时，`review` 会标记为建议新增专用 Skill。该阈值只是提醒条件，不会自动创建 Skill。需要新增记录时，先说明拟追加内容和影响并取得用户确认。

## 版本感知

本地安装的 SDK 与官网最新文档可能不同。检查版本：

```bash
agent/bin/deepfos-agent version --json
```

- 项目内 CLI 只读取本地缓存，不联网。
- 当前项目能否运行以本地已安装 SDK 和项目代码为准。
- 新版本建议只作为升级参考，并明确标注。

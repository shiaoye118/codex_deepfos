# DeepFOS Python SDK 1.1.94

## 包信息

- `deepfos.__version__ = "1.1.94"`
- `deepfos.__product_version__ = "3.0.0"`
- Python 要求：`>=3.8.3`
- 包内约 173 个 `.py` 文件，约 70,751 行 Python 代码。
- 静态 `compileall` 检查通过。

## 分层

### `deepfos.api`

Open API 封装、路由、请求装饰器和 Pydantic DTO/VO。常用基类：

- `RootAPI`：固定 URL API。
- `DynamicRootAPI`：按组件版本和服务发现动态解析 URL。
- `ChildAPI`：固定地址 API 的子路由。
- `get` / `post`：声明接口方法和请求参数。

同步 API 默认 `sync=True`；`sync=False` 的 `DynamicRootAPI` 必须异步初始化，其方法使用 `await`。

### `deepfos.element`

- 变量：`Variable` / `AsyncVariable`
- 维度：`Dimension` / `AsyncDimension`
- 财务模型：`FinancialCube` / `AsyncFinancialCube`
- 业务模型：`BusinessModel` / `AsyncBusinessModel`
- 数据表：`DataTableMySQL`、`DataTableClickHouse`、`DataTableOracle`、`DataTableSQLServer`、`DataTableKingBase`、`DataTableGauss`、`DataTableDaMeng`、`DataTablePostgreSQL`、`DataTableDeepEngine`、`DataTableDeepModel` 及异步版本。
- 事实表：`FactTable` / `AsyncFactTable`
- 值列表：`SmartList` / `AsyncSmartList`
- 权限方案：`RoleStrategy` / `AsyncRoleStrategy`
- 审批流：`ApprovalProcess` / `AsyncApprovalProcess`
- 工作流：`WorkFlow` / `AsyncWorkFlow`
- 数据流 3.0：`DeepPipeline` / `AsyncDeepPipeline`
- DeepModel：`DeepModel` / `AsyncDeepModel`
- 凭证模型：`JournalModel` / `AsyncJournalModel`
- 单据模板：`JournalTemplate` / `AsyncJournalTemplate`
- 会计/单据引擎：`AccountingEngines`、`BillEngines`、`AccountingEventType`
- 对账：`ReconciliationEngine`、`ReconciliationMsEngine`
- Python 元素任务：`PythonScript`
- 连接器 3.0：`DeepConnector`

元素基类 `ElementBase` 负责：

- 按 `element_name` + `folder_id` 或 `path` 定位元素。
- 解析组件版本和服务名。
- 自动创建同步 `api` 和异步 `async_api`。
- 元数据通过 `future_property` 按需异步加载。

### `deepfos.core`

- `SysCube`：成员公式、`fix()`、自动汇总和计算结果提交。
- `SysDimension`、`DimMember`、`DimExprAnalysor`：维度表达式和成员树。
- `BaseTable`、`MetaTable`、`SQLCondition`、`TreeRenderer`：逻辑表和查询条件。

### `deepfos.db`

- 同名同步/异步数据库客户端。
- 通用能力：`query_dfs()`、`exec_sqls()`、`insert_df()`。
- SQL 中的 `${element_name}` 可解析为数据表真实表名。
- 多句 `exec_sqls()` 以事务执行；ClickHouse 和事实表不支持事务。

### `deepfos.lib`

重要能力包括：

- `ThreadCtxExecutor`、`ParallelProxy`、`compute`
- `synchronize`、`future_property`、`FuturePropertyMeta`
- `dict_to_expr`、`expr_to_dict`、`retry`、`split_dataframe`
- `ParamZipHelper`、`TaskUtil`、`export_file_for_download`
- `as_datasource`（DeepUX / 图表数据源）
- DeepFos Logger、Redis、消息、子任务和通用装饰器

## 同步、异步和并发

- 元素和 DB 均有 `Async*` 实现。
- 同步元素由 `SyncMeta` 对 `synchronize` 元组中的异步方法进行包装。
- `OPTION.general.parallel_mode = True` 时，同步调用可能返回 `ParallelProxy`。
- 需要确保结果实际取回或保证执行顺序时使用 `compute(proxy)`。
- 所有网络 API 可设为异步模式。
- 异步元素中涉及网络 IO 的方法应使用 `await`。

## 关键全局配置

- `OPTION.api.timeout`：API 默认超时，默认 180 秒。
- `OPTION.api.verify_ssl`：SSL 校验。
- `OPTION.api.dump_on_failure` / `dump_always`：输出 curl 调试信息。
- `OPTION.general.parallel_mode`：同步调用的协程并发模式。
- `OPTION.general.preserve_concurrency`：并发保留配置。
- `OPTION.general.locale`：语言环境。
- `OPTION.edgedb.dsn` / `timeout`：DeepModel 直连。
- `OPTION.discovery.enabled` / `implementation` / `cache_strategy` / `take_over`：服务发现。
- 服务发现实现支持 `local`、`eureka`、`nacos`、`k8s`。
- `OPTION.boost.skip_internal_existence_check`：跳过元素内部存在性检查，优化性能。

## 重要行为

### 数据表

- `DataTable*` 写操作通常立即执行。
- 事务语义使用 `with table.start_transaction():`。
- `select()` 返回 `DataFrame`；`select_raw()` 返回原始查询结果。
- `table` 是 pypika `Table`，用于构造条件。
- `DataTableDeepModel.insert_df()` 支持 `conflict_target`。
- 1.1.94 的 `DataTableMySQL.insert_df()` 只有 `updatecol`、`chunksize`、`auto_fit`，不直接接受 `conflict_target`。

### 维度

- `add_member`、`delete_member`、`update` 等先修改内存。
- 必须调用 `save()` 才提交。
- `query(expression, fields=..., as_model=...)` 查询成员。
- 支持子集 CRUD、成员别名、`update_parent`、`load_dataframe`、同步 DeepModel 等功能。

### 变量

1.1.94 的真实签名：

```python
Variable.add_text(name, value=None, description=None, is_global=False, is_customize_value=True, length=255)
Variable.add_number(name, value=None, description=None, is_global=False, is_customize_value=True, ...)
Variable.add_dimension(name, dim, dim_expression, value=None, description=None, ...)
Variable.get_value(name, is_customize_value=True, default=UNSET, auto_cast=True, obj_hook=None)
```

新增、修改、删除变量后调用 `save()`。

### 财务模型

- `query()` 默认返回 `(DataFrame, pov)`，`compact=False` 时合并 POV 到 DataFrame。
- 支持 `pivot_dim`、`pivot_members`、`return_alias`。
- `save()`、`save_unpivot()`、`complement_save()`、`complement_save_unpivot()`。
- `delete()`、`delete_with_mdx()`、`insert_null()`。
- `copy_calculate()`、`mdx_execution()`、`mdx_execution_with_code()`。
- 支持块级 `before_chunk` / `after_chunk` 回调。

### 业务模型

- `logic_tables` 暴露模型逻辑表；`MetaTable.lock()` 和 `.data` 管理锁定条件与查询。
- `save()` 支持多表 DataFrame 映射。
- 支持 `copy_rows()`、审批流设置和模型权限对象。

### DeepModel

- 默认 `direct_access=True`，但只有设置 `OPTION.edgedb.dsn` 时才真正直连。
- 核心方法：`query()`、`query_object()`、`query_df()`、`execute()`、`get_object()`。
- 批量方法：`insert_df()`、`insert_df_pg()`、`update_df()`。
- DML 通过事务执行，可用 `start_transaction()`。
- 支持 `with_globals()` / `without_globals()`。
- `relation` 是 DataFrame 映射，用于 multi link：至少包含 `source`、`target`，可附加 link property 列。
- 1.1.94 新增默认注入当前模块 global：`{space}::current_module = app{app_id}`。
- 无效或缺少必填字段会抛 DeepModel 异常。

### 工作流

- 启动使用 `launch_process()`；批量使用 `batch_launch_process()`。
- 查询流程/任务支持启动参数、业务键和状态。
- `complete_task_by_id()` 支持 `outcome`、`comment`、`extra_res_params`、`attachments`。
- 消息使用 `broadcast()` 或 `send_msg_to_processes()`。

### 数据流

- `run()` 为同步执行，`run_async()` 返回 run_id，`result()` 获取结果，`run_batch()` 批量。
- 1.1.94 中同步 `run()` 固定为不带启停的进程内执行；传入 `in_process=False` 只会警告，不改变行为。
- 只有存在已审批发布版时才能运行。

### 凭证

- `JournalModel` 围绕头表、行表和 `_type` 保存/更新/校验/查询/过账。
- `JournalTemplate` 使用 `new_query()`、`batch_save()`、`batch_query()`、`get_posting()` 等接口。
- 复杂过账参数使用 `FullPostingParameter`。

## 官网与 1.1.94 的显著差异

以下官网示例不应直接当成 1.1.94 代码：

1. 官网变量新增示例使用 `default_value=`；1.1.94 使用 `value=`。
2. 官网维度变量示例使用 `dimension_name=`；1.1.94 使用 `dim` 对象和 `dim_expression=`。
3. 官网部分示例写 `get_value(..., is_customize_value=False)` 为默认；1.1.94 的实际默认值是 `True`。
4. 官网 DataTableMySQL 示例使用 `conflict_target=`；1.1.94 的 `DataTableMySQL` 不接收该参数，DeepModel 数据表才支持。
5. 旧工作流示例中的 `launch()` 应写为 `launch_process()`。

## 异常

主要基类：

- `DeepfosBaseException`
- `APIError` / `APIRequestError` / `APIResponseError`
- `ElementError` / `ElementNotFoundError` / `ElementAmbiguousError`
- `DimensionSaveError` / `MemberNotFoundError`
- `VariableCreateError` / `VariableUpdateError`
- `DeepModelError` 系列
- `JournalModelError` 系列
- `PyTaskError` 系列
- `DeepPipelineRunError` 系列

业务集成应记录 `element_name`、`task_id` / `run_id`、`proc_inst_id`、请求参数和 `APIResponseError.code`。

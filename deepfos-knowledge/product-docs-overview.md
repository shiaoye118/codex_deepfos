# DeepFOS 产品与开发文档知识地图

## 产品定位

DeepFOS 是企业级应用底座和工作台，不是单一业务系统。平台统一管理企业、空间、应用、组件、元素、成员、用户组、角色、菜单、权限、SSO、API Key、文件和网关边界；具体业务规则由应用或组件承担。

## 当前文档结构

### 平台

- 企业与空间
- 应用生命周期、组件注册、元素和菜单
- 成员、用户组、角色和权限模型
- SSO、用户同步、API Key、网关、License、日志和故障排查

### 数据与模型

- DeepModel：对象、属性、链接、DeepQL、对象分析、数据重写、触发器、业务规则、自增序列、迁移。
- 领域模型：基于 DeepModel 对象与链接形成的业务领域，包含模型视图、领域动作和访问策略。
- 维度：层级主数据、UD、权限、子集、指标公式、维度表达式、多版本实体维。
- 财务模型：多维数据存储、汇总、权限、子模型、数据审计、批注附件、拷贝计算和合并报表。
- DeepCube：基于 Python 的财务模型计算 SDK，适合复杂计算、范围计算、跨 Cube 计算和大计算量场景。
- 分析主题：聚合财务模型子模型，供普通用户创建个人报表。

### 展现

- DeepUX：低代码页面、数据源、页面变量、表达式、事件动作、清单表、表单、图表和自定义组件。
- DeepTable：电子表格 2.0，包含工作簿、工作表、筛选器、动态表、DF 函数、大纲树、快速填充和分发下载。
- 图表和 Python DataFrame 数据源：`deepfos.lib.deepchart.as_datasource`。
- DeepUX Python DataFrame 数据源：`deepfos.lib.deepux.as_datasource`。

### 集成与流程

- 连接器：数据库和 API 连接信息管理。
- 数据流 3.0：画布式数据查询、转换、组件调用、流程控制和发布调度。
- 单据引擎 3.0：基于领域模型实现单据转换和凭证生成。
- 工作流：BPMN、表单/UX 任务、全局变量、消息、子流程、批量启动和监控。
- Python 2.0：在线编辑、文件上传、运行参数、Celery 队列、前置/后置逻辑和按钮逻辑。

## 开发者中心

### API

- 变量、维度、财务模型、数据表、工作流、数据流、凭证三件套。
- 统一 JSON 响应通常为 `{status, code, message, data}`。
- Python 同步运行接口的成功响应直接返回脚本 return 值，不使用统一包装。

### Python SDK

- 变量
- 维度
- 财务模型
- DataTable 与数据库客户端
- 工作流
- 数据流
- 凭证模型和单据模板

### 其他开发者资源

- UX1 自定义组件
- 电子表格自定义 JS
- 本地页面联调
- DeepFos Logger
- DeepFOS 文档 MCP

## DeepQL 核心

- `select Obj { prop, link: { ... } }`
- `filter`、`order by ... then ...`、`limit`、`offset`
- 正向链接：`.link`
- 反向链接：`.<link[is Type]`
- 计算字段：`alias := expression`
- 参数：`<type>$name`，Python 端以 `dm.query(ql, name=value)` 传入。
- 多语言字段：`<str>.name['zh-cn']`
- 聚合：`count`、`sum`、`min`、`max`、`math::mean`
- 条件：`if ... else ...`、空值 `??`
- 层级：`cal::base`、`cal::ibase`、`cal::descendant`、`cal::idescendant`、`cal::ancestor`、`cal::iancestor`
- 业务主键快捷字段：`.__bk__`
- `with` 和子查询适合复用查询与参数化。
- `group` 保留 `key`、`grouping`、`elements`，支持 ROLLUP / CUBE。

## 平台集成关系

- Python 可以读取变量、维度、财务模型、DataTable/数据库、DeepModel、工作流、数据流和凭证。
- DeepUX 可以调用 Python DataFrame 数据源。
- 数据流可调用 Python 脚本、DeepModel、财务模型、维度、数据表、连接器、工作流和 HTTP API。
- 工作流与 UX 协作处理待办页面、审批和数据回写。
- DeepModel 与数据表、维度可建立视图对象或同步关系。

## 当前产品版本线索

- 2026 Q2 发布说明对应平台 v3.8。
- 数据流新增财务模型分摊节点、财务模型数据复制、全局异常自定义处理、批量同步调用、AI 辅助。
- 工作流增强父子流程查看、附件在线预览、流程监控和批量启动。
- 电子表格增强管理页面、快速填充、分发下载。

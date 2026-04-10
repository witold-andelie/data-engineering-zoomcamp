# 金融量化端到端数据工程项目设计（含 OPM + CI/CD + 云模块 + 批流一体）

## 1. 项目目标
构建一个**面向金融量化场景**的端到端数据平台，产出一个含 **2 个核心 Tile** 的可视化 Dashboard，并满足课程项目要求：

1. 选择并接入数据集（实时 + 批量）
2. 建立数据落地到 Data Lake 的管道
3. 建立从 Lake 到 Data Warehouse 的管道
4. 在仓库内建模（可用于可视化）
5. 构建可视化 Dashboard
6. 必须具备 CI/CD、云计算模块、明确区分批处理与实时处理

---

## 2. 业务主题与数据集选择（金融量化）

### 2.1 推荐主题
**“加密资产/股票市场微观结构监控与因子看板”**

### 2.2 数据源（建议双通道）
- **实时流数据（Streaming）**：交易所 WebSocket（如 Binance trades / bookTicker）
- **批量数据（Batch）**：交易所 REST Kline（1m/5m/1h）和参考信息（symbol metadata）

这样可以自然体现：
- 实时链路负责“分钟级/秒级监控”
- 批处理链路负责“历史回补 + 每日重算 + 低成本归档”

---

## 3. Dashboard 设计（2 个 Tile）

### Tile A：**实时市场脉冲（Realtime Pulse）**
- 指标：
  - 最新价格、1m 收益率、成交量突变（z-score）
  - 实时买卖盘不平衡（可选）
- 更新频率：10s ~ 30s
- 数据来源：BigQuery 中的 streaming 表（由 Dataflow/Flink 持续写入）

### Tile B：**因子与风险概览（Factor & Risk）**
- 指标：
  - 日级波动率（rolling std）
  - 动量因子（过去 N 日收益）
  - 最大回撤 / Sharpe（简化版）
- 更新频率：每小时/每日
- 数据来源：dbt 建模后的 mart 层

---

## 4. 端到端架构（与你给的 Mermaid 一致化）

你给出的流程非常完整，可落地为三层：

1. **Dev & OPM 层**：本地开发、质量门禁、构建、发布、部署
2. **Platform 层（Cloud + IaC + K8s）**：Terraform 创建 GCP 资源、GKE 承载服务
3. **Data 层（Stream + Batch）**：Pub/Sub + Dataflow + Airflow + BigQuery + dbt + Streamlit

关键路径：
- 实时：`WebSocket -> collector -> Pub/Sub -> Dataflow -> BigQuery -> Streamlit`
- 批量：`REST -> Airflow -> GCS(raw) -> BigQuery(staging) -> dbt -> marts -> Streamlit`

---

## 5. 批处理 vs 实时处理（必须明确）

| 维度 | 实时处理（Streaming） | 批处理（Batch） |
|---|---|---|
| 目标 | 低延迟监控、告警 | 稳定重算、全量一致性 |
| 触发方式 | 事件驱动（持续） | 时间调度（小时/天） |
| 典型工具 | Pub/Sub + Dataflow/Flink | Airflow + Spark/SQL |
| 数据特征 | 高频、小批次、乱序可能 | 大批量、边界清晰 |
| 成本模型 | 常驻计算成本 | 定时计算成本 |
| 金融场景示例 | 分钟级异动检测 | 每日因子重算与回测输入 |

**项目建议**：
- 同时实现两条链路（课程展示更完整）
- 在 dashboard 上用标签标注数据 freshness（例如 `realtime <= 1 min`, `batch D-1`）

---

## 6. OPM（ObjectJS/opm）方法论落地

将 OPM 作为工程流程“总入口”（而非只当命令工具）：

### 6.1 统一命令面
- `opm install`：安装依赖、初始化开发环境
- `opm compile`：统一 lint/typecheck/dbt compile
- `opm build`：构建数据服务镜像
- `opm publish`：推送镜像到 Artifact Registry
- `opm deploy`：触发 Terraform + GitOps 发布

### 6.2 质量门禁策略
在 OPM 流程中定义分层门禁：
1. 代码质量：ruff/black/mypy
2. 数据质量：dbt test（not_null, unique, accepted_values）
3. 合约质量：schema contract / 数据字典校验
4. 部署质量：镜像扫描 + manifests 校验

### 6.3 与 CI/CD 对齐
GitHub Actions 只调用 OPM 命令，避免脚本分叉：
- CI job: `opm compile` + `pytest` + `dbt compile`
- CD job: `opm build` + `opm publish` + `opm deploy`

---

## 7. 云计算模块（GCP）

### 7.1 Terraform 资源清单（最小可行）
- GKE Cluster（运行 collector/airflow/streamlit）
- Artifact Registry（镜像仓库）
- Pub/Sub topics/subscriptions（实时总线）
- Cloud Storage buckets（raw/backup）
- BigQuery dataset + 表（staging/core/marts）
- IAM Service Accounts + 最小权限策略
- Monitoring/Alert Policies

### 7.2 为什么这是“云模块”而非本地拼装
- 资源弹性（Dataflow autoscaling）
- 托管服务减少运维负担
- 与 CI/CD、IAM、监控天然集成

---

## 8. CI/CD 设计（必选项）

### 8.1 分支策略
- `feature/*` -> PR -> `main`
- PR 必须通过 CI 检查（required checks）

### 8.2 GitHub Actions 工作流（建议 3 条）
1. `ci.yml`
   - 单元测试、静态检查、dbt compile/test（可用样本数据）
2. `build_publish.yml`
   - 构建镜像并推送 Artifact Registry（仅 main/tag）
3. `deploy_gitops.yml`
   - 更新 GitOps 仓库 image tag，触发 Argo CD 同步

### 8.3 CD + 回滚
- 正常发布：Argo CD 自动对齐 Git 状态
- 故障回滚：
  - Argo CD app rollback
  - `kubectl rollout undo`（快速止血）

---

## 9. Kubernetes（强烈建议）

在 GKE 中部署：
- `collector` Deployment（接实时行情）
- `streamlit` Deployment + Service + Ingress
- `airflow`（Helm 部署或独立命名空间）

实践建议：
- HPA：collector/streamlit 按 CPU 或自定义指标扩缩
- 配置管理：ConfigMap + Secret
- 命名空间隔离：`data-platform`, `observability`

---

## 10. 数据模型分层（BigQuery + dbt）

- **staging**：原始结构轻清洗（字段标准化、时间戳统一）
- **core**：统一事实表（trades, klines）
- **marts**：面向看板（realtime_metrics, factor_daily）

dbt 关键点：
- 增量模型（incremental）降低成本
- 分区分簇（按交易日期 + symbol）
- tests + exposures 连接 dashboard 血缘

---

## 11. 12 周落地计划（可直接当项目排期）

- **Week 1-2**：选题 + 数据源 PoC + Terraform 基础资源
- **Week 3-4**：实时采集链路（collector -> Pub/Sub -> BQ）
- **Week 5-6**：批处理链路（Airflow -> GCS -> BQ）
- **Week 7-8**：dbt 模型 + 数据质量测试
- **Week 9**：Streamlit 双 Tile 看板
- **Week 10**：CI/CD + GitOps + Argo CD
- **Week 11**：监控告警 + 回滚演练 + 压测
- **Week 12**：文档固化 + 演示脚本 + 成本复盘

---

## 12. 项目验收清单（对照课程要求）

- [ ] 有明确数据集与业务问题（金融量化）
- [ ] 有 Data Lake（GCS）
- [ ] 有 Warehouse（BigQuery）
- [ ] 有批处理链路（Airflow）
- [ ] 有实时链路（Pub/Sub + Dataflow）
- [ ] 有 dbt 转换与测试
- [ ] 有 2 个 Tile 的可视化 Dashboard
- [ ] 有 IaC（Terraform）
- [ ] 有 CI/CD（GitHub Actions + Argo CD）
- [ ] 有 OPM 统一研发流程

---

## 13. 你下一步可以直接执行的最小启动命令（示例）

1. 初始化项目骨架与依赖：`opm install`
2. 本地质量检查：`opm compile`
3. 运行单测：`pytest`
4. dbt 编译：`dbt compile`
5. 构建镜像：`opm build`
6. 推送镜像：`opm publish`
7. 部署开发环境：`opm deploy`

> 如果你愿意，我下一步可以基于这个设计给你输出：
> - `terraform/` 目录结构模板
> - `airflow` DAG 样板
> - `dbt` 模型与 tests 样板
> - `GitHub Actions` 三个 workflow 的可运行初版

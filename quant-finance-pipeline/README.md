# Quant Finance Data Platform (Modular Build)

本目录用于按模块逐步落地你的端到端金融量化数据工程项目。

## 模块化路线图

- Module 01：OPM 方法论与工程骨架（已完成）
  - OPM 产物（系统上下文、数据生命周期、部署回滚、责任矩阵）
  - 数据契约（trade event JSON Schema）
  - OPM 一致性检查脚本
- Module 02：基础云资源 Terraform（GCP：GCS/BQ/PubSub）（已完成）
- Module 03：实时采集链路（collector -> Pub/Sub）（已完成）
- Module 04：流处理链路（Dataflow -> BigQuery）（已完成）
- Module 05：批处理链路（Airflow -> GCS -> BigQuery）（已完成）
- Module 06：dbt 分层建模与 alpha 因子（已完成）
- Module 07：Streamlit 双 Tile 看板（已完成）
- **Module 08（当前）**：CI/CD + GitOps + Argo CD

## 当前模块（Module 01）内容

1. `opm/system-context.opm.md`
2. `opm/data-lifecycle.opm.md`
3. `opm/deployment-process.opm.md`
4. `opm/ownership-matrix.md`
5. `contracts/trade_event.schema.json`
6. `scripts/check_opm_consistency.py`

## 快速使用

```bash
python3 scripts/check_opm_consistency.py
```

该脚本会检查 OPM 文档和数据契约文件是否齐备，作为后续 CI 的前置门禁。

## 新增模块（Module 03）内容

1. `collector/app.py`
2. `collector/requirements.txt`
3. `collector/Dockerfile`
4. `collector/.env.example`
5. `collector/README.md`

## 新增模块（Module 04）内容

1. `streaming-dataflow/pipeline.py`
2. `streaming-dataflow/requirements.txt`
3. `streaming-dataflow/README.md`

## 新增模块（Module 05）内容

1. `batch-airflow/dags/market_batch_ingest_dag.py`
2. `batch-airflow/requirements.txt`
3. `batch-airflow/README.md`

## 新增模块（Module 06）内容

1. `dbt-quant/dbt_project.yml`
2. `dbt-quant/profiles.yml.example`
3. `dbt-quant/models/staging/stg_trade_events_stream.sql`
4. `dbt-quant/models/staging/schema.yml`
5. `dbt-quant/models/marts/fct_alpha_factors_daily.sql`
6. `dbt-quant/models/marts/schema.yml`
7. `dbt-quant/README.md`

## 新增模块（Module 07）内容

1. `dashboard-streamlit/app.py`
2. `dashboard-streamlit/requirements.txt`
3. `dashboard-streamlit/.env.example`
4. `dashboard-streamlit/README.md`

## 新增模块（Module 08）内容

1. `.github/workflows/quant_ci.yml`
2. `.github/workflows/quant_build_publish.yml`
3. `.github/workflows/quant_deploy_gitops.yml`
4. `gitops/base/collector-deployment.yaml`
5. `gitops/base/dashboard-deployment.yaml`
6. `gitops/apps/quant-platform-app.yaml`
7. `gitops/README.md`

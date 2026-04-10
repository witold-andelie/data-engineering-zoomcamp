# Module 05 - Batch Pipeline (Airflow -> GCS -> BigQuery)

该模块提供批处理链路骨架：

`REST API -> Airflow DAG -> GCS(raw) -> BigQuery(staging)`

## 文件

- `dags/market_batch_ingest_dag.py`：每日批处理 DAG

## DAG 流程

1. `extract_rest_to_gcs`
   - 调用 Binance Kline REST API
   - 按执行日抽取数据
   - 落地到 GCS `raw/klines/dt=YYYY-MM-DD/*.json`
2. `load_gcs_to_bq`
   - 从 GCS 读取 JSONL
   - 加载到 BigQuery staging 表

## 必需环境变量（Airflow worker）

- `QF_BATCH_SYMBOL`（默认 `BTCUSDT`）
- `QF_BATCH_INTERVAL`（默认 `1m`）
- `QF_BATCH_GCS_BUCKET`
- `QF_BATCH_BQ_TABLE`（`project.dataset.table`）

## 调度

- 默认每日 UTC 01:00 运行
- 可在 DAG 定义里修改 `schedule`


# Module 04 - Dataflow Streaming Pipeline (Pub/Sub -> BigQuery)

该模块使用 **Apache Beam + Dataflow Runner** 实现实时处理链路：

`Pub/Sub subscription -> parsing/validation -> windowing -> BigQuery`

## 输入输出

- **Input**: Pub/Sub subscription（来自 collector 的 TradeEvent JSON）
- **Output**: BigQuery `staging.trade_events_stream`

## 运行参数

- `--project`: GCP project id
- `--region`: GCP region
- `--runner`: `DataflowRunner`（云端）或 `DirectRunner`（本地）
- `--temp_location`: Dataflow 临时目录（GCS）
- `--staging_location`: Dataflow staging 目录（GCS）
- `--subscription`: Pub/Sub subscription 全名
- `--output_table`: BigQuery 目标表（`project:dataset.table`）

## 本地调试（DirectRunner）

```bash
pip install -r requirements.txt
python pipeline.py \
  --runner DirectRunner \
  --subscription projects/<project>/subscriptions/trade-events-stream-sub \
  --output_table <project>:qf_dev_staging.trade_events_stream
```

## Dataflow 运行（DataflowRunner）

```bash
python pipeline.py \
  --project <project> \
  --region us-central1 \
  --runner DataflowRunner \
  --temp_location gs://<bucket>/dataflow/temp \
  --staging_location gs://<bucket>/dataflow/staging \
  --subscription projects/<project>/subscriptions/trade-events-stream-sub \
  --output_table <project>:qf_dev_staging.trade_events_stream
```

## 处理逻辑

1. 读取 Pub/Sub JSON
2. 字段校验与类型转换（price/quantity/event_time）
3. 失败记录打日志（可扩展 dead-letter topic）
4. 固定窗口（60 秒）聚合批写入 BigQuery


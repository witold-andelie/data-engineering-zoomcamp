# Module 03 - Realtime Collector (WebSocket -> Pub/Sub)

该模块实现实时采集服务（collector），负责：

1. 从交易所 WebSocket 接收成交事件
2. 映射到统一 `TradeEvent` 契约
3. 发布到 Pub/Sub（或本地 stdout 方便调试）

## 环境变量

- `SOURCE_WS_URL`：WebSocket 地址（默认 Binance trade stream）
- `SOURCE_SYMBOL`：交易对，如 `btcusdt`
- `PUBSUB_TOPIC`：GCP Pub/Sub topic 全名（例如 `projects/<project>/topics/trade-events`）
- `GCP_PROJECT_ID`：GCP project id（可选，Pub/Sub 客户端常可从 ADC 推断）
- `PUBLISH_MODE`：`pubsub` 或 `stdout`（默认 `stdout`）
- `LOG_LEVEL`：日志级别（默认 `INFO`）

## 本地运行

```bash
pip install -r requirements.txt
python app.py
```

## 容器运行

```bash
docker build -t qf-collector:dev .
docker run --rm -e PUBLISH_MODE=stdout qf-collector:dev
```

> 说明：生产环境请使用 Workload Identity / Service Account 访问 Pub/Sub。

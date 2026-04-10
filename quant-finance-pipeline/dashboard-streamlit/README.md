# Module 07 - Streamlit Dashboard (2 Tiles)

该模块实现课程要求的 2-Tile dashboard：

- Tile A: Realtime Pulse（实时市场脉冲）
- Tile B: Alpha & Risk（alpha 因子和风险）

## 数据来源

BigQuery（建议使用 dbt 产物）：
- `qf_dev_staging.trade_events_stream`
- `qf_dev_marts.fct_alpha_factors_daily`

## 环境变量

- `BQ_PROJECT_ID`（必填）
- `BQ_DATASET_STAGING`（默认 `qf_dev_staging`）
- `BQ_DATASET_MARTS`（默认 `qf_dev_marts`）
- `DASHBOARD_SYMBOL`（默认 `BTCUSDT`）
- `DASHBOARD_LIMIT`（默认 `50`）

## 运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

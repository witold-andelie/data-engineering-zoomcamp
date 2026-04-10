"""Airflow batch DAG: REST -> GCS -> BigQuery."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

import requests
from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.python import PythonOperator
from google.cloud import bigquery, storage

BINANCE_KLINE_URL = "https://api.binance.com/api/v3/klines"


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise AirflowFailException(f"Missing required env: {name}")
    return value


def extract_rest_to_gcs(ds: str, **_: object) -> str:
    symbol = _env("QF_BATCH_SYMBOL", "BTCUSDT")
    interval = _env("QF_BATCH_INTERVAL", "1m")
    bucket_name = _env("QF_BATCH_GCS_BUCKET")

    day = datetime.strptime(ds, "%Y-%m-%d")
    start_ms = int(day.timestamp() * 1000)
    end_ms = int((day + timedelta(days=1)).timestamp() * 1000)

    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000,
    }

    response = requests.get(BINANCE_KLINE_URL, params=params, timeout=30)
    response.raise_for_status()
    rows = response.json()
    if not rows:
        raise AirflowFailException(f"No klines returned for ds={ds}, symbol={symbol}, interval={interval}")

    formatted = []
    for item in rows:
        formatted.append(
            {
                "open_time": item[0],
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
                "close_time": item[6],
                "quote_asset_volume": float(item[7]),
                "number_of_trades": int(item[8]),
                "taker_buy_base_asset_volume": float(item[9]),
                "taker_buy_quote_asset_volume": float(item[10]),
                "symbol": symbol,
                "interval": interval,
                "dt": ds,
            }
        )

    object_name = f"raw/klines/dt={ds}/symbol={symbol.lower()}.jsonl"

    with NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
        for row in formatted:
            tmp.write(json.dumps(row, ensure_ascii=False) + "\n")
        tmp_path = tmp.name

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_filename(tmp_path)

    return f"gs://{bucket_name}/{object_name}"


def load_gcs_to_bq(ti, **_: object) -> None:  # type: ignore[no-untyped-def]
    destination_table = _env("QF_BATCH_BQ_TABLE")
    gcs_uri = ti.xcom_pull(task_ids="extract_rest_to_gcs")
    if not gcs_uri:
        raise AirflowFailException("Missing gcs_uri from upstream task")

    bq_client = bigquery.Client()
    config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        autodetect=True,
    )
    job = bq_client.load_table_from_uri(gcs_uri, destination_table, job_config=config)
    job.result()


with DAG(
    dag_id="market_batch_ingest_dag",
    schedule="0 1 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["quant", "batch", "gcs", "bigquery"],
) as dag:
    extract_task = PythonOperator(
        task_id="extract_rest_to_gcs",
        python_callable=extract_rest_to_gcs,
    )

    load_task = PythonOperator(
        task_id="load_gcs_to_bq",
        python_callable=load_gcs_to_bq,
    )

    extract_task >> load_task

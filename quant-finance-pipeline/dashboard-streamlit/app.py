#!/usr/bin/env python3
"""Streamlit dashboard with two tiles for quant finance project."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from google.cloud import bigquery


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env: {name}")
    return value


@st.cache_resource
def get_bq_client() -> bigquery.Client:
    project = _env("BQ_PROJECT_ID")
    return bigquery.Client(project=project)


def query_realtime_pulse(client: bigquery.Client, project: str, dataset_staging: str, symbol: str, limit: int) -> pd.DataFrame:
    sql = f"""
    select
      event_time,
      symbol,
      price,
      quantity
    from `{project}.{dataset_staging}.trade_events_stream`
    where symbol = @symbol
    order by event_time desc
    limit @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    return client.query(sql, job_config=job_config).to_dataframe()


def query_alpha_risk(client: bigquery.Client, project: str, dataset_marts: str, symbol: str, limit: int) -> pd.DataFrame:
    sql = f"""
    select
      factor_date,
      symbol,
      alpha_score,
      alpha_rank,
      intraday_volatility,
      mom_5d,
      rev_1d
    from `{project}.{dataset_marts}.fct_alpha_factors_daily`
    where symbol = @symbol
    order by factor_date desc
    limit @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("symbol", "STRING", symbol),
            bigquery.ScalarQueryParameter("limit", "INT64", limit),
        ]
    )
    return client.query(sql, job_config=job_config).to_dataframe()


def render_tile_realtime(df: pd.DataFrame) -> None:
    st.subheader("Tile A - Realtime Pulse")
    if df.empty:
        st.warning("No realtime data available for selected symbol.")
        return

    latest = df.iloc[0]
    latest_price = float(latest["price"])
    latest_qty = float(latest["quantity"])

    prev_price = float(df.iloc[1]["price"]) if len(df) > 1 else latest_price
    ret_1_tick = (latest_price / prev_price - 1.0) if prev_price else 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Latest Price", f"{latest_price:,.4f}")
    c2.metric("Latest Qty", f"{latest_qty:,.4f}")
    c3.metric("Tick Return", f"{ret_1_tick:.4%}")

    chart_df = df.sort_values("event_time")[["event_time", "price"]].set_index("event_time")
    st.line_chart(chart_df)


def render_tile_alpha(df: pd.DataFrame) -> None:
    st.subheader("Tile B - Alpha & Risk")
    if df.empty:
        st.warning("No alpha-factor data available for selected symbol.")
        return

    latest = df.iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Alpha Score", f"{float(latest['alpha_score']):.4f}")
    c2.metric("Alpha Rank", f"{int(latest['alpha_rank'])}")
    c3.metric("Intraday Vol", f"{float(latest['intraday_volatility']):.4f}")

    hist = df.sort_values("factor_date").set_index("factor_date")
    st.area_chart(hist[["alpha_score"]])
    st.dataframe(hist[["mom_5d", "rev_1d", "intraday_volatility", "alpha_rank"]].tail(20))


def main() -> None:
    st.set_page_config(page_title="Quant Finance Dashboard", layout="wide")
    st.title("Quant Finance Monitoring Dashboard")

    project = _env("BQ_PROJECT_ID")
    dataset_staging = _env("BQ_DATASET_STAGING", "qf_dev_staging")
    dataset_marts = _env("BQ_DATASET_MARTS", "qf_dev_marts")

    col_left, col_right = st.columns([2, 1])
    with col_left:
        symbol = st.text_input("Symbol", value=_env("DASHBOARD_SYMBOL", "BTCUSDT")).upper()
    with col_right:
        limit = st.number_input("Rows", min_value=10, max_value=1000, value=int(_env("DASHBOARD_LIMIT", "50")), step=10)

    st.caption(f"Last refresh (UTC): {datetime.now(timezone.utc).isoformat()}")

    client = get_bq_client()
    realtime_df = query_realtime_pulse(client, project, dataset_staging, symbol, int(limit))
    alpha_df = query_alpha_risk(client, project, dataset_marts, symbol, int(limit))

    left, right = st.columns(2)
    with left:
        render_tile_realtime(realtime_df)
    with right:
        render_tile_alpha(alpha_df)


if __name__ == "__main__":
    main()

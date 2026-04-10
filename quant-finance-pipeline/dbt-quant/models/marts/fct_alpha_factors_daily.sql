{{ config(materialized='table') }}

with base as (
    select
        symbol,
        trade_date,
        avg(price) as close_px,
        stddev(price) as intraday_volatility,
        sum(quantity) as daily_volume
    from {{ ref('stg_trade_events_stream') }}
    group by 1,2
),
returns as (
    select
        symbol,
        trade_date,
        close_px,
        intraday_volatility,
        daily_volume,
        safe_divide(close_px, lag(close_px, 1) over (partition by symbol order by trade_date)) - 1 as ret_1d,
        safe_divide(close_px, lag(close_px, 5) over (partition by symbol order by trade_date)) - 1 as mom_5d,
        -(safe_divide(close_px, lag(close_px, 1) over (partition by symbol order by trade_date)) - 1) as rev_1d,
        (daily_volume - avg(daily_volume) over (partition by symbol order by trade_date rows between 19 preceding and current row)) /
          nullif(stddev(daily_volume) over (partition by symbol order by trade_date rows between 19 preceding and current row), 0)
          as vol_zscore_20d
    from base
),
scored as (
    select
        *,
        (
          coalesce(mom_5d, 0)
          + coalesce(rev_1d, 0)
          - coalesce(intraday_volatility, 0)
          + coalesce(vol_zscore_20d, 0)
        ) as alpha_score
    from returns
)
select
    symbol,
    trade_date as factor_date,
    close_px,
    intraday_volatility,
    daily_volume,
    ret_1d,
    mom_5d,
    rev_1d,
    vol_zscore_20d,
    alpha_score,
    dense_rank() over (partition by trade_date order by alpha_score desc) as alpha_rank
from scored

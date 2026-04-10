{{ config(materialized='view') }}

select
  cast(event_time as timestamp) as event_time,
  upper(symbol) as symbol,
  cast(price as float64) as price,
  cast(quantity as float64) as quantity,
  cast(source as string) as source,
  cast(ingestion_mode as string) as ingestion_mode,
  cast(trade_id as string) as trade_id,
  cast(side as string) as side,
  date(cast(event_time as timestamp)) as trade_date
from `{{ target.project }}.qf_dev_staging.trade_events_stream`
where event_time is not null

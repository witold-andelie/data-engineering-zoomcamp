# OPM - Data Lifecycle

## Lifecycle States
1. RawIngested
2. SchemaValidated
3. LakePersisted
4. WarehouseLoaded
5. TransformedForAnalytics
6. PublishedToDashboard

## State Transitions
- RawIngested -> SchemaValidated
  - Trigger: contract validation passed
- SchemaValidated -> LakePersisted
  - Trigger: object written to raw bucket
- SchemaValidated -> WarehouseLoaded
  - Trigger: stream/batch writer success
- WarehouseLoaded -> TransformedForAnalytics
  - Trigger: dbt model run success
- TransformedForAnalytics -> PublishedToDashboard
  - Trigger: dashboard cache/materialization refresh

## Data Quality Gates
- Gate A: schema compliance (`contracts/trade_event.schema.json`)
- Gate B: freshness and null checks (warehouse staging)
- Gate C: dbt tests for marts and alpha factors

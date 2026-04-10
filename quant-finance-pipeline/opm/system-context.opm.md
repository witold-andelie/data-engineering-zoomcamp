# OPM - System Context

## Objects
- MarketDataSource
- CollectorService
- PubSubTopic
- StreamProcessor
- DataLakeRawBucket
- WarehouseStaging
- WarehouseMarts
- DashboardService
- MonitoringSystem

## Processes
- IngestRealtimeEvents
- ValidateEventSchema
- PublishEventBus
- ProcessStream
- PersistRawData
- LoadWarehouse
- TransformMarts
- ServeDashboard
- AlertAndRollback

## Object-Process Mapping
- MarketDataSource -> IngestRealtimeEvents -> CollectorService
- CollectorService -> ValidateEventSchema -> PubSubTopic
- PubSubTopic -> ProcessStream -> WarehouseStaging
- CollectorService -> PersistRawData -> DataLakeRawBucket
- WarehouseStaging -> TransformMarts -> WarehouseMarts
- WarehouseMarts -> ServeDashboard -> DashboardService
- MonitoringSystem -> AlertAndRollback -> DeploymentState

## States
- Raw
- Validated
- Curated
- MartReady
- Served

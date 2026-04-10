# OPM Ownership Matrix

| Object / Process | Data Eng | Platform Eng | Analytics Eng | SRE |
|---|---|---|---|---|
| IngestRealtimeEvents | R | C | I | I |
| ValidateEventSchema | R | I | C | I |
| ProcessStream | R | C | I | I |
| PersistRawData | R | C | I | I |
| LoadWarehouse | R | I | C | I |
| TransformMarts (incl. alpha factors) | C | I | R | I |
| ServeDashboard | C | C | R | I |
| AlertAndRollback | I | C | I | R |

- R = Responsible
- C = Consulted
- I = Informed

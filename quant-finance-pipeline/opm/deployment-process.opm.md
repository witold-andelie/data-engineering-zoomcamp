# OPM - Deployment & Rollback Process

## Deployment Process
1. CodeMerged
2. ImageBuilt
3. ImagePushed
4. GitOpsManifestUpdated
5. ArgoSynced
6. RuntimeHealthy

## Rollback Process
1. AlertTriggered
2. IdentifyFailedRelease
3. ArgoRollbackOrRolloutUndo
4. HealthRecheck
5. IncidentClosed

## Process Constraints
- `RuntimeHealthy` requires:
  - collector pod ready
  - dashboard pod ready
  - data freshness SLO met
- Rollback is mandatory if:
  - error budget burn > threshold
  - data delay exceeds SLA

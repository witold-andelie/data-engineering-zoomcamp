output "raw_bucket_name" {
  value       = google_storage_bucket.raw_lake.name
  description = "Raw lake bucket"
}

output "bq_datasets" {
  value = {
    staging = google_bigquery_dataset.staging.dataset_id
    core    = google_bigquery_dataset.core.dataset_id
    marts   = google_bigquery_dataset.marts.dataset_id
  }
  description = "BigQuery datasets"
}

output "pubsub_topic" {
  value       = google_pubsub_topic.trade_events.name
  description = "Trade events topic"
}

output "pubsub_subscription" {
  value       = google_pubsub_subscription.trade_events_stream.name
  description = "Stream processing subscription"
}

output "collector_service_account_email" {
  value       = google_service_account.collector.email
  description = "Service account for collector"
}

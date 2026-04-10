locals {
  dataset_staging = "${var.bq_dataset_prefix}_${var.environment}_staging"
  dataset_core    = "${var.bq_dataset_prefix}_${var.environment}_core"
  dataset_marts   = "${var.bq_dataset_prefix}_${var.environment}_marts"
  service_account = "qf-${var.environment}-collector"
}

resource "google_storage_bucket" "raw_lake" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }
}

resource "google_bigquery_dataset" "staging" {
  dataset_id  = local.dataset_staging
  location    = var.region
  description = "staging layer"
}

resource "google_bigquery_dataset" "core" {
  dataset_id  = local.dataset_core
  location    = var.region
  description = "core layer"
}

resource "google_bigquery_dataset" "marts" {
  dataset_id  = local.dataset_marts
  location    = var.region
  description = "marts layer"
}

resource "google_pubsub_topic" "trade_events" {
  name = var.pubsub_topic_name
}

resource "google_pubsub_subscription" "trade_events_stream" {
  name  = var.pubsub_subscription_name
  topic = google_pubsub_topic.trade_events.name

  ack_deadline_seconds = 20

  expiration_policy {
    ttl = ""
  }
}

resource "google_service_account" "collector" {
  account_id   = local.service_account
  display_name = "Quant Finance Collector (${var.environment})"
}

resource "google_project_iam_member" "collector_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.collector.email}"
}

resource "google_project_iam_member" "collector_storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.collector.email}"
}

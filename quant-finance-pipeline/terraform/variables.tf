variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev/stg/prod)"
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "Unique GCS bucket name for raw lake"
  type        = string
}

variable "bq_dataset_prefix" {
  description = "Prefix for BigQuery datasets"
  type        = string
  default     = "qf"
}

variable "pubsub_topic_name" {
  description = "Pub/Sub topic for trade events"
  type        = string
  default     = "trade-events"
}

variable "pubsub_subscription_name" {
  description = "Pub/Sub subscription for stream processor"
  type        = string
  default     = "trade-events-stream-sub"
}

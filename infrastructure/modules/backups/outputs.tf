output "bucket_name" {
  value = google_storage_bucket.backups.name
}

output "bucket_url" {
  value = "gs://${google_storage_bucket.backups.name}"
}

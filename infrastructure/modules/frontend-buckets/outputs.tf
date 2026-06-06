output "frontend_bucket_name" {
  value = google_storage_bucket.frontend.name
}

output "frontend_bucket_url" {
  value = "gs://${google_storage_bucket.frontend.name}"
}

output "backoffice_bucket_name" {
  value = google_storage_bucket.backoffice.name
}

output "backoffice_bucket_url" {
  value = "gs://${google_storage_bucket.backoffice.name}"
}

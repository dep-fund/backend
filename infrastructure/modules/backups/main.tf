resource "google_storage_bucket" "backups" {
  project                     = var.project_id
  name                        = "${var.environment}-depfund-backups"
  location                    = var.backup_location
  storage_class               = "STANDARD"
  force_destroy               = false
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
}

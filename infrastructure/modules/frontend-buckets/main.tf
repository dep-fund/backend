resource "google_storage_bucket" "frontend" {
  project                     = var.project_id
  name                        = "${var.environment}-depfund-frontend"
  location                    = var.location
  storage_class               = "STANDARD"
  force_destroy               = true
  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }

  cors {
    origin          = var.cors_origins
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket" "backoffice" {
  project                     = var.project_id
  name                        = "${var.environment}-depfund-backoffice"
  location                    = var.location
  storage_class               = "STANDARD"
  force_destroy               = true
  uniform_bucket_level_access = true

  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }

  cors {
    origin          = var.cors_origins
    method          = ["GET", "HEAD", "OPTIONS"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

resource "google_storage_bucket_iam_member" "frontend_public" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

resource "google_storage_bucket_iam_member" "backoffice_public" {
  bucket = google_storage_bucket.backoffice.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

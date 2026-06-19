resource "google_service_account" "backup_sa" {
  project      = var.project_id
  account_id   = "depfund-backup-sa"
  display_name = "DepFund Backup Service Account"
}

resource "google_project_iam_member" "backup_sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.backup_sa.email}"
}

resource "google_project_iam_member" "gke_sa_backup_binding" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${var.project_id}.svc.id.goog[depfund/backup-sa]"
}

resource "google_service_account_iam_binding" "backup_sa_wi" {
  service_account_id = google_service_account.backup_sa.name
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[depfund/backup-sa]",
  ]
}

resource "google_service_account_iam_binding" "gke_sa_eso" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/${var.cluster_sa}"
  role               = "roles/iam.workloadIdentityUser"
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[external-secrets/external-secrets]",
  ]
}

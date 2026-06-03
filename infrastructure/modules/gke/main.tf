data "google_client_config" "default" {}

resource "google_service_account" "gke_sa" {
  project      = var.project_id
  account_id   = "${var.cluster_name}-sa"
  display_name = "GKE Service Account - ${var.cluster_name}"
}

resource "google_container_cluster" "cluster" {
  project  = var.project_id
  location = var.region
  name     = var.cluster_name

  network    = var.network
  subnetwork = var.subnet

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  deletion_protection = false

  node_pool {
    name = "default-pool"

    node_count = var.node_count

    node_config {
      spot           = true
      machine_type   = var.node_machine_type
      disk_size_gb   = 20
      disk_type      = "pd-standard"
      service_account = google_service_account.gke_sa.email
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
      ]
      labels = {
        environment = var.environment
      }
      tags = ["depfund"]
    }

    autoscaling {
      min_node_count = var.node_min_count
      max_node_count = var.node_max_count
    }

    management {
      auto_repair  = true
      auto_upgrade = true
    }
  }

  depends_on = [google_service_account.gke_sa]
}

resource "google_project_iam_member" "gke_sa_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_metrics" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "gke_sa_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

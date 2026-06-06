resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "google_compute_global_address" "private_services" {
  project       = var.project_id
  name          = "${var.environment}-depfund-private-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = var.network_id
}

resource "google_service_networking_connection" "private_services" {
  network                 = var.network_id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_services.name]
}

resource "google_sql_database_instance" "postgres" {
  project          = var.project_id
  name             = "${var.environment}-depfund-db"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    edition           = "ENTERPRISE"
    tier              = var.tier
    disk_size         = var.disk_size
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    availability_type = var.availability_type

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      start_time                     = "03:00"
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.network_id
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 4500
      record_application_tags = true
      record_client_address   = false
    }
  }

  deletion_protection = var.deletion_protection

  depends_on = [google_service_networking_connection.private_services]
}

resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
  project  = var.project_id
}

resource "google_sql_user" "app_user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

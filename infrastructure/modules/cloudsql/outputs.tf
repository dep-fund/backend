output "instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.postgres.name
}

output "private_ip_address" {
  description = "Private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "db_name" {
  description = "Database name"
  value       = google_sql_database.database.name
}

output "db_user" {
  description = "Database application user"
  value       = google_sql_user.app_user.name
}

output "db_password" {
  description = "Database application user password"
  value       = random_password.db_password.result
  sensitive   = true
}

output "connection_name" {
  description = "Cloud SQL connection name (project:region:instance)"
  value       = google_sql_database_instance.postgres.connection_name
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "network_id" {
  description = "Self-link of the VPC network for private IP"
  type        = string
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "depfund"
}

variable "db_user" {
  description = "Database application user"
  type        = string
  default     = "depfund_app"
}

variable "tier" {
  description = "Cloud SQL tier (https://cloud.google.com/sql/docs/pricing#db-tier)"
  type        = string
  default     = "db-f1-micro"
}

variable "disk_size" {
  description = "Disk size in GB"
  type        = number
  default     = 20
}

variable "deletion_protection" {
  description = "Enable deletion protection for production"
  type        = bool
  default     = true
}

variable "availability_type" {
  description = "ZONAL or REGIONAL (HA)"
  type        = string
  default     = "ZONAL"
}

variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone (single zone for cost savings)"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "subnet_cidr" {
  description = "CIDR block for the VPC subnet"
  type        = string
  default     = "10.0.0.0/20"
}

variable "node_machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-2"
}

variable "node_count" {
  description = "Initial node count (autoscaler manages actual count)"
  type        = number
  default     = 1
}

variable "node_min_count" {
  description = "Minimum node count (autoscaling)"
  type        = number
  default     = 1
}

variable "node_max_count" {
  description = "Maximum node count (autoscaling)"
  type        = number
  default     = 3
}


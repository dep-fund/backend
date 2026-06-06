variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
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
  default     = "e2-small"
}

variable "node_count" {
  description = "Initial node count"
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

variable "backend_neg_ids" {
  description = "Self-links of the GKE NEGs (one per zone) for the backend"
  type        = list(string)
  default     = []
}

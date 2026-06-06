variable "project_id" {
  type = string
}

variable "environment" {
  type = string
}

variable "frontend_bucket_name" {
  type = string
}

variable "backoffice_bucket_name" {
  type = string
}

variable "backend_neg_ids" {
  type        = list(string)
  description = "List of self_links of the GKE NEGs (one per zone) for the backend service"
}

variable "static_ip_name" {
  type        = string
  description = "Name of the existing global static IP address"
  default     = "prod-depfund-ingress-ip"
}

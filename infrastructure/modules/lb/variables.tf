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

variable "backend_neg_id" {
  type        = string
  description = "The self_link of the GKE NEG for the backend service. Run: gcloud compute network-endpoint-groups list --project=PROJECT_ID"
}

variable "static_ip_name" {
  type        = string
  description = "Name of the existing global static IP address"
  default     = "prod-depfund-ingress-ip"
}

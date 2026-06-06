variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "zone" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "network" {
  type = string
}

variable "subnet" {
  type = string
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "node_machine_type" {
  type    = string
  default = "e2-small"
}

variable "node_count" {
  type    = number
  default = 1
}

variable "node_min_count" {
  type    = number
  default = 1
}

variable "node_max_count" {
  type    = number
  default = 3
}

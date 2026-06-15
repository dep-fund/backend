provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

resource "google_artifact_registry_repository" "backend" {
  project       = var.gcp_project_id
  location      = var.gcp_region
  repository_id = "depfund"
  description   = "Docker images for DepFund backend"
  format        = "DOCKER"
}

module "vpc" {
  source      = "../../modules/vpc"
  project_id  = var.gcp_project_id
  region      = var.gcp_region
  vpc_name    = "${var.environment}-depfund-vpc"
  subnet_cidr = var.subnet_cidr
}

module "gke" {
  source            = "../../modules/gke"
  project_id        = var.gcp_project_id
  region            = var.gcp_region
  zone              = var.gcp_zone
  cluster_name      = "${var.environment}-depfund-cluster"
  network           = module.vpc.network_id
  subnet            = module.vpc.subnet_id
  environment       = var.environment
  node_machine_type = var.node_machine_type
  node_count        = var.node_count
  node_min_count    = var.node_min_count
  node_max_count    = var.node_max_count
  depends_on        = [module.vpc]
}

module "backups" {
  source          = "../../modules/backups"
  project_id      = var.gcp_project_id
  environment     = var.environment
  backup_location = var.gcp_region
}

module "iam" {
  source       = "../../modules/iam"
  project_id   = var.gcp_project_id
  cluster_name = module.gke.cluster_name
  cluster_sa   = module.gke.cluster_sa
  depends_on   = [module.gke]
}

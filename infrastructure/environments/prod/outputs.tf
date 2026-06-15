output "cluster_name" {
  value = module.gke.cluster_name
}

output "cluster_endpoint" {
  value = module.gke.cluster_endpoint
}

output "bucket_backups" {
  value = module.backups.bucket_name
}

output "network_name" {
  value = module.vpc.network_name
}

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

output "ingress_static_ip" {
  value = google_compute_global_address.ingress_ip.address
}

output "frontend_bucket_name" {
  value = module.frontend_buckets.frontend_bucket_name
}

output "backoffice_bucket_name" {
  value = module.frontend_buckets.backoffice_bucket_name
}

output "lb_url_map" {
  value = module.lb.url_map_name
}

output "lb_ip_address" {
  value = module.lb.lb_ip_address
}

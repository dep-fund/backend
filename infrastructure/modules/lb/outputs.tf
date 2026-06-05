output "url_map_name" {
  value = google_compute_url_map.main.name
}

output "lb_ip_address" {
  value = data.google_compute_global_address.ingress_ip.address
}

output "backend_service_name" {
  value = google_compute_backend_service.backend.name
}

output "frontend_backend_bucket" {
  value = google_compute_backend_bucket.frontend.name
}

output "backoffice_backend_bucket" {
  value = google_compute_backend_bucket.backoffice.name
}

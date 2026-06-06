locals {
  name_prefix = "${var.environment}-depfund"
}

# ─── Backend buckets (frontend + backoffice) ───

resource "google_compute_backend_bucket" "frontend" {
  project     = var.project_id
  name        = "${local.name_prefix}-frontend-bucket"
  bucket_name = var.frontend_bucket_name
  enable_cdn  = false
  description = "Serves the public frontend SPA"
}

resource "google_compute_backend_bucket" "backoffice" {
  project     = var.project_id
  name        = "${local.name_prefix}-backoffice-bucket"
  bucket_name = var.backoffice_bucket_name
  enable_cdn  = false
  description = "Serves the backoffice admin SPA"
}

# ─── Backend service for GKE NEG ───

resource "google_compute_health_check" "backend" {
  project = var.project_id
  name    = "${local.name_prefix}-lb-health-check"

  check_interval_sec = 10
  timeout_sec        = 5
  healthy_threshold  = 2
  unhealthy_threshold = 3

  http_health_check {
    port         = 8000
    request_path = "/health"
  }
}

resource "google_compute_backend_service" "backend" {
  project     = var.project_id
  name        = "${local.name_prefix}-backend"
  description = "Routes to the GKE backend via NEG"

  port_name        = "http"
  protocol         = "HTTP"
  timeout_sec      = 30
  health_checks    = [google_compute_health_check.backend.id]
  load_balancing_scheme = "EXTERNAL_MANAGED"

  dynamic "backend" {
    for_each = var.backend_neg_ids
    content {
      group          = backend.value
      balancing_mode = "RATE"
      max_rate_per_endpoint = 100
    }
  }
}

# ─── URL Map ───

resource "google_compute_url_map" "main" {
  project         = var.project_id
  name            = "${local.name_prefix}-url-map"
  description     = "URL map: frontend default, backoffice /admin/*, backend /api/* /health"

  default_service = google_compute_backend_bucket.frontend.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "all-paths"
  }

  path_matcher {
    name            = "all-paths"
    default_service = google_compute_backend_bucket.frontend.id

    path_rule {
      paths = [
        "/api/*",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
      ]
      service = google_compute_backend_service.backend.id
    }

    path_rule {
      paths = ["/admin/*"]
      service = google_compute_backend_bucket.backoffice.id
    }
  }
}

# ─── Target HTTP Proxy ───

resource "google_compute_target_http_proxy" "main" {
  project = var.project_id
  name    = "${local.name_prefix}-http-proxy"
  url_map = google_compute_url_map.main.id
}

# ─── Global Forwarding Rule (uses existing static IP) ───

data "google_compute_global_address" "ingress_ip" {
  project = var.project_id
  name    = var.static_ip_name
}

resource "google_compute_global_forwarding_rule" "http" {
  project    = var.project_id
  name       = "${local.name_prefix}-http-forwarding-rule"
  target     = google_compute_target_http_proxy.main.id
  ip_address = data.google_compute_global_address.ingress_ip.address
  port_range = "80"
}

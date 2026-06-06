gcp_project_id = "depfund-498022-d7"
gcp_region     = "us-central1"
environment    = "prod"
subnet_cidr    = "10.0.0.0/20"
backend_neg_ids = [
  "https://www.googleapis.com/compute/v1/projects/depfund-498022-d7/zones/us-central1-a/networkEndpointGroups/k8s1-9c84b76e-depfund-depfund-backend-8000-5e5645ab",
  "https://www.googleapis.com/compute/v1/projects/depfund-498022-d7/zones/us-central1-c/networkEndpointGroups/k8s1-9c84b76e-depfund-depfund-backend-8000-5e5645ab",
  "https://www.googleapis.com/compute/v1/projects/depfund-498022-d7/zones/us-central1-f/networkEndpointGroups/k8s1-9c84b76e-depfund-depfund-backend-8000-5e5645ab",
]

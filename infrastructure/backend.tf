terraform {
  backend "gcs" {
    bucket = "depfund-tfstate-depfund-498022-d7"
    prefix = "prod"
  }

  required_version = ">= 1.7.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40"
    }
  }
}

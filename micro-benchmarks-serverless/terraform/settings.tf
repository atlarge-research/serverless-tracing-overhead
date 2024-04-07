terraform {
  required_version = ">= 1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    # Change the bucket name to your bucket
    bucket = "msc-distributed-tracing-benchmark-state"
    key    = "micro-benchmarks"
    region = "eu-west-1"
  }
}

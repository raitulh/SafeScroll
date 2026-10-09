terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.80, < 6" }
    random = { source = "hashicorp/random", version = ">= 3.6, < 4" }
  }
}
provider "aws" { region = var.aws_region }

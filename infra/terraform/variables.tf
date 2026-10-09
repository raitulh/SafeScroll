variable "aws_region" { type = string default = "ap-southeast-1" }
variable "project" { type = string default = "safescroll" }
variable "db_password" { type = string sensitive = true }
variable "api_image" { type = string description = "Full API container image URI (ECR or another registry)." }
variable "db_instance_class" { type = string default = "db.t4g.micro" }
variable "db_multi_az" { type = bool default = false }
variable "redis_node_type" { type = string default = "cache.t4g.micro" }
variable "api_cpu" { type = string default = "512" }
variable "api_memory" { type = string default = "1024" }
variable "api_desired_count" { type = number default = 2 }
variable "cors_origins" { type = string default = "https://example.com" }

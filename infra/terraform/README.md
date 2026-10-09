# Production AWS baseline

This stack provisions:

- VPC with public/private subnets
- Internet gateway + NAT gateway
- Application Load Balancer
- ECS Fargate API service (private subnets)
- ECR repository
- encrypted PostgreSQL RDS
- encrypted ElastiCache Redis
- CloudWatch log group
- ECS IAM execution/task roles
- Secrets Manager for JWT, database URL and Redis URL

## Deploy

1. Build/push the API image to ECR.
2. Provide `api_image`, `db_password` and a real `cors_origins` value.
3. Use a remote Terraform state backend and CI-managed AWS credentials.
4. Add an ACM certificate and HTTPS listener before public production launch; the included HTTP listener is intentionally the lowest-friction baseline.
5. Add AWS WAF, CloudWatch alarms, backups/restore drills and incident response before declaring the service operationally complete.

Never commit `terraform.tfvars` or private key material.

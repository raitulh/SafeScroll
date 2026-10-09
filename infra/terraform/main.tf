data "aws_availability_zones" "available" { state = "available" }

data "aws_caller_identity" "current" {}

resource "aws_vpc" "this" {
  cidr_block           = "10.50.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "${var.project}-vpc" }
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.50.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${var.project}-public-${count.index}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.50.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "${var.project}-private-${count.index}" }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

resource "aws_eip" "nat" { domain = "vpc" }
resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.this]
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route { cidr_block = "0.0.0.0/0" gateway_id = aws_internet_gateway.this.id }
}
resource "aws_route_table_association" "public" {
  count = 2
  subnet_id = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id
  route { cidr_block = "0.0.0.0/0" nat_gateway_id = aws_nat_gateway.this.id }
}
resource "aws_route_table_association" "private" {
  count = 2
  subnet_id = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "alb" {
  name = "${var.project}-alb"
  vpc_id = aws_vpc.this.id
  ingress { from_port = 80 to_port = 80 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }
  ingress { from_port = 443 to_port = 443 protocol = "tcp" cidr_blocks = ["0.0.0.0/0"] }
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_security_group" "api" {
  name = "${var.project}-api"
  vpc_id = aws_vpc.this.id
  ingress { from_port = 8000 to_port = 8000 protocol = "tcp" security_groups = [aws_security_group.alb.id] }
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_security_group" "db" {
  name = "${var.project}-db"
  vpc_id = aws_vpc.this.id
  ingress { from_port = 5432 to_port = 5432 protocol = "tcp" security_groups = [aws_security_group.api.id] }
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
}
resource "aws_security_group" "redis" {
  name = "${var.project}-redis"
  vpc_id = aws_vpc.this.id
  ingress { from_port = 6379 to_port = 6379 protocol = "tcp" security_groups = [aws_security_group.api.id] }
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
}

resource "aws_db_subnet_group" "db" {
  name = "${var.project}-db"
  subnet_ids = aws_subnet.private[*].id
}
resource "aws_db_instance" "postgres" {
  identifier = var.project
  engine = "postgres"
  engine_version = "17"
  instance_class = var.db_instance_class
  allocated_storage = 20
  max_allocated_storage = 100
  storage_type = "gp3"
  storage_encrypted = true
  db_name = "safescroll"
  username = "safescroll"
  password = var.db_password
  port = 5432
  db_subnet_group_name = aws_db_subnet_group.db.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible = false
  backup_retention_period = 7
  deletion_protection = true
  multi_az = var.db_multi_az
  skip_final_snapshot = false
}

resource "aws_elasticache_subnet_group" "redis" {
  name = "${var.project}-redis"
  subnet_ids = aws_subnet.private[*].id
}
resource "random_password" "redis" { length = 48 special = false }
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = var.project
  description = "SafeScroll Redis"
  engine = "redis"
  node_type = var.redis_node_type
  num_cache_clusters = 1
  port = 6379
  auth_token = random_password.redis.result
  subnet_group_name = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  automatic_failover_enabled = false
}

resource "aws_ecr_repository" "api" {
  name = "${var.project}-api"
  image_scanning_configuration { scan_on_push = true }
  force_delete = false
}

resource "aws_cloudwatch_log_group" "api" {
  name = "/ecs/${var.project}/api"
  retention_in_days = 30
}

resource "aws_iam_role" "ecs_execution" {
  name = "${var.project}-ecs-execution"
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"},Action="sts:AssumeRole"}]})
}
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role" "ecs_task" {
  name = "${var.project}-ecs-task"
  assume_role_policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Principal={Service="ecs-tasks.amazonaws.com"},Action="sts:AssumeRole"}]})
}

resource "random_password" "jwt" {
  length = 64
  special = true
}
resource "aws_secretsmanager_secret" "jwt" { name = "${var.project}/jwt" }
resource "aws_secretsmanager_secret_version" "jwt" {
  secret_id = aws_secretsmanager_secret.jwt.id
  secret_string = random_password.jwt.result
}
resource "aws_secretsmanager_secret" "database_url" { name = "${var.project}/database-url" }
resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = "postgresql+asyncpg://safescroll:${var.db_password}@${aws_db_instance.postgres.address}:5432/safescroll"
}
resource "aws_secretsmanager_secret" "redis_url" { name = "${var.project}/redis-url" }
resource "aws_secretsmanager_secret_version" "redis_url" {
  secret_id = aws_secretsmanager_secret.redis_url.id
  secret_string = "rediss://:${aws_elasticache_replication_group.redis.auth_token}@${aws_elasticache_replication_group.redis.primary_endpoint_address}:6379/0"
}

resource "aws_iam_role_policy" "secrets" {
  role = aws_iam_role.ecs_task.id
  policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action=["secretsmanager:GetSecretValue"],Resource=[aws_secretsmanager_secret.jwt.arn,aws_secretsmanager_secret.database_url.arn,aws_secretsmanager_secret.redis_url.arn]}]})
}
resource "aws_iam_role_policy" "execution_secrets" {
  role = aws_iam_role.ecs_execution.id
  policy = jsonencode({Version="2012-10-17",Statement=[{Effect="Allow",Action=["secretsmanager:GetSecretValue"],Resource=[aws_secretsmanager_secret.jwt.arn,aws_secretsmanager_secret.database_url.arn,aws_secretsmanager_secret.redis_url.arn]}]})
}

resource "aws_ecs_cluster" "this" {
  name = var.project
  setting { name = "containerInsights" value = "enabled" }
}
resource "aws_lb" "api" {
  name = "${var.project}-api"
  load_balancer_type = "application"
  security_groups = [aws_security_group.alb.id]
  subnets = aws_subnet.public[*].id
}
resource "aws_lb_target_group" "api" {
  name = "${var.project}-api"
  port = 8000
  protocol = "HTTP"
  target_type = "ip"
  vpc_id = aws_vpc.this.id
  health_check { path = "/api/v1/health" healthy_threshold = 2 unhealthy_threshold = 3 timeout = 5 interval = 30 matcher = "200" }
}
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.api.arn
  port = 80
  protocol = "HTTP"
  default_action { type = "forward" target_group_arn = aws_lb_target_group.api.arn }
}
resource "aws_ecs_task_definition" "api" {
  family = "${var.project}-api"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = var.api_cpu
  memory = var.api_memory
  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn = aws_iam_role.ecs_task.arn
  container_definitions = jsonencode([{name="api",image=var.api_image,essential=true,portMappings=[{containerPort=8000,hostPort=8000,protocol="tcp"}],environment=[{name="APP_ENV",value="production"},{name="APP_VERSION",value="1.0.0"},{name="AUTO_CREATE_DB",value="false"},{name="CORS_ORIGINS",value=var.cors_origins},{name="OLLAMA_MODEL",value="qwen3:1.7b"}],secrets=[{name="JWT_SECRET",valueFrom=aws_secretsmanager_secret.jwt.arn},{name="DATABASE_URL",valueFrom=aws_secretsmanager_secret.database_url.arn},{name="REDIS_URL",valueFrom=aws_secretsmanager_secret.redis_url.arn}],logConfiguration={logDriver="awslogs",options={awslogs-group=aws_cloudwatch_log_group.api.name,awslogs-region=var.aws_region,awslogs-stream-prefix="api"}},healthCheck={command=["CMD-SHELL","python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')\""],interval=30,timeout=5,retries=3,startPeriod=20}}])
}
resource "aws_ecs_service" "api" {
  name = "${var.project}-api"
  cluster = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count = var.api_desired_count
  launch_type = "FARGATE"
  network_configuration { subnets = aws_subnet.private[*].id security_groups = [aws_security_group.api.id] assign_public_ip = false }
  load_balancer { target_group_arn = aws_lb_target_group.api.arn container_name = "api" container_port = 8000 }
  depends_on = [aws_lb_listener.http]
}

output "api_url" { value = "http://${aws_lb.api.dns_name}" }
output "ecr_repository" { value = aws_ecr_repository.api.repository_url }
output "database_endpoint" { value = aws_db_instance.postgres.address }
output "redis_endpoint" { value = aws_elasticache_replication_group.redis.primary_endpoint_address }

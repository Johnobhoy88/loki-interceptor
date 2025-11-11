# LOKI Infrastructure Outputs

# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnets
}

# EKS Outputs
output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_certificate_authority_data" {
  description = "EKS cluster certificate authority data"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = module.eks.cluster_security_group_id
}

output "oidc_provider_arn" {
  description = "OIDC provider ARN for EKS"
  value       = module.eks.oidc_provider_arn
}

# RDS Outputs
output "db_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.loki.endpoint
}

output "db_address" {
  description = "RDS address"
  value       = aws_db_instance.loki.address
}

output "db_port" {
  description = "RDS port"
  value       = aws_db_instance.loki.port
}

output "db_name" {
  description = "Database name"
  value       = aws_db_instance.loki.db_name
}

# Connection commands
output "configure_kubectl" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "database_connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.loki.endpoint}/${var.db_name}"
  sensitive   = true
}

# LOKI Terraform Infrastructure

This directory contains Terraform configurations for deploying LOKI infrastructure on AWS.

## Prerequisites

- Terraform >= 1.5.0
- AWS CLI configured with appropriate credentials
- kubectl

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Create a terraform.tfvars file

```hcl
# terraform.tfvars
project_name = "loki"
environment  = "production"
aws_region   = "us-east-1"

# Database credentials (use AWS Secrets Manager in production)
db_username = "loki"
db_password = "your-secure-password-here"

# Domain configuration
domain_name     = "loki.yourdomain.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/xxx"
```

### 3. Plan the deployment

```bash
terraform plan
```

### 4. Apply the configuration

```bash
terraform apply
```

### 5. Configure kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name loki-production
```

## Infrastructure Components

### Networking
- **VPC**: Isolated network with public and private subnets across 3 AZs
- **NAT Gateways**: High availability internet access for private subnets
- **VPC Endpoints**: Cost-optimized access to AWS services

### Compute
- **EKS Cluster**: Managed Kubernetes cluster (version 1.28)
- **Node Groups**: Auto-scaling worker nodes (t3.large)
- **IAM Roles**: Least-privilege access for pods

### Database
- **RDS PostgreSQL**: Managed database (version 15.4)
- **Multi-AZ**: High availability deployment
- **Encryption**: At-rest encryption with KMS
- **Backups**: Automated daily backups (7 day retention)

### Security
- **KMS Keys**: Encryption for EKS secrets and RDS
- **Security Groups**: Network access control
- **IAM Policies**: Fine-grained permissions

## Environments

Different environments can be managed using workspaces:

```bash
# Development
terraform workspace new dev
terraform apply -var-file=environments/dev/terraform.tfvars

# Staging
terraform workspace new staging
terraform apply -var-file=environments/staging/terraform.tfvars

# Production
terraform workspace new prod
terraform apply -var-file=environments/prod/terraform.tfvars
```

## State Management

It's recommended to use remote state storage:

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "loki-terraform-state"
    key            = "loki/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "loki-terraform-locks"
  }
}
```

## Outputs

After applying, Terraform will output:
- EKS cluster endpoint
- RDS database endpoint
- kubectl configuration command

## Maintenance

### Updating Kubernetes version

```bash
terraform apply -var="cluster_version=1.29"
```

### Scaling nodes

```bash
terraform apply \
  -var="node_min_capacity=3" \
  -var="node_desired_capacity=5" \
  -var="node_max_capacity=15"
```

### Destroying infrastructure

```bash
terraform destroy
```

## Security Best Practices

1. **Store secrets securely**: Use AWS Secrets Manager or Parameter Store
2. **Enable MFA**: Require MFA for destructive operations
3. **Audit logs**: Enable CloudTrail for all API calls
4. **Network security**: Use private subnets for workloads
5. **Encryption**: Enable encryption at rest and in transit

## Cost Optimization

- Use Spot Instances for non-production environments
- Enable auto-scaling to match demand
- Use VPC endpoints to reduce NAT Gateway costs
- Enable RDS storage auto-scaling

## Troubleshooting

### EKS access denied

```bash
aws sts get-caller-identity
aws eks update-kubeconfig --region us-east-1 --name loki-production
```

### RDS connection timeout

Check security group rules allow traffic from EKS nodes:
```bash
terraform output db_endpoint
```

## Support

For issues and questions, please refer to:
- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)

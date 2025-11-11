# LOKI Deployment Guide

Comprehensive guide for deploying LOKI AI Safety Interceptor to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Cloud Infrastructure (Terraform)](#cloud-infrastructure-terraform)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security](#security)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

---

## Prerequisites

### Required Tools

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **kubectl** >= 1.28
- **Terraform** >= 1.5.0 (for cloud deployment)
- **Git**
- **AWS CLI** (for AWS deployment)

### Required Accounts

- GitHub account (for CI/CD)
- Container registry account (Docker Hub, GHCR, ECR, etc.)
- Cloud provider account (AWS, GCP, or Azure)
- API Keys:
  - Anthropic API Key
  - OpenAI API Key (optional)
  - Google AI API Key (optional)

---

## Local Development

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/loki-interceptor.git
cd loki-interceptor
```

2. **Create environment file**

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-google-key-here
```

3. **Start local development environment**

```bash
chmod +x scripts/deploy/local-dev.sh
./scripts/deploy/local-dev.sh
```

This will:
- Build Docker images
- Start all services (backend, frontend, PostgreSQL, Redis)
- Run health checks

4. **Access the application**

- Frontend: http://localhost
- Backend API: http://localhost:5002
- API Health: http://localhost:5002/health

5. **View logs**

```bash
docker-compose logs -f
docker-compose logs -f backend  # Backend only
docker-compose logs -f frontend # Frontend only
```

6. **Stop services**

```bash
docker-compose down
```

---

## Docker Deployment

### Building Images

#### Build all images locally

```bash
chmod +x scripts/deploy/docker-build.sh
./scripts/deploy/docker-build.sh
```

#### Build specific images

```bash
# Backend only
docker build -t loki-backend:latest -f backend/Dockerfile backend/

# Frontend only
docker build -t loki-frontend:latest -f frontend/Dockerfile frontend/
```

### Running with Docker Compose

#### Production deployment

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### With monitoring stack

```bash
# Start with Prometheus and Grafana
docker-compose --profile monitoring up -d

# Access monitoring
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
```

### Pushing to Registry

```bash
# Login to registry
docker login ghcr.io -u USERNAME -p TOKEN

# Tag images
docker tag loki-backend:latest ghcr.io/yourusername/loki-backend:v1.0.0
docker tag loki-frontend:latest ghcr.io/yourusername/loki-frontend:v1.0.0

# Push images
docker push ghcr.io/yourusername/loki-backend:v1.0.0
docker push ghcr.io/yourusername/loki-frontend:v1.0.0

# Or use the script
export DOCKER_REGISTRY=ghcr.io
export DOCKER_REPO=yourusername/loki-interceptor
export VERSION=v1.0.0
./scripts/deploy/docker-push.sh
```

### Docker Image Optimization

Our multi-stage builds are optimized for:
- **Small image size**: Backend ~150MB, Frontend ~20MB
- **Security**: Non-root user, minimal attack surface
- **Performance**: Layer caching, parallel builds

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (>= 1.28)
- kubectl configured
- Container registry with images pushed
- Ingress controller (nginx-ingress recommended)
- cert-manager for SSL certificates

### Namespace Setup

```bash
kubectl create namespace loki
kubectl config set-context --current --namespace=loki
```

### Configure Secrets

Create a secrets file (DO NOT commit to git):

```bash
cat > k8s/base/secrets-prod.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: loki-secrets
  namespace: loki
type: Opaque
stringData:
  ANTHROPIC_API_KEY: "sk-ant-your-actual-key"
  OPENAI_API_KEY: "sk-your-actual-key"
  GOOGLE_API_KEY: "your-actual-key"
  SECRET_KEY: "$(openssl rand -hex 32)"
  POSTGRES_PASSWORD: "$(openssl rand -base64 32)"
  REDIS_PASSWORD: "$(openssl rand -base64 32)"
  DATABASE_URL: "postgresql://loki:\$(POSTGRES_PASSWORD)@loki-postgres:5432/loki"
  REDIS_URL: "redis://:\$(REDIS_PASSWORD)@loki-redis:6379/0"
EOF

kubectl apply -f k8s/base/secrets-prod.yaml
```

### Deploy with kubectl

```bash
# Apply all manifests
kubectl apply -k k8s/base/

# Check deployment status
kubectl get pods -n loki
kubectl get services -n loki
kubectl get ingress -n loki

# Wait for rollout
kubectl rollout status deployment/loki-backend -n loki
kubectl rollout status deployment/loki-frontend -n loki
```

### Deploy with Script

```bash
chmod +x scripts/deploy/k8s-deploy.sh

# Set environment variables
export K8S_NAMESPACE=loki
export ENVIRONMENT=production
export REGISTRY=ghcr.io
export REPO=yourusername/loki-interceptor

# Deploy
./scripts/deploy/k8s-deploy.sh
```

### Update Ingress

Edit `k8s/base/ingress.yaml` to match your domain:

```yaml
spec:
  tls:
  - hosts:
    - loki.yourdomain.com
    - api.loki.yourdomain.com
    secretName: loki-tls-cert
  rules:
  - host: loki.yourdomain.com
    # ...
```

Apply changes:

```bash
kubectl apply -f k8s/base/ingress.yaml
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment loki-backend --replicas=5 -n loki

# Check HPA status
kubectl get hpa -n loki

# The HPA will automatically scale between 3-10 replicas based on CPU/memory
```

### Rollback

```bash
# Rollback to previous version
./scripts/deploy/rollback.sh

# Or manually
kubectl rollout undo deployment/loki-backend -n loki
kubectl rollout undo deployment/loki-frontend -n loki

# View rollout history
kubectl rollout history deployment/loki-backend -n loki
```

---

## Cloud Infrastructure (Terraform)

### AWS Deployment

#### 1. Configure AWS credentials

```bash
aws configure
```

#### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

#### 3. Create terraform.tfvars

```hcl
# terraform/terraform.tfvars
project_name = "loki"
environment  = "production"
aws_region   = "us-east-1"

# Database credentials
db_username = "loki"
db_password = "your-secure-password"

# Cluster configuration
cluster_version        = "1.28"
node_instance_types    = ["t3.large"]
node_desired_capacity  = 3
node_min_capacity      = 2
node_max_capacity      = 10

# Domain
domain_name     = "loki.yourdomain.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/xxx"

# Features
enable_monitoring = true
enable_deletion_protection = true
```

#### 4. Plan and apply

```bash
# Preview changes
terraform plan

# Apply infrastructure
terraform apply

# Get outputs
terraform output
```

#### 5. Configure kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name loki-production
kubectl get nodes
```

#### 6. Deploy LOKI to EKS

```bash
cd ..
kubectl apply -k k8s/base/
```

### Infrastructure Components

The Terraform configuration creates:

- **VPC**: 3 AZs with public and private subnets
- **EKS Cluster**: Managed Kubernetes with auto-scaling node groups
- **RDS PostgreSQL**: Multi-AZ database with automated backups
- **ElastiCache Redis**: High-availability cache
- **KMS Keys**: Encryption for secrets and data at rest
- **IAM Roles**: Least-privilege access for services
- **VPC Endpoints**: Cost-optimized AWS service access

### Cost Estimation

Approximate monthly costs (us-east-1):
- EKS Control Plane: $73
- EC2 Nodes (3x t3.large): $150
- RDS (db.t3.medium, Multi-AZ): $120
- ElastiCache (2x cache.t3.medium): $100
- NAT Gateways (2): $90
- Data Transfer: $50-200 (varies)

**Total: ~$583-733/month**

---

## CI/CD Pipeline

### GitHub Actions Setup

#### 1. Configure secrets

Go to Settings > Secrets and variables > Actions:

```
ANTHROPIC_API_KEY          # Your Anthropic API key
OPENAI_API_KEY             # Your OpenAI API key
KUBE_CONFIG_PRODUCTION     # Base64 encoded kubeconfig
KUBE_CONFIG_STAGING        # Base64 encoded kubeconfig
SNYK_TOKEN                 # Snyk security scanning token
```

Get kubeconfig:
```bash
kubectl config view --raw | base64
```

#### 2. Workflows

Three workflows are configured:

##### CI Workflow (`.github/workflows/ci.yml`)
- Triggers: Pull requests, pushes to main/develop
- Actions:
  - Run backend tests with pytest
  - Lint code with flake8, black
  - Build Docker images
  - Run integration tests
  - Generate coverage reports

##### Deploy Workflow (`.github/workflows/deploy.yml`)
- Triggers: Push to main, tags, manual
- Actions:
  - Build and push Docker images to GHCR
  - Deploy to staging/production
  - Run smoke tests
  - Auto-rollback on failure

##### Security Scan Workflow (`.github/workflows/security-scan.yml`)
- Triggers: Daily, PRs, manual
- Actions:
  - Dependency vulnerability scan (Snyk)
  - Code security scan (CodeQL)
  - Secret scanning (TruffleHog)
  - Docker image scan (Trivy)
  - SAST scan (Bandit)
  - License compliance check

### Manual Deployment

```bash
# Trigger deployment via workflow_dispatch
gh workflow run deploy.yml -f environment=production
```

---

## Monitoring & Logging

### Prometheus Metrics

LOKI exposes metrics at `/metrics`:

```bash
curl http://localhost:5002/metrics
```

**Key metrics:**
- `loki_requests_total` - Total HTTP requests
- `loki_request_duration_seconds` - Request latency
- `loki_validations_total` - Validation counts
- `loki_gate_triggers_total` - Gate trigger counts
- `loki_cache_hits_total` - Cache performance
- `loki_model_tokens_total` - Token usage

### Grafana Dashboards

Access Grafana at http://localhost:3000 (admin/admin)

Import dashboards:
1. Click + > Import
2. Upload `configs/grafana/dashboards/*.json`

### Log Aggregation

#### With Fluentd (Recommended)

1. Deploy Fluentd DaemonSet:

```bash
kubectl apply -f https://raw.githubusercontent.com/fluent/fluentd-kubernetes-daemonset/master/fluentd-daemonset-elasticsearch.yaml
```

2. Configure Fluentd to use our config:

```bash
kubectl create configmap fluentd-config --from-file=configs/fluentd.conf -n kube-system
```

#### With CloudWatch (AWS)

```bash
# Install CloudWatch agent
kubectl apply -f https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/cwagent/cwagent-daemonset.yaml
```

### Health Checks

```bash
# Liveness probe (is it alive?)
curl http://localhost:5002/health

# Readiness probe (ready for traffic?)
curl http://localhost:5002/health?detailed=true

# Expected response:
{
  "status": "healthy",
  "modules": ["hr_scottish", "gdpr_uk", ...],
  "modules_loaded": 10,
  "uptime_seconds": 3600.0
}
```

---

## Security

### Security Checklist

- [ ] Rotate all default passwords
- [ ] Use secrets management (AWS Secrets Manager, Vault)
- [ ] Enable encryption at rest (RDS, EBS)
- [ ] Enable encryption in transit (TLS/SSL)
- [ ] Configure network policies
- [ ] Enable pod security policies
- [ ] Run security scans regularly
- [ ] Set up audit logging
- [ ] Configure RBAC properly
- [ ] Use non-root containers
- [ ] Scan images for vulnerabilities
- [ ] Keep dependencies updated

### Secrets Management

#### AWS Secrets Manager

```bash
# Store secret
aws secretsmanager create-secret \
  --name loki/anthropic-api-key \
  --secret-string "sk-ant-your-key"

# Use in Kubernetes with External Secrets Operator
kubectl apply -f https://raw.githubusercontent.com/external-secrets/external-secrets/main/deploy/crds/bundle.yaml
```

#### HashiCorp Vault

```bash
# Install Vault
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault

# Store secret
vault kv put secret/loki/api-keys \
  anthropic_key="sk-ant-your-key" \
  openai_key="sk-your-key"
```

### Network Security

Network policies are configured in `k8s/base/network-policy.yaml`:
- Backend can only access database and Redis
- Frontend can only access backend
- Database and Redis only accept traffic from backend
- All egress traffic is controlled

### TLS/SSL

Use cert-manager for automatic certificate management:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Troubleshooting

### Common Issues

#### 1. Backend pod not starting

```bash
# Check logs
kubectl logs -f deployment/loki-backend -n loki

# Common issues:
# - Missing API keys → Check secrets
# - Database connection failed → Check RDS security group
# - Module loading failed → Check module files exist
```

#### 2. Database connection timeout

```bash
# Verify database is running
kubectl get pods -n loki | grep postgres

# Check connectivity from backend pod
kubectl exec -it deployment/loki-backend -n loki -- bash
psql $DATABASE_URL

# Check security group allows traffic
aws ec2 describe-security-groups --group-ids sg-xxx
```

#### 3. High memory usage

```bash
# Check current resource usage
kubectl top pods -n loki

# Increase limits in deployment
kubectl set resources deployment/loki-backend \
  --limits=memory=4Gi,cpu=2000m \
  -n loki
```

#### 4. Slow response times

```bash
# Check metrics
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
# Open http://localhost:9090

# Query: rate(loki_request_duration_seconds_sum[5m]) / rate(loki_request_duration_seconds_count[5m])

# Common causes:
# - Cache misses → Check Redis connection
# - Database slow queries → Check RDS Performance Insights
# - Too few replicas → Scale up
```

#### 5. Certificate issues

```bash
# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check certificate status
kubectl describe certificate loki-tls-cert -n loki

# Force renewal
kubectl delete secret loki-tls-cert -n loki
```

---

## Maintenance

### Regular Tasks

#### Daily
- Check application health
- Review error logs
- Monitor resource usage

#### Weekly
- Review security scan results
- Check for dependency updates
- Review performance metrics

#### Monthly
- Update Kubernetes cluster
- Rotate credentials
- Review and optimize costs
- Test disaster recovery

### Updating LOKI

```bash
# Build new version
export VERSION=v1.1.0
./scripts/deploy/docker-build.sh

# Push to registry
./scripts/deploy/docker-push.sh

# Deploy to Kubernetes
./scripts/deploy/k8s-deploy.sh

# Or trigger CI/CD
git tag v1.1.0
git push origin v1.1.0
```

### Database Backup

```bash
# Manual backup
kubectl exec -n loki deployment/loki-postgres -- \
  pg_dump -U loki loki > backup-$(date +%Y%m%d).sql

# Restore from backup
kubectl exec -i -n loki deployment/loki-postgres -- \
  psql -U loki loki < backup-20231115.sql
```

### Disaster Recovery

1. **Backup regularly**
   - Database: Automated RDS snapshots (7 days)
   - Configuration: Store in Git
   - Secrets: Backup from Secrets Manager

2. **Recovery procedure**
   ```bash
   # Restore database from snapshot
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier loki-restored \
     --db-snapshot-identifier loki-snapshot-20231115

   # Redeploy application
   ./scripts/deploy/k8s-deploy.sh
   ```

3. **Test recovery** (quarterly)

### Performance Tuning

#### Backend
- Adjust worker count: `WORKERS=8`
- Increase cache size: `CACHE_TTL=3600`
- Enable Redis clustering for high load

#### Database
- Adjust connection pool size
- Enable query performance insights
- Add read replicas for read-heavy workloads

#### Kubernetes
- Adjust HPA thresholds
- Use pod topology spread for better distribution
- Enable cluster autoscaler

---

## Support & Documentation

### Additional Resources

- [12-Factor App Methodology](https://12factor.net/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)

### Getting Help

- GitHub Issues: https://github.com/yourusername/loki-interceptor/issues
- Documentation: See `/docs` directory
- Security Issues: security@yourdomain.com

---

## Appendix

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment mode | `production` | No |
| `SECRET_KEY` | Flask secret key | - | Yes |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | No |
| `GOOGLE_API_KEY` | Google AI API key | - | No |
| `PORT` | Backend port | `5002` | No |
| `WORKERS` | Gunicorn workers | `4` | No |
| `LOG_LEVEL` | Logging level | `info` | No |
| `PROMETHEUS_ENABLED` | Enable Prometheus metrics | `true` | No |

### Port Reference

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Backend | 5002 | HTTP | API endpoints |
| Frontend | 80 | HTTP | Web interface |
| Frontend | 443 | HTTPS | Secure web interface |
| PostgreSQL | 5432 | TCP | Database |
| Redis | 6379 | TCP | Cache |
| Prometheus | 9090 | HTTP | Metrics collection |
| Grafana | 3000 | HTTP | Dashboards |

### Kubernetes Resources

| Resource | Namespace | Description |
|----------|-----------|-------------|
| `loki-backend` | loki | Backend API deployment |
| `loki-frontend` | loki | Frontend web deployment |
| `loki-postgres` | loki | PostgreSQL database |
| `loki-redis` | loki | Redis cache |
| `loki-ingress` | loki | Ingress controller |
| `loki-secrets` | loki | Application secrets |

---

**Last Updated**: 2024-11-11
**Version**: 1.0.0

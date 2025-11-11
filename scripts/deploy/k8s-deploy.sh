#!/bin/bash
# Kubernetes deployment script for LOKI
# Deploys LOKI to Kubernetes cluster

set -e

# Configuration
NAMESPACE="${K8S_NAMESPACE:-loki}"
ENVIRONMENT="${ENVIRONMENT:-production}"
VERSION="${VERSION:-latest}"
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo "=================================="
echo "LOKI Kubernetes Deployment Script"
echo "=================================="
echo "Namespace: $NAMESPACE"
echo "Environment: $ENVIRONMENT"
echo "Version: $VERSION"
echo "Git Commit: $GIT_COMMIT"
echo "=================================="

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "❌ kubectl not found. Please install kubectl."
        exit 1
    fi
    echo "✓ kubectl found"
}

# Function to check cluster connectivity
check_cluster() {
    echo ""
    echo "Checking cluster connectivity..."
    if ! kubectl cluster-info &> /dev/null; then
        echo "❌ Cannot connect to Kubernetes cluster"
        exit 1
    fi
    echo "✓ Connected to cluster"
}

# Function to create namespace if not exists
create_namespace() {
    echo ""
    echo "Checking namespace..."
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo "Creating namespace $NAMESPACE..."
        kubectl create namespace "$NAMESPACE"
        kubectl label namespace "$NAMESPACE" environment="$ENVIRONMENT"
    fi
    echo "✓ Namespace $NAMESPACE exists"
}

# Function to apply Kubernetes manifests
apply_manifests() {
    echo ""
    echo "Applying Kubernetes manifests..."

    # Apply base manifests
    if [ -f "k8s/base/kustomization.yaml" ]; then
        echo "Applying kustomize base..."
        kubectl apply -k k8s/base/
    else
        echo "Applying individual manifests..."
        kubectl apply -f k8s/base/ -n "$NAMESPACE"
    fi

    # Apply environment-specific overlay if exists
    if [ -d "k8s/overlays/$ENVIRONMENT" ]; then
        echo "Applying $ENVIRONMENT overlay..."
        kubectl apply -k "k8s/overlays/$ENVIRONMENT/"
    fi

    echo "✓ Manifests applied"
}

# Function to update image tags
update_images() {
    echo ""
    echo "Updating image tags to $GIT_COMMIT..."

    kubectl set image deployment/loki-backend \
        backend="$REGISTRY/$REPO-backend:$GIT_COMMIT" \
        -n "$NAMESPACE"

    kubectl set image deployment/loki-frontend \
        frontend="$REGISTRY/$REPO-frontend:$GIT_COMMIT" \
        -n "$NAMESPACE"

    echo "✓ Image tags updated"
}

# Function to wait for rollout
wait_for_rollout() {
    echo ""
    echo "Waiting for rollout to complete..."

    kubectl rollout status deployment/loki-backend -n "$NAMESPACE" --timeout=10m
    kubectl rollout status deployment/loki-frontend -n "$NAMESPACE" --timeout=5m

    echo "✓ Rollout complete"
}

# Function to verify deployment
verify_deployment() {
    echo ""
    echo "Verifying deployment..."

    # Check pod status
    echo "Backend pods:"
    kubectl get pods -n "$NAMESPACE" -l app=loki-backend

    echo ""
    echo "Frontend pods:"
    kubectl get pods -n "$NAMESPACE" -l app=loki-frontend

    # Check if all pods are running
    local backend_ready=$(kubectl get deployment loki-backend -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
    local backend_desired=$(kubectl get deployment loki-backend -n "$NAMESPACE" -o jsonpath='{.status.replicas}')

    if [ "$backend_ready" != "$backend_desired" ]; then
        echo "⚠ Warning: Backend pods not all ready ($backend_ready/$backend_desired)"
    else
        echo "✓ All backend pods ready"
    fi

    local frontend_ready=$(kubectl get deployment loki-frontend -n "$NAMESPACE" -o jsonpath='{.status.readyReplicas}')
    local frontend_desired=$(kubectl get deployment loki-frontend -n "$NAMESPACE" -o jsonpath='{.status.replicas}')

    if [ "$frontend_ready" != "$frontend_desired" ]; then
        echo "⚠ Warning: Frontend pods not all ready ($frontend_ready/$frontend_desired)"
    else
        echo "✓ All frontend pods ready"
    fi
}

# Function to run smoke tests
run_smoke_tests() {
    echo ""
    echo "Running smoke tests..."

    # Get service URLs
    local backend_url=$(kubectl get ingress loki-ingress -n "$NAMESPACE" -o jsonpath='{.spec.rules[1].host}' 2>/dev/null || echo "")

    if [ -n "$backend_url" ]; then
        echo "Testing backend health endpoint..."
        if curl -f "https://$backend_url/health" > /dev/null 2>&1; then
            echo "✓ Backend health check passed"
        else
            echo "⚠ Backend health check failed"
        fi
    else
        echo "⚠ Could not determine backend URL, skipping smoke test"
    fi
}

# Main execution
main() {
    check_kubectl
    check_cluster
    create_namespace
    apply_manifests
    update_images
    wait_for_rollout
    verify_deployment
    run_smoke_tests

    echo ""
    echo "=================================="
    echo "Deployment Complete!"
    echo "=================================="
    echo "Deployed version: $GIT_COMMIT"
    echo "Namespace: $NAMESPACE"
    echo "Environment: $ENVIRONMENT"
    echo "=================================="
}

main "$@"

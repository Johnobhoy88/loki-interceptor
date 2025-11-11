#!/bin/bash
# Kubernetes rollback script for LOKI
# Rolls back LOKI deployment to previous version

set -e

# Configuration
NAMESPACE="${K8S_NAMESPACE:-loki}"
REVISION="${REVISION:-0}"  # 0 = previous version

echo "=================================="
echo "LOKI Kubernetes Rollback Script"
echo "=================================="
echo "Namespace: $NAMESPACE"
echo "Revision: $REVISION (0 = previous)"
echo "=================================="

# Function to rollback deployment
rollback_deployment() {
    local deployment=$1
    local revision_flag=""

    if [ "$REVISION" != "0" ]; then
        revision_flag="--to-revision=$REVISION"
    fi

    echo ""
    echo "Rolling back $deployment..."

    kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE" $revision_flag

    echo "Waiting for rollback to complete..."
    kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=10m

    echo "✓ $deployment rolled back successfully"
}

# Main execution
echo ""
echo "Starting rollback process..."

# Rollback backend
rollback_deployment "loki-backend"

# Rollback frontend
rollback_deployment "loki-frontend"

echo ""
echo "=================================="
echo "Rollback Complete!"
echo "=================================="
echo "Deployments rolled back to previous version"
echo ""
echo "Current status:"
kubectl get pods -n "$NAMESPACE" -l 'app in (loki-backend,loki-frontend)'
echo "=================================="

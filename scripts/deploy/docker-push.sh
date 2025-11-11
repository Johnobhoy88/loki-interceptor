#!/bin/bash
# Docker push script for LOKI
# Pushes Docker images to registry

set -e

# Configuration
REGISTRY="${DOCKER_REGISTRY:-ghcr.io}"
REPO="${DOCKER_REPO:-loki-interceptor}"
VERSION="${VERSION:-latest}"
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo "=================================="
echo "LOKI Docker Push Script"
echo "=================================="
echo "Registry: $REGISTRY"
echo "Repository: $REPO"
echo "Version: $VERSION"
echo "Git Commit: $GIT_COMMIT"
echo "=================================="

# Login to registry
echo ""
echo "Logging in to $REGISTRY..."
if [ -n "$DOCKER_PASSWORD" ]; then
    echo "$DOCKER_PASSWORD" | docker login "$REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
else
    echo "⚠ DOCKER_PASSWORD not set, assuming already logged in"
fi

# Function to push image
push_image() {
    local component=$1

    echo ""
    echo "Pushing $component images..."

    docker push "$REGISTRY/$REPO-$component:$VERSION"
    echo "✓ Pushed $REGISTRY/$REPO-$component:$VERSION"

    docker push "$REGISTRY/$REPO-$component:$GIT_COMMIT"
    echo "✓ Pushed $REGISTRY/$REPO-$component:$GIT_COMMIT"
}

# Push backend images
push_image "backend"

# Push frontend images
push_image "frontend"

echo ""
echo "=================================="
echo "Push Complete!"
echo "=================================="
echo "Images pushed:"
echo "  - $REGISTRY/$REPO-backend:$VERSION"
echo "  - $REGISTRY/$REPO-backend:$GIT_COMMIT"
echo "  - $REGISTRY/$REPO-frontend:$VERSION"
echo "  - $REGISTRY/$REPO-frontend:$GIT_COMMIT"
echo "=================================="

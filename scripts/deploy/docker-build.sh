#!/bin/bash
# Docker build script for LOKI
# Builds and tags Docker images for deployment

set -e

# Configuration
REGISTRY="${DOCKER_REGISTRY:-ghcr.io}"
REPO="${DOCKER_REPO:-loki-interceptor}"
VERSION="${VERSION:-latest}"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

echo "=================================="
echo "LOKI Docker Build Script"
echo "=================================="
echo "Registry: $REGISTRY"
echo "Repository: $REPO"
echo "Version: $VERSION"
echo "Git Commit: $GIT_COMMIT"
echo "Build Date: $BUILD_DATE"
echo "=================================="

# Function to build image
build_image() {
    local component=$1
    local context=$2
    local dockerfile=$3

    echo ""
    echo "Building $component image..."
    echo "Context: $context"
    echo "Dockerfile: $dockerfile"

    docker build \
        --file "$dockerfile" \
        --tag "$REGISTRY/$REPO-$component:$VERSION" \
        --tag "$REGISTRY/$REPO-$component:$GIT_COMMIT" \
        --label "org.opencontainers.image.created=$BUILD_DATE" \
        --label "org.opencontainers.image.revision=$GIT_COMMIT" \
        --label "org.opencontainers.image.version=$VERSION" \
        --build-arg VERSION="$VERSION" \
        --build-arg GIT_COMMIT="$GIT_COMMIT" \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        "$context"

    echo "✓ $component image built successfully"
}

# Build backend image
build_image "backend" "./backend" "./backend/Dockerfile"

# Build frontend image
build_image "frontend" "./frontend" "./frontend/Dockerfile"

echo ""
echo "=================================="
echo "Build Complete!"
echo "=================================="
echo "Images created:"
echo "  - $REGISTRY/$REPO-backend:$VERSION"
echo "  - $REGISTRY/$REPO-backend:$GIT_COMMIT"
echo "  - $REGISTRY/$REPO-frontend:$VERSION"
echo "  - $REGISTRY/$REPO-frontend:$GIT_COMMIT"
echo "=================================="

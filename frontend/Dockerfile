# Multi-stage Dockerfile for LOKI Frontend (Web Version)
# Stage 1: Builder
FROM node:18-alpine as builder

WORKDIR /build

# Copy package files (if any - for web dependencies)
COPY package*.json ./

# Install dependencies if package.json exists
RUN if [ -f package.json ]; then npm ci --only=production; fi

# Copy frontend files
COPY . .

# Stage 2: Runtime - Nginx for static content
FROM nginx:alpine

# Set labels
LABEL maintainer="LOKI DevOps Team"
LABEL app="loki-frontend"
LABEL version="1.0.0"

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy frontend files
COPY --from=builder /build /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 101 -S nginx-runner && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx-runner -g nginx-runner nginx-runner

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Run as non-root user
USER nginx-runner

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

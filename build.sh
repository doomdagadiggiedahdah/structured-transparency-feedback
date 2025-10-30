#!/bin/bash
# Build Docker images for structured-transparency

echo "Building landing page image..."
docker build -f Dockerfile.landing -t landing-page .

echo "Building event server image..."
docker build -f Dockerfile.event -t event-server .

echo ""
echo "✓ Images built successfully!"
echo ""
docker images | grep -E "REPOSITORY|landing-page|event-server"

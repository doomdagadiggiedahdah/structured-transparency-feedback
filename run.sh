#!/bin/bash
# Run structured-transparency services with SSL

# Stop and remove existing containers
docker stop nginx-ssl 2>/dev/null
docker rm nginx-ssl 2>/dev/null
docker stop landing 2>/dev/null
docker rm landing 2>/dev/null

# Create a network for the containers
docker network create landing-network 2>/dev/null || true

# Run landing page on internal network only (with Docker socket access)
echo "Starting landing page..."
docker run -d \
  --network landing-network \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e PUBLIC_IP=52.3.6.242 \
  --name landing \
  landing-page

# Run nginx with SSL - on landing-network to resolve "landing" hostname
echo "Starting nginx with SSL on ports 80, 443..."
docker run -d \
  --network landing-network \
  -p 80:80 \
  -p 443:443 \
  -v /home/ubuntu/nginx-ssl/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /home/ubuntu/nginx-ssl/certs:/etc/nginx/certs:ro \
  --name nginx-ssl \
  nginx:alpine

echo ""
echo "✓ Landing page running behind nginx with SSL"
echo "✓ HTTP (port 80) redirects to HTTPS"
echo "✓ HTTPS available on port 443"
echo ""
docker ps

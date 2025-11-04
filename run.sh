#!/bin/bash
# Run structured-transparency services with SSL

# Stop and remove existing containers
docker stop nginx-ssl 2>/dev/null
docker rm nginx-ssl 2>/dev/null
docker stop landing 2>/dev/null
docker rm landing 2>/dev/null

# Create a network for the containers
docker network create landing-network 2>/dev/null || true

# Run landing page with port exposed to host
echo "Starting landing page..."
docker run -d \
  --network host \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e PUBLIC_IP=52.3.6.242 \
  --name landing \
  landing-page

# Start event server on port 5001
echo "Starting event server..."
cd /home/ubuntu/structured-transparency
source .venv/bin/activate 2>/dev/null || true

# Kill any existing event_server processes
pkill -f "gunicorn.*event_server" 2>/dev/null || true

# Start event server on port 5001
gunicorn -w 4 -b 0.0.0.0:5001 event_server.app:app --daemon

# Run nginx with SSL using host network to access all ports
echo "Starting nginx with SSL on host network..."
docker run -d \
  --network host \
  -v /home/ubuntu/nginx-ssl/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /home/ubuntu/nginx-ssl/certs:/etc/nginx/certs:ro \
  --name nginx-ssl \
  nginx:alpine

echo ""
echo "✓ Landing page running on port 5000"
echo "✓ Event server running on port 5001"
echo "✓ Nginx with SSL proxying requests"
echo "✓ HTTP (port 80) redirects to HTTPS"
echo "✓ HTTPS available on port 443"
echo "✓ /federated/* routes to event server"
echo "✓ Session ports 8000-9000 available with SSL"
echo ""
docker ps

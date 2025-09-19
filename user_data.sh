#!/bin/bash
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install dependencies
apt-get install -y \
    docker.io \
    docker-compose \
    curl \
    jq \
    bc \
    nginx \
    openssl \
    git \
    cron \
    awscli

# Start Docker
systemctl start docker
systemctl enable docker

# Clone repository (replace with your repo)
cd /opt
git clone https://github.com/your-username/autonomous-jarvis.git || \
  mkdir -p autonomous-jarvis

cd autonomous-jarvis

# Copy deployment files (assuming they're in the repo)
# If not, you can download them from S3 or another source

# Run deployment
./deploy.sh

# Configure domain (if provided)
if [ -n "${domain}" ]; then
    # Update nginx configuration with the domain
    sed -i "s/server_name _;/server_name ${domain};/g" /etc/nginx/sites-available/default
    systemctl reload nginx
fi

echo "🚀 Autonomous JARVIS deployed successfully!"

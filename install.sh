#!/bin/bash

set -e

echo "=== Dementia Companion Installer ==="

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not available"
    exit 1
fi

# Clone repo
if [ ! -d "dementia-companion" ]; then
    echo "Cloning repo from GitHub..."
    git clone https://github.com/miles-a0/dementia-companion.git
fi

cd dementia-companion

# Build frontend
echo "Building frontend..."
cd companion-frontend
npm install
npm run build
cd ..

# Create network if it doesn't exist
echo "Checking network..."
if ! docker network ls | grep -q companion-net; then
    echo "Creating network companion-net..."
    docker network create companion-net
else
    echo "Network companion-net already exists"
fi

# Update passwords
echo ""
echo "=== Configuration ==="
read -p "Enter PostgreSQL password: " -s POSTGRES_PASSWORD
echo ""
read -p "Enter Carer password: " -s CARER_PASSWORD
echo ""

# Create .env file
cat > companion-backend/.env << EOF
QDRANT_URL=http://173.249.40.161:5467
N8N_URL=https://n8n.zu-auto.co.uk
N8N_LEARNING_WEBHOOK_URL=https://n8n.zu-auto.co.uk/webhook/learning-loop
IMMICH_URL=http://173.249.40.161:2283
IMMICH_API_KEY=eeq1EQNyIWKSH03tAVV4ojPBp3hNcMQwI7NDgSwh1o
VIKUNJA_URL=https://vik.zu-auto.co.uk
VIKUNJA_API_KEY=tk_78320358404f85c3fe92b139dc307d04ba3de518
OPENROUTER_API_KEY=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
DATABASE_URL=postgresql://companion:${POSTGRES_PASSWORD}@db:5432/companion
JWT_SECRET=zY8rJpQ4sVn2XcKfL1aW7eTgH5uBqD3mR6yN0oI8pCwSxE4FvUjZkG1hM2lA9t
CARER_USERNAME=carer
CARER_PASSWORD=${CARER_PASSWORD}
JOHN_LAT=53.8317
JOHN_LON=-2.2340
JOHN_USER_ID=1
WHISPER_URL=http://whisper:8000
EOF

# Update password in compose file
sed -i "s/your_secure_password_here/$POSTGRES_PASSWORD/g" docker-compose.companion.yml

echo ""
echo "=== Building and starting containers ==="
docker compose -f docker-compose.companion.yml build --no-cache
docker compose -f docker-compose.companion.yml up -d

echo ""
echo "=== Status ==="
docker compose -f docker-compose.companion.yml ps

echo ""
echo "=== Done ==="
echo "API should be available at: http://localhost:5471"
echo "Check logs with: docker compose -f docker-compose.companion.yml logs"
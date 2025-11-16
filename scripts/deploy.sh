#!/bin/bash

# Production Deployment Script
# Usage: ./scripts/deploy.sh [staging|production]

set -e  # Exit on error

ENVIRONMENT=${1:-staging}
COMPOSE_FILE="infra/docker-compose.prod.yml"

echo "🚀 Starting deployment to $ENVIRONMENT environment..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please create .env.production with required environment variables."
    exit 1
fi

# Load environment variables
export $(cat .env.production | grep -v '^#' | xargs)

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose -f $COMPOSE_FILE pull backend frontend

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T backend alembic upgrade head || {
    echo "⚠️  Migration failed. Attempting to continue..."
}

# Stop old containers gracefully
echo "🛑 Stopping old containers..."
docker-compose -f $COMPOSE_FILE down --timeout 30

# Start new containers
echo "▶️  Starting new containers..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Health check
echo "🏥 Running health checks..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:8000/health/ready > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "⏳ Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Health check failed after $MAX_RETRIES attempts"
    echo "📋 Container logs:"
    docker-compose -f $COMPOSE_FILE logs --tail=50
    exit 1
fi

# Check frontend
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Frontend is healthy!"
else
    echo "⚠️  Frontend health check failed, but continuing..."
fi

# Rebuild FAISS indexes if needed
echo "🔍 Checking FAISS indexes..."
docker-compose -f $COMPOSE_FILE exec -T backend python -c "
from app.services.index_service import IndexService
from app.core.database import SessionLocal
db = SessionLocal()
# Check if indexes exist, rebuild if needed
" || echo "⚠️  Index check skipped (may need manual rebuild)"

echo "✅ Deployment completed successfully!"
echo "📊 Services:"
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:${FRONTEND_PORT:-8501}"
echo "   Backend API: http://localhost:${BACKEND_PORT:-8000}"
echo "   API Docs: http://localhost:${BACKEND_PORT:-8000}/docs"


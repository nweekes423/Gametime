#!/bin/bash

# Simple Docker Test Script
set -e

echo "=================================="
echo "🐳 Simple Docker Test"
echo "=================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 1. Test PostgreSQL and Redis only
echo ""
echo "🔍 Testing PostgreSQL and Redis..."
docker-compose up -d postgres redis

sleep 15

if docker-compose ps postgres | grep -q "healthy"; then
    print_success "PostgreSQL is healthy"
else
    print_error "PostgreSQL failed"
    docker-compose down
    exit 1
fi

if docker-compose ps redis | grep -q "healthy"; then
    print_success "Redis is healthy"
else
    print_error "Redis failed"
    docker-compose down
    exit 1
fi

# 2. Test Django with minimal setup
echo ""
echo "🔍 Testing Django container..."
docker-compose up -d django

sleep 20

echo ""
echo "📋 Django container logs:"
docker-compose logs django

echo ""
echo "📋 Container status:"
docker-compose ps

# 3. Check if Django is healthy
if docker-compose ps django | grep -q "healthy"; then
    print_success "Django is healthy"
else
    print_error "Django failed to become healthy"
fi

# 4. Cleanup
echo ""
echo "🧹 Cleaning up..."
docker-compose down

echo ""
echo "=================================="
echo "✅ Simple Docker Test Complete"
echo "=================================="
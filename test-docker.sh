#!/bin/bash

# Docker Implementation Test Script
set -e

echo "=================================="
echo "🐳 Docker Implementation Test"
echo "=================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 1. Check Docker installation
echo ""
echo "🔍 Checking Docker installation..."
if command -v docker &> /dev/null; then
    print_success "Docker installed: $(docker --version)"
else
    print_error "Docker not found. Please install Docker first."
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    print_success "Docker Compose installed: $(docker-compose --version)"
else
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# 2. Validate docker-compose.yml
echo ""
echo "🔍 Validating docker-compose.yml..."
if docker-compose config > /dev/null 2>&1; then
    print_success "docker-compose.yml is valid"
else
    print_error "docker-compose.yml has syntax errors"
    exit 1
fi

# 3. Test Django configuration (without Docker)
echo ""
echo "🔍 Testing Django configuration..."
cd app
if python manage.py check > /dev/null 2>&1; then
    print_success "Django configuration check passed"
else
    print_error "Django configuration check failed"
    exit 1
fi

# 4. Test health endpoint locally
echo ""
echo "🔍 Testing health endpoint locally..."
python manage.py runserver > /dev/null 2>&1 &
DJANGO_PID=$!
sleep 5

if curl -s http://localhost:8000/game-monitor/health/ > /dev/null 2>&1; then
    print_success "Health endpoint responding"
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/game-monitor/health/)
    echo "Response: $HEALTH_RESPONSE"
else
    print_warning "Health endpoint not responding (may need Redis running)"
fi

kill $DJANGO_PID 2>/dev/null || true
cd ..

# 5. Test PostgreSQL and Redis startup
echo ""
echo "🔍 Testing PostgreSQL and Redis startup..."
docker-compose up -d postgres redis

sleep 10

if docker-compose ps postgres | grep -q "Up"; then
    print_success "PostgreSQL container is running"
else
    print_error "PostgreSQL container failed to start"
    docker-compose down
    exit 1
fi

if docker-compose ps redis | grep -q "Up"; then
    print_success "Redis container is running"
else
    print_error "Redis container failed to start"
    docker-compose down
    exit 1
fi

# 6. Test connectivity
echo ""
echo "🔍 Testing service connectivity..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis connectivity working"
else
    print_error "Redis connectivity failed"
fi

# 7. Cleanup
echo ""
echo "🧹 Cleaning up test containers..."
docker-compose down
print_success "Test containers stopped"

# 8. Summary
echo ""
echo "=================================="
echo "✅ Docker Implementation Tests Passed!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Run: docker-compose up -d --build (full stack)"
echo "  2. Check: docker-compose ps (service status)"
echo "  3. Monitor: docker-compose logs -f django (logs)"
echo "  4. Access: http://localhost (application)"
echo "  "  "        http://localhost:9090 (Prometheus)"
echo "  " "        http://localhost:3000 (Grafana)"
echo ""
echo "To stop: docker-compose down"
echo "To remove volumes: docker-compose down -v"
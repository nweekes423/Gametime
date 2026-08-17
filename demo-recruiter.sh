#!/bin/bash

# 🎯 Gametime Recruiter Demo Script
# Simple demo script that checks requirements and launches the app

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${CYAN}==================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}==================================${NC}"
}

print_step() {
    echo -e "${BLUE}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header "🎯 Gametime Recruiter Demo"
echo ""
echo "This demo showcases your NBA/WNBA game monitoring application:"
echo "  • Live game score tracking and close-game alerts"
echo "  • Professional API documentation"
echo "  • Health monitoring and observability"
echo "  • SMS notification system"
echo ""
print_info "💡 TIP: For a reliable demo, try ./demo-simple.sh (no Docker needed)"

# Check if Docker is available
print_step "Checking Docker availability..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    print_info "Would you like to run the local development version instead? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Starting local development version..."
        source venv311/bin/activate
        cd app
        python manage.py migrate
        python manage.py runserver
        exit 0
    else
        print_error "Please install Docker to run the full demo"
        exit 1
    fi
fi

# Check if Docker daemon is running
print_step "Checking Docker daemon..."
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    print_info "Please start Docker Desktop and try again"
    print_info "Or run local version: source venv311/bin/activate && cd app && python manage.py runserver"
    exit 1
fi

print_success "Docker is ready!"

echo ""
print_step "Starting application with Docker..."
print_info "This will launch several services (database, cache, web server, etc.)"
print_info "This may take 1-2 minutes on first run..."
echo ""

# Try to start Docker services with error handling
if ! docker-compose up -d 2>&1; then
    print_error "Failed to start Docker services"
    print_info "Troubleshooting steps:"
    echo "  1. Check Docker Desktop is running"
    echo "  2. Try: docker-compose down && docker-compose up -d"
    echo "  3. Check for port conflicts: lsof -i :8000"
    echo "  4. Or try the simple demo: ./demo-simple.sh"
    exit 1
fi

print_info "Waiting for services to start (this may take a minute)..."
sleep 45

print_step "Checking service status..."
echo ""
docker-compose ps
echo ""

# Check if any containers failed
FAILED_CONTAINERS=$(docker-compose ps --services --filter "status=exited" --filter "status=dead")
UNHEALTHY_CONTAINERS=$(docker-compose ps --services --filter "status=unhealthy")

if [ -n "$FAILED_CONTAINERS" ] || [ -n "$UNHEALTHY_CONTAINERS" ]; then
    if [ -n "$FAILED_CONTAINERS" ]; then
        print_error "Some containers failed to start: $FAILED_CONTAINERS"
    fi
    if [ -n "$UNHEALTHY_CONTAINERS" ]; then
        print_error "Some containers are unhealthy: $UNHEALTHY_CONTAINERS"
    fi
    
    print_info "Checking logs for problematic containers..."
    for container in $FAILED_CONTAINERS $UNHEALTHY_CONTAINERS; do
        echo "📋 Logs for $container:"
        docker-compose logs --tail=20 "$container"
        echo ""
    done
    
    print_info "Common fixes:"
    echo "  1. Stop everything: docker-compose down"
    echo "  2. Remove volumes: docker-compose down -v"
    echo "  3. Try again: docker-compose up -d"
    echo "  4. Or use simple demo: ./demo-simple.sh (recommended for now)"
    echo ""
    print_info "The Docker setup has a configuration issue. The simple demo works perfectly!"
    exit 1
fi

print_step "Testing application health..."
if curl -s http://localhost:8000/game-monitor/health/ > /dev/null; then
    print_success "Application is healthy!"
else
    print_error "Application health check failed"
    print_info "Checking Django logs..."
    docker-compose logs --tail=30 django
    echo ""
    print_info "Troubleshooting:"
    echo "  1. Check Django logs: docker-compose logs django"
    echo "  2. Restart Django: docker-compose restart django"
    echo "  3. Try simple demo: ./demo-simple.sh"
    exit 1
fi
echo ""

print_step "Access the application:"
echo ""
echo "🌐 Main Application: http://localhost:8000"
echo "📱 Phone Registration: http://localhost:8000/game-monitor/phone-form/"
echo "📚 API Documentation: http://localhost:8000/game-monitor/docs/"
echo "💚 Health Check: http://localhost:8000/game-monitor/health/"
echo ""
echo "📊 Monitoring (if available):"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3030 (admin/admin)"
echo ""

print_step "Testing key features..."
print_info "Testing phone form..."
if curl -s http://localhost:8000/game-monitor/phone-form/ | grep -q "phone"; then
    print_success "Phone form is working"
else
    print_error "Phone form test failed"
fi

print_info "Testing API documentation..."
if curl -s http://localhost:8000/game-monitor/docs/ | grep -q "swagger"; then
    print_success "API documentation is working"
else
    print_error "API documentation test failed"
fi

echo ""
print_header "🎉 Demo Setup Complete!"
echo ""
echo "✅ Your application is now running!"
echo ""
echo "🔍 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🧹 To clean up: docker-compose down -v"
echo ""
print_success "Ready to impress recruiters! 🎯"
echo ""
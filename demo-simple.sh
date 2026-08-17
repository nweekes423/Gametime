#!/bin/bash

# 🎯 Simple Gametime Demo (No Docker Required)
# This runs the app locally for quick demonstrations

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

print_header "🎯 Gametime Simple Demo"
echo ""
echo "Quick demo of your NBA/WNBA game monitoring app"
echo ""

# Check if virtual environment exists
print_step "Checking virtual environment..."
if [ ! -d "venv311" ]; then
    print_error "Virtual environment not found"
    print_info "Create it with: python3.11 -m venv venv311"
    exit 1
fi

print_success "Virtual environment found"

# Activate virtual environment
print_step "Activating virtual environment..."
source venv311/bin/activate

# Check if Django is installed
print_step "Checking dependencies..."
if ! python -c "import django" &> /dev/null; then
    print_error "Django not installed"
    print_info "Install dependencies: pip install -r requirements.txt"
    exit 1
fi

print_success "Dependencies are installed"

# Run migrations
print_step "Setting up database..."
cd app
python manage.py migrate --no-input
print_success "Database is ready"

# Start the server in background
print_step "Starting the application..."
print_info "The server will start in the background"
python manage.py runserver 8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
print_info "Waiting for server to start..."
sleep 5

# Test if server is running
print_step "Testing application..."
if curl -s http://localhost:8000/game-monitor/health/ > /dev/null; then
    print_success "Application is running!"
else
    print_error "Application failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
print_header "🎉 Demo is Ready!"
echo ""
echo "🌐 Access your application at:"
echo "   • Main page: http://localhost:8000"
echo "   • Phone form: http://localhost:8000/game-monitor/phone-form/"
echo "   • API docs: http://localhost:8000/game-monitor/docs/"
echo "   • Health check: http://localhost:8000/game-monitor/health/"
echo ""
echo "🔍 The server is running in background (PID: $SERVER_PID)"
echo "🛑 To stop: kill $SERVER_PID"
echo "📋 To view logs: Check the terminal output"
echo ""
print_success "Your app is ready for the demo! 🎯"

# Keep the script running
print_info "Press Ctrl+C to stop the server"
trap "kill $SERVER_PID 2>/dev/null; print_info 'Server stopped'; exit 0" INT

# Wait for user to stop
wait $SERVER_PID
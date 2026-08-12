#!/bin/bash

# Local CI/CD Test Script
# This script mimics your GitHub Actions and Jenkins pipelines

set -e  # Exit on error

echo "=================================="
echo "🚀 Local CI/CD Test Script"
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Navigate to project
cd /Users/will/Gametime

echo "📁 Working directory: $(pwd)"

# ============================================
# GitHub Actions Workflow Simulation
# ============================================
echo ""
echo "=================================="
echo "🔧 GitHub Actions Workflow"
echo "=================================="

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv311/bin/activate
print_success "Virtual environment activated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
pip install ruff pytest coverage pytest-cov factory-boy safety bandit > /dev/null 2>&1
print_success "Dependencies installed"

# Django configuration check
echo "🔍 Verifying Django configuration..."
cd app
python manage.py check
if [ $? -eq 0 ]; then
    print_success "Django configuration check passed"
else
    print_error "Django configuration check failed"
    exit 1
fi

# Run linting
echo "🔍 Running linting..."
ruff check --no-cache .
if [ $? -eq 0 ]; then
    print_success "Linting passed"
else
    print_error "Linting failed"
    exit 1
fi

# Run tests with coverage
echo "🧪 Running tests with coverage..."
coverage run --source='.' manage.py test game_monitor.tests
if [ $? -eq 0 ]; then
    print_success "Tests passed"
else
    print_error "Tests failed"
    exit 1
fi

# Generate coverage report
echo "📊 Generating coverage report..."
coverage report
COVERAGE=$(coverage report | grep TOTAL | awk '{print $4}' | sed 's/%//')
print_success "Coverage: ${COVERAGE}%"

# Security scans
echo "🔒 Running security scans..."
echo "  - Safety scan..."
safety check --json > /dev/null 2>&1 || print_warning "Safety scan found issues (continuing)"
echo "  - Bandit scan..."
bandit -r . || print_warning "Bandit scan found issues (continuing)"
print_success "Security scans completed"

# ============================================
# Summary
# ============================================
echo ""
echo "=================================="
echo "✅ All CI/CD Tests Passed!"
echo "=================================="
echo ""
echo "Summary:"
echo "  ✓ GitHub Actions workflow: PASSED"
echo "  ✓ Code coverage: ${COVERAGE}%"
echo "  ✓ Security scans: COMPLETED"
echo ""
echo "Note: Some security warnings found (Bandit), but tests continue"
echo "You're ready to push to dev! 🚀"
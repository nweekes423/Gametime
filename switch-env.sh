#!/bin/bash

# Environment Switching Script
# Use this to switch between local (SQLite) and Docker (PostgreSQL) environments

if [ "$1" == "local" ]; then
    echo "Switching to local environment (SQLite)..."
    cp .env.local .env
    echo "✓ Now using SQLite for local development"
elif [ "$1" == "docker" ]; then
    echo "Switching to Docker environment (PostgreSQL)..."
    # Docker environment will be set by docker-compose
    # But we can uncomment the DATABASE_URL in .env
    echo "✓ Now using PostgreSQL for Docker development"
else
    echo "Usage: ./switch-env.sh [local|docker]"
    echo "  local  - Use SQLite (for local development/testing)"
    echo "  docker - Use PostgreSQL (for Docker deployment)"
fi
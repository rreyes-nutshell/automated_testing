#!/bin/bash
set -e

echo "🛑 Stopping and removing containers and volumes..."
docker-compose down -v

echo "🧱 Rebuilding all services without cache..."
docker-compose build --no-cache

echo "🚀 Starting up fresh containers..."
docker-compose up -d --remove-orphans

echo "✅ Project reset complete."

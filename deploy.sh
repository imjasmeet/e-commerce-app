#!/bin/bash

echo "🚀 Deploying E-Commerce App with Docker Compose..."

# Stop any existing containers
echo "📦 Stopping existing containers..."
docker-compose down

# Build and start the application
echo "🔨 Building and starting the application..."
docker-compose up --build -d

# Wait for the application to be ready
echo "⏳ Waiting for application to be ready..."
sleep 10

# Check if the application is running
echo "🔍 Checking application status..."
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access the app at: http://localhost:8000"
    echo "📊 View logs with: docker-compose logs -f"
else
    echo "❌ Application failed to start. Check logs with: docker-compose logs"
    exit 1
fi

echo "🎉 Deployment complete!" 
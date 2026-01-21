#!/bin/bash
# Startup script for Koyeb - builds frontend then starts Flask

set -e  # Exit on error

echo "🚀 Starting deployment process..."

# Build frontend if not already built
if [ ! -d "dist" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
    
    echo "🏗️  Building React frontend..."
    npm run build
else
    echo "✅ dist/ folder already exists, skipping build"
fi

# Start Flask with gunicorn
echo "🐍 Starting Flask application..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

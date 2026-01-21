#!/bin/bash
# Build script for Koyeb deployment

echo "🔧 Installing Node.js dependencies..."
npm install

echo "🏗️  Building React frontend..."
npm run build

echo "✅ Build complete! Frontend ready in dist/"

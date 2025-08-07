#!/bin/bash

# Build the frontend
echo "Building frontend..."
cd frontend
npm install
npm run build

# Copy built frontend to backend static directory
echo "Copying frontend build to backend..."
mkdir -p ../backend/static
cp -r build/* ../backend/static/

echo "Build complete!" 
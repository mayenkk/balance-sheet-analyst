#!/bin/bash

# Create conda environment
echo "Creating conda environment..."
conda env create -f backend/environment.yml

# Activate conda environment
echo "Activating conda environment..."
source activate analyst-env

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
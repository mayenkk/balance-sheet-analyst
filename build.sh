#!/bin/bash

# Install Node.js if not available
if ! command -v node &> /dev/null; then
    echo "Node.js not found, installing..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

# Check Node.js and npm
echo "Node.js version:"
node --version
echo "npm version:"
npm --version

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
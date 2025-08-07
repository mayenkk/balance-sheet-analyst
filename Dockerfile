# Use Python base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy package files
COPY package.json ./
COPY frontend/package.json ./frontend/

# Install Node.js dependencies
RUN cd frontend && npm install

# Copy application code
COPY . .

# Build frontend
RUN cd frontend && npm run build

# Copy built frontend to backend static directory
RUN mkdir -p backend/static && cp -r frontend/build/* backend/static/

# Expose port
EXPOSE 8000

# Start command - use $PORT environment variable
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT"] 
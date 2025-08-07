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

# Copy Python dependencies and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend package.json and install Node deps
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm install

# Copy the rest of the codebase
COPY . .

# Build React frontend
RUN cd frontend && npm run build

# Move frontend build to backend static
RUN mkdir -p backend/static && cp -r frontend/build/* backend/static/

# Set working directory to backend for server launch
WORKDIR /app/backend

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI using direct uvicorn call
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
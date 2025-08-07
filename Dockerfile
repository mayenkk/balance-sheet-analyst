# Use a base image with both Python and Node.js
FROM node:18-alpine

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    curl \
    wget \
    git

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

# Add conda to PATH
ENV PATH="/opt/conda/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY frontend/package.json ./frontend/
COPY backend/environment.yml ./backend/

# Install Node.js dependencies
RUN cd frontend && npm install

# Create conda environment
RUN conda env create -f backend/environment.yml

# Copy application code
COPY . .

# Build frontend
RUN cd frontend && npm run build

# Copy built frontend to backend static directory
RUN mkdir -p backend/static && cp -r frontend/build/* backend/static/

# Expose port
EXPOSE 8000

# Start command
CMD ["/bin/bash", "-c", "source activate analyst-env && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"] 
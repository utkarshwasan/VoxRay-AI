# Stage 1: Build the React Frontend
FROM node:20-alpine as frontend-builder
WORKDIR /app/frontend

# Copy package files first for better caching
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python Backend & Runtime
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
# libsndfile1: Required by librosa/soundfile
# ffmpeg: Required by edge-tts and general audio handling
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend Code
COPY backend/ /app/backend/

# Copy Built Frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Set Environment Variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose Port
EXPOSE 8000

# Run Uvicorn Server
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
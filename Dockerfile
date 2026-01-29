FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (Audio + TF support)
RUN apt-get update && apt-get install -y \
    libsndfile1 ffmpeg libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create user (Hugging Face Security Requirement)
RUN useradd -m -u 1000 user && mkdir -p /app && chown -R user:user /app

# Switch to user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

# Install dependencies (Cached layer)
COPY --chown=user:user backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy Application Code
COPY --chown=user:user backend/ ./backend/


# Hugging Face Port
EXPOSE 7860

# Robust Health Check (Standard Lib)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7860/health', timeout=5)" || exit 1

# Launch
CMD ["python", "-m", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]

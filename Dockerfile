# Dockerfile for Nino Medical AI - Italian Medical NER
FROM python:3.11.7-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
COPY web_demo_requirements.txt .
COPY api_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r web_demo_requirements.txt && \
    pip install --no-cache-dir -r api_requirements.txt && \
    pip install --no-cache-dir streamlit fastapi uvicorn

# Copy application files
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose ports
EXPOSE 8501 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command (can be overridden)
CMD ["streamlit", "run", "web_demo_app.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including ones needed for PyMuPDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    libmagic1 \
    # Additional dependencies for PyMuPDF
    libmupdf-dev \
    mupdf-tools \
    libfreetype6-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install LibreOffice for file conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create temporary directory for file processing
RUN mkdir -p /app/tmp && chmod 777 /app/tmp

# Create non-root user and set permissions
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 
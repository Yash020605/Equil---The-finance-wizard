# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for Tesseract, Postgres, etc.)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libmagic1 \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the backend code
COPY . .

# Install Python dependencies
# Fallback hardcoded install to guarantee build success if requirements.txt is absent
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; else pip install --no-cache-dir fastapi uvicorn pydantic pandas numpy google-cloud-vision pytesseract Pillow langchain_core langgraph sqlalchemy asyncpg; fi

# Expose port
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

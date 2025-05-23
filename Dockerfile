# Dockerfile
FROM python:3.12-slim

# Create a non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Install system deps (if any) and cleanup
RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Chown everything to appuser
RUN chown -R appuser:appuser /home/appuser

# Switch to non-root user
USER appuser

# Expose Uvicorn port
EXPOSE 8000

# Unbuffered Python output for logs
ENV PYTHONUNBUFFERED=1

# Command to run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

# Gradio UI Dockerfile
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements for UI
COPY requirements-ui.txt ./requirements-ui.txt

# Install UI dependencies
RUN pip install --no-cache-dir -r requirements-ui.txt

# Copy UI source code
COPY ui/ ./ui/

# Expose Gradio default port
EXPOSE 7860

# Set environment variables
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV PYTHONPATH=/app

# Run Gradio app
CMD ["python", "ui/app.py"]
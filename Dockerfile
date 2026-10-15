FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set default Streamlit port (supports Cloud Run $PORT)
ENV PORT=8501
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Start Streamlit application
ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (keeps the same structure the code expects)
COPY backend/ backend/
COPY sample_data/ sample_data/

# The code auto-loads the CSV from: /app/sample_data/sardarit_projects_database.csv

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Start FastAPI server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

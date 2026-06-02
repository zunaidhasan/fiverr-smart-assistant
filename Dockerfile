FROM python:3.11

WORKDIR /app

# Install dependencies first (leverages Docker layer caching)
COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend/ backend/
COPY sample_data/ sample_data/

# The CSV auto-loads from: /app/sample_data/sardarit_projects_database.csv
# (resolved by main.py as ../sample_data/ relative to backend/)

EXPOSE 8000

# PORT env is set by Render or defaults to 8000 in main.py
ENTRYPOINT []
CMD exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}

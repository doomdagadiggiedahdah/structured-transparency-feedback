FROM python:3.11-slim

WORKDIR /app

# Copy package files
COPY event_server/ ./event_server/
COPY pyproject.toml ./

# Install dependencies using pip (uv would be better but keeping it simple for Docker)
RUN pip install --no-cache-dir -e .

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "event_server.app:app"]

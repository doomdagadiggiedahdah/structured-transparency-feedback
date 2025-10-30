FROM python:3.11-slim

WORKDIR /app

# Copy package files
COPY landing_page/ ./landing_page/
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -e .

EXPOSE 5000

# Use gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "landing_page.app:app"]

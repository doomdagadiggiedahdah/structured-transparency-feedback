# Structured Transparency

Event-driven transparency platform with dynamic Q&A sessions.

## Quick Start (Docker)

```bash
# Build images
./build.sh

# Run landing page on port 80
./run.sh
```

Your landing page will be available at `http://your-server-ip`

## Manual Docker Commands

```bash
# Build images
docker build -f Dockerfile.landing -t landing-page .
docker build -f Dockerfile.event -t event-server .

# Run landing page on port 80
docker run -d -p 80:5000 --name landing landing-page

# Run event server on a different port (for testing)
docker run -d -p 5001:5000 --name event event-server
```

## Project Structure

```
structured-transparency/
├── event_server/          # Session management service
│   ├── __init__.py
│   ├── app.py            # Flask app factory
│   ├── routes.py         # API endpoints
│   ├── models.py         # Data models
│   └── templates/        # HTML templates
├── landing_page/         # Landing page service
│   ├── __init__.py
│   ├── app.py           # Flask app factory
│   ├── routes.py        # Routes
│   └── templates/       # HTML templates
├── Dockerfile.landing    # Landing page Docker image
├── Dockerfile.event      # Event server Docker image
├── build.sh             # Build script
├── run.sh               # Run script
└── pyproject.toml       # Python dependencies
```

## Development (Without Docker)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create venv and install
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run event server
PORT=8000 python -m event_server.app

# Run landing page
PORT=8001 python -m landing_page.app
```

## API Endpoints

### Event Server
- GET / - Admin interface
- GET /participant - Participant interface
- GET /api/state - Get session state
- POST /api/questions - Update questions
- POST /api/expire-time - Set expiration time
- POST /api/close-collection - Close feedback collection
- POST /api/submit-feedback - Submit participant feedback
- GET /health - Health check

### Landing Page
- GET / - Landing page
- POST /create-session - Create new session (TODO: spawn event-server container)

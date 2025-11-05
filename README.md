# Structured Transparency

Event-driven transparency platform with dynamic Q&A sessions and AI-powered report generation.

## Features

- 📱 **Mobile voice recording** with client-side transcription (Whisper)
- 🤖 **AI-powered reports** using Claude 3.5 Haiku
- 🔒 **Privacy-first**: Ephemeral data (dies with container)
- ⚡ **Real-time feedback** collection
- 📊 **Automatic insights** from participant responses

## Quick Start (Docker)

```bash
# Build images
./build.sh

# Run landing page on port 80
./run.sh
```

Your landing page will be available at `http://your-server-ip`

## Environment Variables

**Required for AI features:**
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Then pass it to containers:
```bash
docker run -d -p 8000:5000 -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" --name session session-server
```

## Manual Docker Commands

```bash
# Build images
docker build -f Dockerfile.landing -t landing-page .
docker build -f Dockerfile.event -t session-server .

# Run landing page on port 80
docker run -d -p 80:5000 --name landing landing-page

# Run event server (single worker for in-memory state)
docker run -d -p 8000:5000 -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  --name session session-server \
  gunicorn -w 1 -b 0.0.0.0:5000 event_server.app:app
```

⚠️ **Note**: Use `-w 1` (single worker) for now since session data is in-memory.

## Project Structure

```
structured-transparency/
├── event_server/          # Session management service
│   ├── app.py            # Flask app with API endpoints
│   ├── models.py         # SessionData model
│   ├── llm.py            # AI report generation
│   ├── routes.py         # (unused, kept for future)
│   ├── templates/        # HTML templates
│   └── tests/            # Test suite
├── landing_page/         # Landing page service
│   ├── app.py           # Flask app
│   ├── routes.py        # Routes
│   └── templates/       # HTML templates
├── Dockerfile.landing    # Landing page image
├── Dockerfile.event      # Event server image
├── DATAFLOW.md          # Data structures & lifecycle
├── IMPLEMENTATION_SUMMARY.md  # Implementation details
└── pyproject.toml       # Dependencies
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

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run event server
PORT=8000 python -m event_server.app

# Run landing page
PORT=8001 python -m landing_page.app
```

## Testing

```bash
# Run test suite
uv run pytest event_server/tests/ -v

# Test end-to-end flow
./test_full_flow.sh

# Test report generation (requires API key)
python test_report.py
```

## API Endpoints

### Event Server

**Participant Endpoints:**
- `GET /participant` - Participant interface (voice recording)
- `POST /api/submit-feedback` - Submit feedback (auto-called from frontend)

**Admin Endpoints:**
- `GET /` - Admin interface
- `GET /api/state` - Get session state (questions, feedback, report)
- `POST /api/questions` - Update questions
- `POST /api/expire-time` - Set expiration time
- `POST /api/close-collection` - Stop accepting feedback
- `POST /api/generate-report` - Generate AI report from feedback ✨

**Utility:**
- `GET /health` - Health check

### Landing Page
- `GET /` - Landing page
- `POST /create-session` - Create new session (spawns event-server container)
- `GET /health` - Health check

## How It Works

1. **Admin** creates session and optionally sets questions
2. **Participant** opens mobile page, records voice response
3. **Whisper** transcribes audio client-side (privacy!)
4. **Frontend** automatically sends transcription to server on Export
5. **Admin** closes collection and generates report
6. **Claude Haiku** analyzes feedback and creates summary
7. **Container stops** → all data destroyed (privacy!)

## Documentation

- **[DATAFLOW.md](DATAFLOW.md)** - Data structures, lifecycle, and API reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details and usage
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and deployment

## License

MIT

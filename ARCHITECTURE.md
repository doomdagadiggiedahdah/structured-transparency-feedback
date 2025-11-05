# Structured Transparency - Architecture Overview

## Directory Structure

```
structured-transparency/
├── event_server/          # Session container code
│   ├── __init__.py       # Package init, exports Flask app
│   ├── app.py            # Flask app with embedded admin HTML + API endpoints
│   ├── models.py         # Data models (SessionData dataclass)
│   ├── llm.py            # LLM integration (Claude 3.5 Haiku)
│   ├── routes.py         # API routes (currently unused)
│   ├── static/           # worker.js for transcription
│   ├── templates/        # participant.html, admin.html.source, README_ADMIN.md
│   └── tests/            # Test suite (pytest)
│
├── landing_page/         # Landing page / session orchestrator
│   ├── __init__.py      # Package init, exports Flask app
│   ├── app.py           # Flask app, creates session containers
│   ├── routes.py        # Routes
│   ├── static/          # CSS, assets (currently empty)
│   └── templates/       # index.html, confirmation.html
│
├── Dockerfile.event     # Builds session-server image
├── Dockerfile.landing   # Builds landing-page image
├── DATAFLOW.md          # Data structures & lifecycle documentation
├── IMPLEMENTATION_SUMMARY.md  # Implementation details
├── build.sh            # Builds both images
└── run.sh              # Starts landing + nginx with SSL
```

## Docker Architecture

### Images

| Image | Built From | Purpose |
|-------|-----------|---------|
| **session-server** | `Dockerfile.event` | Serves participant & admin pages + AI report generation |
| **landing-page** | `Dockerfile.landing` | Landing page + orchestrates session containers |
| **nginx:alpine** | Official image | SSL reverse proxy |

### Running Containers

| Container | Image | Ports | Purpose |
|-----------|-------|-------|---------|
| **landing** | landing-page | 5000 | Landing page, creates session containers via Docker socket |
| **session-XXXXXX** | session-server | 8000-9000 | Individual session (created dynamically per user) |
| **nginx-ssl** | nginx:alpine | 80, 443 | HTTPS termination, proxies to landing + sessions |

⚠️ **Important**: Sessions should run with **single gunicorn worker** (`-w 1`) for now since `SessionData` is in-memory and not shared across workers.

## Request Flow

```
User → HTTPS (443) → nginx-ssl → Landing page (5000)
                                ↓
                         Creates session container
                                ↓
User → HTTPS (443) → nginx-ssl → Session (800X) → Participant/Admin pages
                                                 ↓
                                          Records voice → Whisper (client-side)
                                                 ↓
                                          Submits to /api/submit-feedback
                                                 ↓
                                          Admin calls /api/generate-report
                                                 ↓
                                          Claude Haiku analyzes feedback
```

## Key Components

### Landing Page (`landing_page/`)
- Creates QR codes
- Spawns session containers dynamically
- Mounts `/var/run/docker.sock` to control Docker
- **Templates**: 
  - `index.html`: Main landing page
  - `confirmation.html`: Session creation confirmation

### Session Server (`event_server/`)

#### Data Models (`models.py`)
- **`SessionData` dataclass**: Manages ephemeral session state
  - `session_id`: Unique identifier
  - `questions`: List of questions to ask
  - `is_collecting`: Whether accepting new feedback
  - `expire_time`: Session expiration
  - `feedback`: Array of question+answer+timestamp dicts
  - `generated_report`: AI-generated summary (None until generated)

#### LLM Integration (`llm.py`)
- **`generate_report(feedback)`**: Calls Anthropic Claude 3.5 Haiku
- Requires `ANTHROPIC_API_KEY` environment variable
- Model: `claude-3-5-haiku-20241022`
- Returns formatted analysis with themes, insights, and recommendations

#### API Endpoints (`app.py`)

**Participant:**
- `GET /participant` - Voice recording interface
- `POST /api/submit-feedback` - Receives transcribed feedback
  - Accepts `{"items": [{"question": "Q", "answer": "A"}, ...]}`
  - Stores in `session_data.feedback`

**Admin:**
- `GET /` - Admin dashboard
- `GET /api/state` - Get full session state (including report)
- `POST /api/questions` - Set questions
- `POST /api/expire-time` - Set expiration
- `POST /api/close-collection` - Stop accepting feedback
- `POST /api/generate-report` - **NEW**: Generate AI report ✨

#### Frontend
- **Participant page** (`templates/participant.html`):
  - Records audio via browser API
  - Transcribes client-side using Whisper (Web Worker)
  - Auto-submits to server on Export
  - Default question: "Please share your general reflections"
- **Admin page** (embedded in `app.py` line 18):
  - Source: `templates/admin.html.source` (sync to app.py before building)
  - See `templates/README_ADMIN.md` for sync instructions

### Build & Deploy
- `./build.sh`: Builds both Docker images
- `./run.sh`: Starts landing page + nginx with SSL
- Sessions auto-created when users visit landing page

## Data Flow

1. **Session Creation**: Landing page spawns new session container
2. **Question Setup**: Admin optionally sets questions (or uses default)
3. **Recording**: Participant records voice → Whisper transcribes
4. **Submission**: Frontend sends `{items: [{question, answer}]}` to `/api/submit-feedback`
5. **Storage**: Added to `session_data.feedback` array (in-memory)
6. **Closure**: Admin calls `/api/close-collection`
7. **Analysis**: Admin calls `/api/generate-report` → Claude analyzes
8. **Report**: Stored in `session_data.generated_report`
9. **Cleanup**: Container stops → all data destroyed (privacy!)

## Testing

```bash
# Run test suite
uv run pytest event_server/tests/ -v

# End-to-end test
./test_full_flow.sh

# Manual report test (requires ANTHROPIC_API_KEY)
python test_report.py
```

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `ANTHROPIC_API_KEY` | Yes (for AI) | Claude API access for report generation |
| `SESSION_ID` | No | Custom session ID (auto-generated if not set) |
| `PORT` | No | Server port (default: 5000) |

## Notes

- **Session state**: In-memory via `SessionData` dataclass (no database)
- **Privacy**: Data is ephemeral and never persisted to disk
- **Worker count**: Use `-w 1` for now (in-memory state not shared)
- **Admin HTML**: Embedded as string in `app.py`, not served from templates
  - To update: edit `admin.html.source` → sync to `app.py` → rebuild
  - Sync script in `templates/README_ADMIN.md`
- **Default question**: "Please share your general reflections"
- **LLM Model**: Claude 3.5 Haiku (fast, cost-effective)

## Future Improvements

- [ ] Shared state backend (Redis/database) for multi-worker support
- [ ] Admin UI for viewing generated reports
- [ ] Streaming LLM responses
- [ ] Custom report prompts
- [ ] Export feedback as JSON
- [ ] Session recording/replay

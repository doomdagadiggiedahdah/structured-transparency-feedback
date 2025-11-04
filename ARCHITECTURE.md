# Structured Transparency - Architecture Overview

## Directory Structure

```
structured-transparency/
├── event_server/          # Session container code
│   ├── app.py            # Flask app with embedded admin HTML
│   ├── routes.py         # API routes (unused, logic in app.py)
│   ├── static/           # worker.js for transcription
│   └── templates/        # participant.html, admin.html.source
│
├── landing_page/         # Landing page / session orchestrator
│   ├── app.py           # Flask app, creates session containers
│   ├── routes.py        # Routes (unused, logic in app.py)
│   ├── static/          # CSS, assets
│   └── templates/       # Landing page HTML
│
├── Dockerfile.event     # Builds session-server image
├── Dockerfile.landing   # Builds landing-page image
├── build.sh            # Builds both images
└── run.sh              # Starts landing + nginx with SSL
```

## Docker Architecture

### Images

| Image | Built From | Purpose |
|-------|-----------|---------|
| **session-server** | `Dockerfile.event` | Serves participant & admin pages for each session |
| **landing-page** | `Dockerfile.landing` | Landing page + orchestrates session containers |
| **nginx:alpine** | Official image | SSL reverse proxy |

### Running Containers

| Container | Image | Ports | Purpose |
|-----------|-------|-------|---------|
| **landing** | landing-page | 5000 | Landing page, creates session containers via Docker socket |
| **session-XXXXXX** | session-server | 8000-9000 | Individual session (created dynamically per user) |
| **nginx-ssl** | nginx:alpine | 80, 443 | HTTPS termination, proxies to landing + sessions |

## Request Flow

```
User → HTTPS (443) → nginx-ssl → Landing page (5000)
                                ↓
                         Creates session container
                                ↓
User → HTTPS (443) → nginx-ssl → Session (800X) → Participant/Admin pages
```

## Key Components

### Landing Page (`landing_page/`)
- Creates QR codes
- Spawns session containers dynamically
- Mounts `/var/run/docker.sock` to control Docker

### Session Server (`event_server/`)
- **Participant page** (`templates/participant.html`): Audio recording + transcription
- **Admin page** (embedded in `app.py` line 18): Question management, view responses
  - Source: `templates/admin.html.source` (sync to app.py before building)
- **Transcription**: Web Worker (`static/worker.js`) with local ML model

### Build & Deploy
- `./build.sh`: Builds both Docker images
- `./run.sh`: Starts landing page + nginx with SSL
- Sessions auto-created when users visit landing page

## Notes
- Admin HTML is **embedded as string in `app.py`**, not served from templates
- To update admin: edit `admin.html.source` → sync to `app.py` → rebuild
- Default question: "Please share your general reflections"

# Publish to Quartz Feature

## Overview
Added functionality to automatically publish generated LLM reports from event sessions to the Quartz static site repository.

## What Was Added

### 1. Backend API Endpoint
**File**: `event_server/app.py`

Added `/api/publish-to-quartz` POST endpoint that:
- Takes the generated report from session memory
- Creates a timestamped markdown file (e.g., `report_2025-11-06_05-27-00.md`)
- Saves it to `/home/ubuntu/quartz/content/`
- Commits and pushes to the quartz Git repository

### 2. Frontend UI
**File**: `event_server/templates/admin.html.source`

Added:
- "📤 Publish to Quartz" button below the AI report section
- Status display showing success/error messages
- JavaScript function `publishToQuartz()` to handle the button click

### 3. Docker Configuration

#### Session Container Setup
**File**: `landing_page/app.py`

Added volume mounts when creating session containers:
```python
volumes={
    '/home/ubuntu/quartz': {'bind': '/home/ubuntu/quartz', 'mode': 'rw'},
    '/home/ubuntu/.ssh': {'bind': '/root/.ssh', 'mode': 'ro'}
}
```

This gives containers access to:
- The quartz repository (read/write)
- SSH keys for GitHub authentication (read-only)

#### Session Server Image
**File**: `Dockerfile.event`

Added:
- Git installation: `apt-get install -y git`
- Git safe directory config: `git config --global --add safe.directory /home/ubuntu/quartz`
- Git user identity:
  - Name: "Structured Transparency"
  - Email: "report@struct.lol"

### 4. QR Code Fix
**File**: `event_server/templates/admin.html.source`

Fixed CORS issue with QR code generation by:
- Adding back missing script tags for `qrcodejs` and `marked.js`
- Switching from external API (`api.qrserver.com`) to client-side `QRCode.js` library
- Changed QR container from `<img>` to `<div>` element

## How It Works

1. User generates a report in an event session
2. User clicks "📤 Publish to Quartz" button
3. Backend endpoint:
   - Writes report as markdown file to `quartz/content/`
   - Runs `git add <file>`
   - Runs `git commit -m "publish(report): <filename>"`
   - Runs `git push` (authenticates using mounted SSH keys)
4. Success message shows the published file path

## Files Modified

- `event_server/app.py` - Added publish endpoint
- `event_server/templates/admin.html.source` - Added button and JS function
- `landing_page/app.py` - Added volume mounts for quartz + SSH keys
- `Dockerfile.event` - Added git and git configuration
- `README.md` - Updated (optional)

## Git Commit Details

Commits are made by:
- **Author**: Structured Transparency <report@struct.lol>
- **Message Format**: `publish(report): report_YYYY-MM-DD_HH-MM-SS.md`

## Testing

1. Create a new event session
2. Add questions and collect feedback
3. Click "Close & Generate Report"
4. Once report appears, click "📤 Publish to Quartz"
5. Check `/home/ubuntu/quartz/content/` for the new markdown file
6. Verify the commit was pushed to GitHub

## Notes

- Only **new sessions** created after the changes will have publish functionality
- Old sessions running before volume mounts were added won't have access to quartz
- SSH keys are mounted read-only for security
- Reports are saved with UTC timestamp in filename

## Troubleshooting

**Error: "Quartz repository not found"**
- Session was created before volume mount was added
- Solution: Create a new session

**Error: "No report generated yet"**
- Generate a report first using "Close & Generate Report"

**Error: "Git operation failed"**
- Check that `/home/ubuntu/quartz` is a valid git repository
- Verify SSH keys are present in `/home/ubuntu/.ssh/`
- Ensure git user is configured in the container

## Future Improvements

- Add option to customize commit message
- Support for batch publishing multiple reports
- UI indicator showing publish history
- Automatic republish on report regeneration

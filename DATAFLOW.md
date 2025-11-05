# Data Flow Documentation

## Overview
This document describes the data structures, lifecycle, and flow of information in the Structured Transparency platform.

## SessionData

### What is SessionData?
`SessionData` is an **ephemeral in-memory data structure** that lives only as long as its container is running. When a session container stops, all data is lost. This is intentional—sessions are meant to be temporary, focused events.

### Structure
Located in `event_server/models.py`, `SessionData` is a Python dataclass with the following fields:

| Field | Type | Description | When Populated |
|-------|------|-------------|----------------|
| `session_id` | `str` | Unique identifier for the session | On initialization (from `SESSION_ID` env var or auto-generated) |
| `questions` | `list[str]` | List of questions for participants to answer | Set by admin via `/api/questions` |
| `is_collecting` | `bool` | Whether new feedback is being accepted | Defaults to `True`, set to `False` via `/api/close-collection` |
| `expire_time` | `datetime \| None` | When the session should expire | Set by admin via `/api/expire-time` |
| `feedback` | `list[dict]` | Array of participant responses | Populated as participants submit via `/api/submit-feedback` |
| `generated_report` | `str \| None` | LLM-generated summary of feedback | Created when admin triggers `/api/generate-report` |

### Feedback Item Structure
Each item in the `feedback` list has:
```python
{
    "question": str,    # The question that was answered
    "answer": str,      # The participant's answer
    "timestamp": str    # ISO format timestamp
}
```

## Data Lifecycle

```
Container Start
    ↓
SessionData initialized (session_id set)
    ↓
Admin sets questions → session_data.questions populated
    ↓
Participants submit responses → session_data.feedback grows
    ↓
Admin generates report → session_data.generated_report created
    ↓
Container Stop → All data destroyed
```

## API Endpoints and Data Flow

### Admin Endpoints

#### `POST /api/questions`
- **Updates**: `session_data.questions`
- **Input**: `{"questions": ["Q1", "Q2", ...]}`
- **Purpose**: Set the questions participants will answer

#### `POST /api/expire-time`
- **Updates**: `session_data.expire_time`
- **Input**: `{"minutes": 30}`
- **Purpose**: Set when session should expire

#### `POST /api/close-collection`
- **Updates**: `session_data.is_collecting` → `False`
- **Purpose**: Stop accepting new participant feedback

#### `POST /api/generate-report`
- **Reads**: `session_data.feedback`
- **Updates**: `session_data.generated_report`
- **Purpose**: Generate LLM summary of all feedback
- **Requires**: `ANTHROPIC_API_KEY` environment variable

### Participant Endpoints

#### `POST /api/submit-feedback`
- **Updates**: `session_data.feedback` (appends new items)
- **Input**: `{"answers": ["A1", "A2", ...]}`
- **Purpose**: Submit answers to session questions
- **Blocked if**: `session_data.is_collecting == False`

### Query Endpoints

#### `GET /api/state`
- **Returns**: Full `session_data.to_dict()` representation
- **Purpose**: Get current state of session (for admin dashboard)

## LLM Integration

### Module: `event_server/llm.py`

The `generate_report()` function:
1. Takes `session_data.feedback` as input
2. Formats feedback into a structured prompt
3. Calls Anthropic's Claude 3.5 Haiku model
4. Returns generated report text

**Environment Variables Required**:
- `ANTHROPIC_API_KEY`: Your Anthropic API key

**Model Used**: `claude-3-5-haiku-20241022`

## Data Persistence

### Current: Ephemeral (In-Memory Only)
- Data lives in Python process memory
- No disk writes, no database
- Container restart = complete data loss
- **This is intentional** for privacy and simplicity

### Future: Optional Export
Consider adding:
- Admin export button → downloads `participant_feedback.json`
- For debugging/analysis only
- Still ephemeral—export is manual, not automatic

## Testing

Sample data available in `event_server/tests/test_sample_data.py`:
- `SAMPLE_FEEDBACK`: Realistic feedback examples for testing

Test coverage:
- `test_models.py`: SessionData behavior
- `test_llm.py`: LLM integration (mocked)

Run tests with:
```bash
uv run pytest event_server/tests/
```

## Security Notes

1. **No PII Storage**: Data is ephemeral and never written to disk
2. **API Key Security**: Never expose `ANTHROPIC_API_KEY` in logs or responses
3. **Session Isolation**: Each container has its own isolated `SessionData`
4. **No Authentication**: Consider adding auth for admin endpoints in production

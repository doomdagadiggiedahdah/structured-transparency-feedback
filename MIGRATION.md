# Migration from Old Structure to Idiomatic Python

## Changes Made

### 1. Project Structure
- **Before**: Flat structure with hyphenated filenames
  - `event_server/event-server.py`
  - `landing_page/dispatch_landing.py`
  
- **After**: Proper Python package structure
  - `structured-transparency/` (project root)
  - Proper `__init__.py` files
  - Snake_case module names
  - Separate `app.py`, `routes.py`, `models.py` modules

### 2. Dependency Management
- **Added**: `pyproject.toml` with proper dependency specification
- **Added**: `.gitignore` for Python projects
- Compatible with `uv` (user preference)

### 3. Flask Application Pattern
- **Before**: Single-file apps with inline HTML
- **After**: 
  - Flask factory pattern (`create_app()`)
  - Blueprint-based routing
  - HTML templates in separate `templates/` directories
  - Proper data classes in `models.py`

### 4. Code Quality Improvements
- Type hints (Python 3.11+ syntax with `|` for unions)
- Proper docstrings
- Dataclasses instead of dictionaries
- Separation of concerns (routes, models, app config)

### 5. Docker Configuration
- Updated Dockerfiles to use new package structure
- Proper COPY patterns
- Reference correct module paths for gunicorn

## Key Improvements

1. **Maintainability**: Modular structure makes code easier to update
2. **Testability**: Separated concerns allow unit testing
3. **Scalability**: Factory pattern supports multiple app instances
4. **Standards**: Follows PEP 8 and Python packaging best practices
5. **Type Safety**: Type hints enable better IDE support and error detection

## Migration Steps

To use the new structure:

```bash
cd structured-transparency

# Set up environment
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run services
python -m event_server.app  # or
python -m landing_page.app
```

The old directories (`event_server/` and `landing_page/` in parent) can be removed once verified.

# Development Guides

This section contains guides for developers working on VoxRay AI.

## Contents

- [Development Guide](development/README.md) — Local development setup and workflow

## Quick Reference

### Running the Application

```bash
# Backend (from project root)
uvicorn backend.api.main:app --reload --port 8000

# Frontend (from frontend/ directory)
npm run dev
```

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Backend unit tests
python -m pytest backend/tests/ -v

# Pipeline tests
python -m pytest pipeline/tests/ -v
```

### Feature Flags

V2 features are controlled via environment variables. Set in `backend/.env`:

```env
FF_ENSEMBLE_MODEL=true
FF_DICOM_SUPPORT=true
FF_MEDICAL_VOCABULARY=true
```

See [Environment Variables Reference](../reference/environment-variables.md) for the complete list.

### API Documentation

The FastAPI auto-generated docs are available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

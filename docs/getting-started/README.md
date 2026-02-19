# Getting Started

Welcome to VoxRay AI. This section guides you through setting up and running the application.

## Contents

- [Quick Start](quick-start.md) — Get running in under 10 minutes
- [Installation](installation.md) — Complete installation guide
- [Prerequisites](prerequisites.md) — System requirements and dependencies
- [Configuration](configuration.md) — Environment variables and settings

## Overview

VoxRay AI requires two services to run:

1. **Backend** — Python FastAPI server handling AI inference (port 8000)
2. **Frontend** — React/Vite application providing the medical console UI (port 5173)

Both services must be running simultaneously for full functionality.

## Quick Reference

```bash
# Backend
uvicorn backend.api.main:app --reload

# Frontend
cd frontend && npm run dev
```

See [Quick Start](quick-start.md) for the complete setup walkthrough.

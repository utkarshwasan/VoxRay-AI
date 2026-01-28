# Configuration

VoxRay AI is configured via environment variables.

## Backend Configuration

File: `backend/.env`

| Variable                  | Required | Description               | Example                   |
| ------------------------- | :------: | ------------------------- | ------------------------- |
| `OPENROUTER_API_KEY`      |   Yes    | API Key for LLM access    | `sk-or-v1-...`            |
| `STACK_PROJECT_ID`        |   Yes    | Stack Auth Project ID     | `a1b2-c3d4...`            |
| `STACK_SECRET_SERVER_KEY` |   Yes    | Secret key for validation | `server-secret...`        |
| `TTS_VOICE`               |    No    | Edge-TTS Voice ID         | `en-US-ChristopherNeural` |

## Frontend Configuration

File: `frontend/.env`

| Variable                            | Required | Description             | Example         |
| ----------------------------------- | :------: | ----------------------- | --------------- |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` |   Yes    | Public key for Login UI | `client-key...` |
| `VITE_STACK_PROJECT_ID`             |   Yes    | Must match backend ID   | `a1b2-c3d4...`  |

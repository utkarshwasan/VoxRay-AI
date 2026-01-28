# Environment Variables Reference

## Backend (`backend/.env`)

| Variable                  | Description                      | Required | Default                   |
| ------------------------- | -------------------------------- | -------- | ------------------------- |
| `OPENROUTER_API_KEY`      | API Key for OpenRouter (Gemini). | Yes      | -                         |
| `STACK_PROJECT_ID`        | Stack Auth Project ID.           | Yes      | -                         |
| `STACK_SECRET_SERVER_KEY` | Stack Auth Server Secret.        | Yes      | -                         |
| `TTS_VOICE`               | Edge-TTS Voice ID.               | No       | `en-US-ChristopherNeural` |

## Frontend (`frontend/.env`)

| Variable                            | Description            | Required | Default |
| ----------------------------------- | ---------------------- | -------- | ------- |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` | Stack Auth Client Key. | Yes      | -       |
| `VITE_STACK_PROJECT_ID`             | Stack Auth Project ID. | Yes      | -       |

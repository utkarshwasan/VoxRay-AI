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

### Feature Flags (V2)

All feature flags default to `false`. Set to `true` to enable:

| Variable                        | Description                      |
| ------------------------------- | -------------------------------- |
| `FF_ENSEMBLE_MODEL`             | Multi-model ensemble predictions |
| `FF_DICOM_SUPPORT`              | DICOM file handling              |
| `FF_MEDICAL_VOCABULARY`         | Medical term correction in STT   |
| `FF_WAKE_WORD_DETECTION`        | Wake word detection              |
| `FF_AUDIT_LOGGING`              | HIPAA-compliant audit trail      |
| `FF_DATA_ANONYMIZATION`         | Patient data anonymization       |
| `FF_UNCERTAINTY_QUANTIFICATION` | Prediction uncertainty scoring   |
| `FF_FHIR_INTEGRATION`           | FHIR R4 interoperability         |

See [Environment Variables Reference](../reference/environment-variables.md) for the complete list.

## Frontend Configuration

File: `frontend/.env`

| Variable                            | Required | Description             | Example         |
| ----------------------------------- | :------: | ----------------------- | --------------- |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` |   Yes    | Public key for Login UI | `client-key...` |
| `VITE_STACK_PROJECT_ID`             |   Yes    | Must match backend ID   | `a1b2-c3d4...`  |

# Reference

This section contains configuration reference documentation for VoxRay AI.

## Contents

- [Environment Variables](environment-variables.md) — All environment variables including feature flags

## Quick Reference

### Required Variables

| Variable                            | Service  | Description                           |
| ----------------------------------- | -------- | ------------------------------------- |
| `OPENROUTER_API_KEY`                | Backend  | API key for Gemini 2.0 via OpenRouter |
| `STACK_PROJECT_ID`                  | Backend  | Stack Auth project identifier         |
| `STACK_SECRET_SERVER_KEY`           | Backend  | Stack Auth server secret              |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` | Frontend | Stack Auth client key                 |
| `VITE_STACK_PROJECT_ID`             | Frontend | Stack Auth project ID (frontend)      |

### Feature Flag Variables (V2)

All feature flags default to `false`. Set to `true` to enable:

| Variable                | Feature                          |
| ----------------------- | -------------------------------- |
| `FF_ENSEMBLE_MODEL`     | Multi-model ensemble predictions |
| `FF_DICOM_SUPPORT`      | DICOM file handling              |
| `FF_MEDICAL_VOCABULARY` | Medical term correction          |
| `FF_AUDIT_LOGGING`      | HIPAA audit trail                |

See [Environment Variables](environment-variables.md) for the complete reference.

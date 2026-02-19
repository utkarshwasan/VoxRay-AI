# Environment Variables Reference

## Backend (`backend/.env`)

| Variable                  | Description                                    | Required | Default                   |
| ------------------------- | ---------------------------------------------- | -------- | ------------------------- |
| `OPENROUTER_API_KEY`      | API Key for OpenRouter (Gemini 2.0 Flash).     | Yes      | -                         |
| `STACK_PROJECT_ID`        | Stack Auth Project ID.                         | Yes      | -                         |
| `STACK_SECRET_SERVER_KEY` | Stack Auth Server Secret for JWT verification. | Yes      | -                         |
| `TTS_VOICE`               | Edge-TTS Voice ID for default English TTS.     | No       | `en-US-ChristopherNeural` |
| `HF_TOKEN`                | HuggingFace token for private model download.  | No       | -                         |
| `FRONTEND_URL`            | Frontend origin URL for CORS allowlist.        | No       | -                         |

## Frontend (`frontend/.env`)

| Variable                            | Description                              | Required | Default                 |
| ----------------------------------- | ---------------------------------------- | -------- | ----------------------- |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` | Stack Auth Client Key for frontend auth. | Yes      | -                       |
| `VITE_STACK_PROJECT_ID`             | Stack Auth Project ID (frontend).        | Yes      | -                       |
| `VITE_API_BASE_URL`                 | Backend API base URL.                    | No       | `http://localhost:8000` |

## V2 Feature Flags (`backend/.env`)

All feature flags default to `false`. Set to `true` to enable the corresponding v2 feature.

### ML Core

| Variable                        | Description                                        | Default |
| ------------------------------- | -------------------------------------------------- | ------- |
| `FF_ENSEMBLE_MODEL`             | Enable multi-model ensemble predictions.           | `false` |
| `FF_UNCERTAINTY_QUANTIFICATION` | Enable MC Dropout uncertainty estimation.          | `false` |
| `FF_CROSS_VALIDATION`           | Enable cross-validation during inference.          | `false` |
| `FF_BENCHMARKING`               | Enable clinical benchmark comparison in responses. | `false` |

### Clinical

| Variable                | Description                                    | Default |
| ----------------------- | ---------------------------------------------- | ------- |
| `FF_DICOM_SUPPORT`      | Enable DICOM file upload and processing.       | `false` |
| `FF_FHIR_INTEGRATION`   | Enable FHIR R4 resource generation.            | `false` |
| `FF_AUDIT_LOGGING`      | Enable HIPAA-compliant audit trail logging.    | `false` |
| `FF_DATA_ANONYMIZATION` | Enable automatic DICOM metadata anonymization. | `false` |

### Voice

| Variable                 | Description                                        | Default |
| ------------------------ | -------------------------------------------------- | ------- |
| `FF_WAKE_WORD_DETECTION` | Enable wake word detection endpoint.               | `false` |
| `FF_MULTILINGUAL_VOICE`  | Enable multilingual TTS/STT support.               | `false` |
| `FF_MEDICAL_VOCABULARY`  | Enable medical term correction for transcriptions. | `false` |
| `FF_NOISE_HANDLING`      | Enable audio noise reduction preprocessing.        | `false` |

### Frontend / UX

| Variable                 | Description                                     | Default |
| ------------------------ | ----------------------------------------------- | ------- |
| `FF_ADVANCED_HEATMAP`    | Enable advanced Grad-CAM heatmap visualization. | `false` |
| `FF_WORKLIST_MANAGEMENT` | Enable radiology worklist management features.  | `false` |
| `FF_BATCH_PROCESSING`    | Enable batch image processing.                  | `false` |
| `FF_MOBILE_PWA`          | Enable Progressive Web App features.            | `false` |

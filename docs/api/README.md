# API Documentation

## Overview

The VoxRay API is built with FastAPI. It handles multimodal inputs (Images, Audio, Text) and returns JSON structure responses.

## Base URL

```
http://localhost:8000
```

## Authentication

Protected endpoints require the **Stack Auth** Access Token.

```bash
curl -H "x-stack-access-token: YOUR_JWT_TOKEN" ...
```

## API Versions

- **v1**: Stable production endpoints (backward compatible)
- **v2**: Enhanced endpoints with feature flag gating

## Endpoints Summary

### V1 Endpoints (Stable, Backward Compatible)

| Method | Endpoint             | Description                  | Auth Required |
| ------ | -------------------- | ---------------------------- | ------------- |
| GET    | `/health`            | Health check                 | No            |
| GET    | `/metrics`           | Prometheus metrics           | No            |
| GET    | `/api/feature-flags` | Feature flag status          | No            |
| POST   | `/predict/image`     | Classify X-Ray abnormalities | Yes           |
| POST   | `/predict/explain`   | Generate Grad-CAM heatmap    | Yes           |
| POST   | `/transcribe/audio`  | Speech-to-Text (Whisper)     | Yes           |
| POST   | `/generate/speech`   | Text-to-Speech (Edge-TTS)    | No            |
| POST   | `/chat`              | Medical LLM Chat             | Yes           |

### V1 Aliases (Explicit Versioned Paths)

| Method | Endpoint               | Description                   |
| ------ | ---------------------- | ----------------------------- |
| POST   | `/v1/predict/image`    | Alias for `/predict/image`    |
| POST   | `/v1/transcribe/audio` | Alias for `/transcribe/audio` |
| POST   | `/v1/generate/speech`  | Alias for `/generate/speech`  |
| POST   | `/v1/chat`             | Alias for `/chat`             |
| GET    | `/v1/health`           | Alias for `/health`           |

### V2 Endpoints (Enhanced, Feature-Flag Gated)

| Method | Endpoint                          | Description                                   | Feature Flag Required         |
| ------ | --------------------------------- | --------------------------------------------- | ----------------------------- |
| GET    | `/v2/health`                      | V2 health check with feature flag status      | None                          |
| POST   | `/v2/chat`                        | Enhanced chat with multilingual support       | None                          |
| POST   | `/v2/predict/image`               | Ensemble prediction with uncertainty          | `FF_ENSEMBLE_MODEL=true`      |
| POST   | `/v2/predict/dicom`               | DICOM file prediction with anonymization      | `FF_DICOM_SUPPORT=true`       |
| POST   | `/v2/voice/enhance-transcription` | Medical vocabulary correction for transcripts | `FF_MEDICAL_VOCABULARY=true`  |
| POST   | `/v2/voice/wake-word-detect`      | Wake word detection in audio (stub)           | `FF_WAKE_WORD_DETECTION=true` |

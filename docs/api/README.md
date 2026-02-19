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

| Method | Endpoint               | Description                  | Version |
| ------ | ---------------------- | ---------------------------- | ------- |
| GET    | `/health`              | Health check                 | v1      |
| GET    | `/metrics`             | Prometheus metrics           | v1      |
| GET    | `/api/feature-flags`   | Feature flag status          | v1      |
| POST   | `/predict/image`       | Classify X-Ray abnormalities | v1/v2   |
| POST   | `/predict/explain`     | Generate Grad-CAM heatmap    | v1/v2   |
| POST   | `/transcribe/audio`    | Speech-to-Text (Whisper)     | v1/v2   |
| POST   | `/generate/speech`     | Text-to-Speech (Edge-TTS)    | v1/v2   |
| POST   | `/chat`                | Medical LLM Chat             | v1/v2   |
| POST   | `/v2/chat`             | Enhanced chat with language  | v2      |
| POST   | `/v2/predict`          | Enhanced prediction          | v2      |
| POST   | `/v2/voice/stt`        | Enhanced STT                 | v2      |
| POST   | `/v2/voice/tts`        | Enhanced TTS                 | v2      |
| GET    | `/v2/clinical/context` | Clinical context             | v2      |

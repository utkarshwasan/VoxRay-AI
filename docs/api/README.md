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

## Endpoints Summary

| Method | Endpoint            | Description                  |
| ------ | ------------------- | ---------------------------- |
| POST   | `/predict/image`    | Classify X-Ray abnormalities |
| POST   | `/predict/explain`  | Generate Grad-CAM heatmap    |
| POST   | `/transcribe/audio` | Speech-to-Text (Whisper)     |
| POST   | `/generate/speech`  | Text-to-Speech (Edge-TTS)    |
| POST   | `/chat`             | Medical LLM Chat             |

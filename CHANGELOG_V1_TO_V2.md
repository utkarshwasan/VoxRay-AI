# VoxRay AI — v1 to v2 Changelog

**Version:** 2.0.0  
**Release Date:** 2026-02-19

---

## Overview

VoxRay AI v2 is a production-hardened release of the intelligent radiology assistant. It introduces a versioned API architecture, feature-flag-gated v2 enhancements, multilingual support, and a complete clinical integration layer — while maintaining full backward compatibility with all v1 endpoints.

---

## Breaking Changes

### API Deprecation Date Updated

The `x-api-deprecation-date` response header on all `/v1/*` endpoints has been updated from `2025-12-31` to `2026-12-31`. Any monitoring system or client that parses this header must be updated.

### `/metrics` Version Field

The Prometheus metrics endpoint now reports `voxray_info{version="2.0.0"}`. Previously reported `1.0.0`. Update any Grafana dashboards or alerting rules that filter on this value.

---

## New Features

### V2 API Layer

A complete `/v2/*` API layer has been added alongside the existing v1 endpoints. All v2 endpoints are gated behind feature flags (`FF_*` environment variables) and default to disabled.

| Endpoint                               | Feature Flag             | Description                                         |
| -------------------------------------- | ------------------------ | --------------------------------------------------- |
| `GET /v2/health`                       | None                     | Enhanced health check with feature flag status      |
| `POST /v2/chat`                        | None                     | Multilingual chat with language enforcement         |
| `POST /v2/predict/image`               | `FF_ENSEMBLE_MODEL`      | Ensemble prediction with uncertainty quantification |
| `POST /v2/predict/dicom`               | `FF_DICOM_SUPPORT`       | DICOM file prediction with anonymization            |
| `POST /v2/voice/enhance-transcription` | `FF_MEDICAL_VOCABULARY`  | Medical vocabulary correction                       |
| `POST /v2/voice/wake-word-detect`      | `FF_WAKE_WORD_DETECTION` | Wake word detection                                 |

### Feature Flag System (16 Flags)

All v2 features are controlled via `FF_*` environment variables. Default is `false` for all flags. See `docs/reference/environment-variables.md` for the complete list.

### Multilingual Support

6 languages are now active: English (`en`), Spanish (`es`), French (`fr`), German (`de`), Chinese (`zh`). Hindi is disabled due to a whisper-base STT limitation (phonetically identical to Urdu at the base model level).

Language enforcement in chat uses a two-message injection pattern to ensure the LLM responds in the requested language regardless of conversation history momentum.

### API Versioning with Deprecation Headers

All `/v1/*` endpoints now return:

- `x-api-version: 1.0`
- `x-api-deprecation-date: 2026-12-31`
- `warning: 299 - 'V1 API is deprecated. Please migrate to /v2 endpoints.'`

All `/v2/*` endpoints return `x-api-version: 2.0`.

### Prometheus Metrics Endpoint

`GET /metrics` returns Prometheus-compatible text format including feature flag status and model load status.

### Feature Flags API Endpoint

`GET /api/feature-flags` returns the current state of all feature flags, merging the real `FF_*` environment variables with frontend-specific defaults.

### DICOM Support (v2, gated)

`POST /v2/predict/dicom` accepts DICOM files, extracts the image, runs classification, and applies metadata anonymization when `FF_DATA_ANONYMIZATION=true`.

### Medical Vocabulary Correction (v2, gated)

`POST /v2/voice/enhance-transcription` corrects medical terminology in transcribed text (e.g., "ammonia" → "pneumonia") when `FF_MEDICAL_VOCABULARY=true`.

---

## Changes

### Application Startup Lifecycle

Replaced deprecated `@app.on_event("startup")` with FastAPI's `lifespan` context manager pattern. No behavioral change — models still load at startup.

### Chat Endpoint Language Enforcement

The v2 chat endpoint (`/v2/chat`) places the language instruction at the **top** of the system prompt (not the bottom) for maximum LLM compliance. A two-message injection pattern reinforces the language requirement after conversation history.

### Confidence Parser Guard

Added `.split()[0]` guard when parsing confidence values from context strings to prevent `ValueError` on trailing text.

### Class Names Loading

Removed duplicate fallback assignment in `load_class_names()`. Single assignment with single log message.

---

## Fixes

### API Documentation Accuracy

`docs/api/README.md` previously listed three v2 endpoints that did not exist in the codebase (`/v2/voice/stt`, `/v2/voice/tts`, `/v2/clinical/context`). These have been removed and replaced with the accurate endpoint list.

### Missing Documentation Files

Four files referenced in `docs/SUMMARY.md` did not exist. Created:

- `docs/getting-started/README.md`
- `docs/architecture/decisions/README.md`
- `docs/guides/README.md`
- `docs/reference/README.md`

### Environment Variable Documentation

`docs/reference/environment-variables.md` now documents all 16 `FF_*` feature flag variables. Previously only 7 variables were documented.

### Test Suite Reliability

- `tests/e2e_api_test.py`: Added server availability probe — e2e tests skip gracefully when no server is running instead of timing out
- `backend/tests/test_prediction.py`: Added TensorFlow availability guard — tests skip on environments where TF DLL loading fails
- `tests/test_multilingual_fix.py`: Fixed invalid escape sequence in docstring

---

## Removed

- All `Implementation_v2/` agent planning files (internal development artifacts)
- All `shared_context/` handoff files (internal development artifacts)
- Temporary test scripts from root directory (`test_flags.py`, `test_manual.py`, `test_multilingual_tts.py`, `test_regression.py`)
- Deployment documentation for platforms not used in production (`DEPLOYMENT.md`, `netlify.toml`)

---

## Dependencies

| Package          | Change | Reason                                                   |
| ---------------- | ------ | -------------------------------------------------------- |
| `pydicom>=2.4.0` | Added  | Required for DICOM file handling in v2 clinical endpoint |

All other dependencies unchanged.

---

## Test Results

```
python -m pytest tests/ backend/tests/ -v
28 passed, 22 skipped, 0 failed
```

Skipped tests are due to: missing test fixtures, TensorFlow DLL environment issues (passes in Docker), intentionally disabled Hindi tests, and e2e tests requiring a live server.

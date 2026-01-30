File 6: SHARED/03_API_CONTRACTS.md
Markdown

# VoxRay AI v2.0 - API Contracts

**Purpose:** Define all API endpoint contracts to ensure consistency across agents

---

## 🔌 API Contract Standards

### Response Format Standards

All API responses MUST follow these formats:

#### Success Response (2xx)

```json
{
  "success": true,
  "data": {
    // Actual response data
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601",
    "version": "v1 or v2"
  }
}
Error Response (4xx, 5xx)
JSON

{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}  // Optional
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO-8601"
  }
}
📍 V1 Endpoints (STABLE - DO NOT MODIFY)
POST /predict/image
Description: Predict diagnosis from X-ray image

Request:

http

POST /predict/image HTTP/1.1
Host: api.voxray.ai
Content-Type: multipart/form-data
x-stack-access-token: <JWT_TOKEN>

--boundary
Content-Disposition: form-data; name="image_file"; filename="xray.png"
Content-Type: image/png

<binary image data>
--boundary--
Response (200 OK):

JSON

{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.983
}
Error Responses:

401 Unauthorized - Missing or invalid auth token
400 Bad Request - Invalid image format
413 Payload Too Large - Image exceeds size limit
503 Service Unavailable - Model not loaded
Contract Rules:

❌ CANNOT add new fields to root level
❌ CANNOT change field names
❌ CANNOT change field types
✅ CAN add internal logging
✅ CAN optimize internal logic
POST /transcribe/audio
Description: Transcribe audio to text using Whisper

Request:

http

POST /transcribe/audio HTTP/1.1
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="audio_file"; filename="recording.wav"
Content-Type: audio/wav

<binary audio data>
--boundary--
Response (200 OK):

JSON

{
  "transcription": "What does this X-ray show?"
}
Error Responses:

400 Bad Request - Invalid audio format
413 Payload Too Large - Audio exceeds size limit
503 Service Unavailable - STT model not loaded
Contract Rules:

❌ CANNOT modify response structure
✅ CAN improve transcription accuracy (same structure)
POST /generate/speech
Description: Generate speech from text using Edge-TTS

Request:

http

POST /generate/speech HTTP/1.1
Content-Type: application/json

{
  "text": "The X-ray shows pneumonia"
}
Response (200 OK):

http

HTTP/1.1 200 OK
Content-Type: audio/mpeg
Transfer-Encoding: chunked

<streaming audio data>
Error Responses:

400 Bad Request - Missing text field
503 Service Unavailable - TTS service unavailable
Contract Rules:

❌ CANNOT change from streaming to non-streaming
❌ CANNOT change audio format
✅ CAN change voice (via env var)
POST /chat
Description: Chat with Gemini 2.0 Flash with medical context

Request:

http

POST /chat HTTP/1.1
Content-Type: application/json
x-stack-access-token: <JWT_TOKEN>

{
  "message": "What are the treatment options?",
  "context": "Diagnosis: PNEUMONIA, Confidence: 0.95",
  "history": [
    {"role": "user", "content": "What does this show?"},
    {"role": "assistant", "content": "This shows pneumonia"}
  ]
}
Response (200 OK):

JSON

{
  "response": "Treatment options include antibiotics..."
}
Error Responses:

401 Unauthorized - Missing or invalid auth token
400 Bad Request - Invalid request format
500 Internal Server Error - LLM API error
Contract Rules:

❌ CANNOT modify response structure
✅ CAN improve response quality (same structure)
📍 V2 Endpoints (NEW - Feature Gated)
POST /v2/predict/image
Description: Enhanced prediction with ensemble and uncertainty

Request:

http

POST /v2/predict/image HTTP/1.1
Content-Type: multipart/form-data
x-stack-access-token: <JWT_TOKEN>

--boundary
Content-Disposition: form-data; name="image_file"; filename="xray.png"
Content-Type: image/png

<binary image data>
--boundary--
Response (200 OK):

JSON

{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.983,
  "uncertainty": {
    "epistemic": 0.05,
    "aleatoric": 0.02,
    "total": 0.07,
    "should_review": false
  },
  "ensemble": {
    "voting_method": "soft",
    "models_used": ["ResNet50V2", "EfficientNetB3"],
    "individual_predictions": {
      "ResNet50V2": {
        "diagnosis": "06_PNEUMONIA",
        "confidence": 0.98
      },
      "EfficientNetB3": {
        "diagnosis": "06_PNEUMONIA",
        "confidence": 0.99
      }
    },
    "disagreement_score": 0.0
  },
  "meta": {
    "model_version": "ensemble_v1.0",
    "inference_time_ms": 450
  }
}
Feature Flags:

FF_ENSEMBLE_MODEL - Ensemble prediction
FF_UNCERTAINTY_QUANTIFICATION - Uncertainty metrics
Fallback: If flags disabled, returns v1 response structure

Owner: AG-01

POST /v2/predict/dicom
Description: Predict from DICOM file

Request:

http

POST /v2/predict/dicom HTTP/1.1
Content-Type: multipart/form-data
x-stack-access-token: <JWT_TOKEN>

--boundary
Content-Disposition: form-data; name="dicom_file"; filename="study.dcm"
Content-Type: application/dicom

<binary DICOM data>
--boundary--
Response (200 OK):

JSON

{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.983,
  "dicom_metadata": {
    "patient_id_hash": "abc123def456",
    "study_instance_uid": "1.2.840.113619...",
    "study_date": "20250131",
    "modality": "DX"
  },
  "image_extracted": true,
  "anonymization_applied": true
}
Feature Flags:

FF_DICOM_SUPPORT
Error Responses:

400 Bad Request - Invalid DICOM file
503 Service Unavailable - Feature not enabled
Owner: AG-03

GET /v2/fhir/diagnostic-report/{patient_id}
Description: Get FHIR-formatted diagnostic report

Request:

http

GET /v2/fhir/diagnostic-report/abc123 HTTP/1.1
x-stack-access-token: <JWT_TOKEN>
Response (200 OK):

JSON

{
  "resourceType": "DiagnosticReport",
  "id": "report-123",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "36643-5",
      "display": "XR Chest"
    }]
  },
  "subject": {
    "reference": "Patient/abc123"
  },
  "conclusion": "Findings consistent with pneumonia",
  "conclusionCode": [{
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "233604007",
      "display": "Pneumonia"
    }]
  }]
}
Feature Flags:

FF_FHIR_INTEGRATION
Owner: AG-03

POST /v2/voice/wake-word-detect
Description: Continuous wake word detection

Request:

http

POST /v2/voice/wake-word-detect HTTP/1.1
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="audio_stream"; filename="stream.wav"
Content-Type: audio/wav

<audio stream data>
--boundary--
Response (200 OK):

JSON

{
  "wake_word_detected": true,
  "confidence": 0.97,
  "timestamp_ms": 1234,
  "wake_word": "hey voxray"
}
Feature Flags:

FF_WAKE_WORD_DETECTION
Owner: AG-04

POST /v2/transcribe/audio
Description: Enhanced transcription with medical vocabulary

Request:

http

POST /v2/transcribe/audio HTTP/1.1
Content-Type: multipart/form-data

{
  "audio_file": <binary>,
  "language": "en",  // or "es"
  "medical_context": true
}
Response (200 OK):

JSON

{
  "transcription": "consolidation in the right lower lobe",
  "language_detected": "en",
  "medical_terms_recognized": [
    "consolidation",
    "right lower lobe"
  ],
  "confidence": 0.95
}
Feature Flags:

FF_MULTILINGUAL_VOICE
FF_MEDICAL_VOCABULARY
Owner: AG-04

🔧 Utility Endpoints
GET /health
Description: System health check

Request:

http

GET /health HTTP/1.1
Response (200 OK):

JSON

{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "medical_model": "loaded",
    "stt_model": "loaded",
    "tts_service": "connected",
    "llm_service": "connected"
  },
  "timestamp": "2025-01-31T12:00:00Z"
}
Response (503 Service Unavailable):

JSON

{
  "status": "unhealthy",
  "version": "2.0.0",
  "services": {
    "medical_model": "not_loaded",
    "stt_model": "loaded",
    "tts_service": "connected",
    "llm_service": "error"
  },
  "errors": ["Medical model failed to load"],
  "timestamp": "2025-01-31T12:00:00Z"
}
GET /metrics
Description: Prometheus metrics

Request:

http

GET /metrics HTTP/1.1
Response (200 OK):

text

# HELP inference_latency_seconds Inference latency in seconds
# TYPE inference_latency_seconds histogram
inference_latency_seconds_bucket{le="0.1"} 10
inference_latency_seconds_bucket{le="0.5"} 100
inference_latency_seconds_bucket{le="1.0"} 150
inference_latency_seconds_bucket{le="+Inf"} 200
inference_latency_seconds_sum 180.5
inference_latency_seconds_count 200

# HELP prediction_confidence Prediction confidence score
# TYPE prediction_confidence gauge
prediction_confidence 0.95

# HELP predictions_total Total number of predictions
# TYPE predictions_total counter
predictions_total{diagnosis="PNEUMONIA"} 50
predictions_total{diagnosis="NORMAL_LUNG"} 30
Owner: AG-05

GET /api/feature-flags
Description: Debug endpoint for feature flag status

Request:

http

GET /api/feature-flags HTTP/1.1
Response (200 OK):

JSON

{
  "flags": {
    "ensemble_model": true,
    "uncertainty_quantification": true,
    "dicom_support": false,
    "fhir_integration": false,
    "wake_word_detection": false,
    "multilingual_voice": false,
    "medical_vocabulary": false,
    "noise_handling": false,
    "advanced_heatmap": false,
    "worklist_management": false,
    "batch_processing": false,
    "mobile_pwa": false
  },
  "environment": "development"
}
Owner: AG-00

📜 API Versioning Rules
URL Structure
text

/                    → v1 (backward compatibility)
/v1/*                → Explicit v1
/v2/*                → New features
Version Migration Path
text

Client using root endpoints (/)
  → Works indefinitely (maps to v1)
  → No breaking changes ever

Client using /v1/* explicitly
  → Guaranteed stable
  → Deprecated features get warnings but still work

Client using /v2/*
  → New features available
  → Feature-gated (503 if disabled)
  → May evolve (but with versioning within v2)
🔐 Authentication Requirements
Endpoint	Auth Required	Auth Type
POST /predict/image	Yes	x-stack-access-token
POST /v2/predict/image	Yes	x-stack-access-token
POST /v2/predict/dicom	Yes	x-stack-access-token
POST /transcribe/audio	No	-
POST /generate/speech	No	-
POST /chat	Yes	x-stack-access-token
GET /health	No	-
GET /metrics	No	-
GET /api/feature-flags	No	-
Note: AG-03 may add more endpoints requiring auth for FHIR

🚦 HTTP Status Code Standards
Code	Usage	Example
200	Success	Prediction returned
201	Created	New resource created
204	No Content	Delete successful
400	Bad Request	Invalid image format
401	Unauthorized	Missing/invalid token
403	Forbidden	Insufficient permissions
404	Not Found	Resource not found
413	Payload Too Large	Image >10MB
422	Unprocessable Entity	Valid format, invalid data
429	Too Many Requests	Rate limit exceeded
500	Internal Server Error	Unexpected error
503	Service Unavailable	Model not loaded or feature disabled
📝 Contract Change Process
Adding New Endpoint
Propose: Add to "Breaking Changes Queue" in CTX_SYNC.md
Design: Document in this file
Review: Affected agents review
Approve: Human coordinator approves
Implement: Assigned agent implements
Test: Unit + integration tests
Document: Update this file and OpenAPI spec
Modifying Existing Endpoint (v2 only)
Assess Impact: Which clients will break?
Version: Create new version if breaking
Deprecate: Mark old version as deprecated
Migrate: Provide migration guide
Sunset: Remove after deprecation period
Modifying v1 Endpoint
NOT ALLOWED - Create v2 endpoint instead

🧪 Contract Testing
All agents MUST run these tests before marking API work complete:

Bash

# Backward compatibility (v1)
pytest tests/api/test_v1_contracts.py -v

# V2 contracts
pytest tests/api/test_v2_contracts.py -v

# Integration
pytest tests/integration/test_api_integration.py -v

# Contract validation
pytest tests/api/test_openapi_compliance.py -v
Last Updated: 2025-01-31
Maintained By: AG-06 (FullStackDeveloper), AG-00 (MigrationLead)
Review Frequency: Before implementing any new endpoint
```

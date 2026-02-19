# System Design

## API Versioning

VoxRay AI v2 introduces versioned APIs:

- **V1 Endpoints**: Stable, backward-compatible endpoints with deprecation headers
- **V2 Endpoints**: Enhanced endpoints with feature flag gating

All V1 endpoints return deprecation headers:

- `x-api-version: 1.0`
- `x-api-deprecation-date: 2026-12-31`

## Data Flow

### 1. Image Analysis Flow

1. **User** uploads X-Ray via Frontend.
2. Image is sent to `POST /predict/image` (v1) or `POST /v2/predict/image` (v2) as multipart/form-data.
3. **Backend** preprocesses image (resize to 224x224, normalize).
4. **ResNet50V2 Model** predicts class probabilities (Pneumonia, etc.).
5. **Grad-CAM module** uses gradients to generate heatmaps.
6. JSON response (Diagnosis + Confidence) returned to Frontend.

**V2 Enhancement:** When `FF_ENSEMBLE_MODEL=true`, multiple models vote and uncertainty is quantified.

### 2. Voice Command Flow

1. **User** presses "Hold to Speak".
2. Audio recorded in browser (Web Audio API).
3. Audio blob sent to `POST /transcribe/audio`.
4. **Whisper Model** converts Audio -> Text.
5. Frontend interprets text (e.g., "Analyze", "Explain").

**V2 Enhancement:** When `FF_MEDICAL_VOCABULARY=true`, transcriptions are corrected for medical terminology.

### 3. Conversational AI Flow

1. **User** asks "What does this mean?".
2. Frontend sends message + _Diagnosis Context_ to `POST /chat` (v1) or `POST /v2/chat` (v2).
3. **Backend** constructs prompt with System Instructions + Medical Guidelines.
4. Request forwarded to **OpenRouter (Gemini 2.0)**.
5. Response returned and read aloud via `POST /generate/speech`.

**V2 Enhancement:** Multilingual support with language enforcement for consistent responses.

### 4. DICOM Flow (V2)

1. **User** uploads DICOM file.
2. Request sent to `POST /v2/predict/dicom` (requires `FF_DICOM_SUPPORT=true`).
3. **Backend** extracts image from DICOM, optionally anonymizes metadata.
4. Standard image analysis pipeline follows.

## Database Schema

Currently, VoxRay AI is stateless for simplicity.

- **Micro-DB**: Use `consolidated_medical_data` for training files.
- **User Data**: Managed externally by Stack Auth.

## Security Design

- **Headers**: All protected endpoints require `x-stack-access-token`.
- **Validation**: Backend uses JWKS (JSON Web Key Sets) to verify signatures from Stack Auth.
- **CORS**: Restricted to allowed origins (localhost).
- **Audit Logging (V2)**: When `FF_AUDIT_LOGGING=true`, all operations are logged for HIPAA compliance.

File 4: SHARED/01_MUST_PRESERVE.md
Markdown

# VoxRay AI v2.0 - MUST PRESERVE (Critical System Components)

**⚠️ WARNING: DO NOT MODIFY THESE COMPONENTS WITHOUT EXPLICIT APPROVAL ⚠️**

**Read this BEFORE starting any work**

---

## 🔒 Zero-Tolerance Components

These components MUST remain 100% functional throughout all phases. Any modification requires:

1. Explicit approval from human coordinator
2. Backward compatibility guarantee
3. Rollback plan
4. 100% test coverage

---

## 1️⃣ Authentication System (Stack Auth)

### Frontend Files - DO NOT MODIFY

```yaml
files_to_preserve:
  - path: frontend/src/stack.js
    reason: Stack Auth client initialization
    modifications_allowed: NONE

  - path: frontend/src/components/OAuthCallbackHandler.jsx
    reason: OAuth redirect handling
    modifications_allowed: NONE

  - path: frontend/src/components/ProtectedRoute.jsx
    reason: Route protection logic
    modifications_allowed: NONE
Backend Files - DO NOT MODIFY
YAML

files_to_preserve:
  - path: backend/api/deps.py
    function: get_current_user()
    reason: JWKS token verification
    modifications_allowed: NONE
    current_behavior: |
      - Extracts x-stack-access-token from headers
      - Verifies JWT signature using JWKS
      - Returns decoded user object
      - Raises HTTPException(401) if invalid
Environment Variables - DO NOT REMOVE
Bash

# Frontend (.env)
VITE_STACK_PUBLISHABLE_CLIENT_KEY=xxx
VITE_STACK_PROJECT_ID=xxx

# Backend (.env)
STACK_PROJECT_ID=xxx
Auth Flow - MUST REMAIN IDENTICAL
text

User → Login Page
  → Stack Auth (OAuth)
  → Callback Handler (/auth/callback)
  → Get Access Token
  → Store in Cookie
  → Redirect to Dashboard

API Request:
  → Extract token from cookie
  → Add to x-stack-access-token header
  → Backend verifies via JWKS
  → Returns 401 if invalid
  → Returns 200 + data if valid
Test Command:

Bash

# This MUST pass after any changes
pytest tests/migration/test_backward_compatibility.py::TestStackAuthIntegration -v
2️⃣ API Endpoints (Existing v1)
Endpoints - EXACT RESPONSE STRUCTURE REQUIRED
POST /predict/image
Current Request:

Python

files = {"image_file": (filename, file_bytes, "image/png")}
headers = {"x-stack-access-token": token}
Current Response (MUST NOT CHANGE):

JSON

{
  "diagnosis": "06_PNEUMONIA",
  "confidence": 0.983
}
Forbidden Changes:

❌ Adding new fields to root level (use v2 endpoint)
❌ Changing field names
❌ Changing data types
❌ Removing fields
❌ Changing HTTP status codes for success (200)
Allowed:

✅ Internal optimization (as long as response unchanged)
✅ Logging additions
✅ Performance improvements
POST /transcribe/audio
Current Response (MUST NOT CHANGE):

JSON

{
  "transcription": "What does this X-ray show?"
}
POST /generate/speech
Current Behavior:

Accepts: {"text": "response text"}
Returns: StreamingResponse with audio/mpeg
MUST NOT change to non-streaming response
POST /chat
Current Response (MUST NOT CHANGE):

JSON

{
  "response": "The X-ray shows pneumonia..."
}
Test Command:

Bash

pytest tests/migration/test_backward_compatibility.py::TestV1PredictionEndpoint -v
pytest tests/migration/test_backward_compatibility.py::TestV1TranscriptionEndpoint -v
pytest tests/migration/test_backward_compatibility.py::TestV1ChatEndpoint -v
3️⃣ ML Models (Current Production)
ResNet50V2 Model - DO NOT MODIFY
YAML

model_file:
  path: backend/models/medical_model_final.keras
  size: ~212.73 MB
  architecture: ResNet50V2
  input_shape: (224, 224, 3)
  output_shape: (6,)
  classes:
    - 01_NORMAL_LUNG
    - 02_NORMAL_BONE
    - 03_NORMAL_PNEUMONIA
    - 04_LUNG_CANCER
    - 05_FRACTURED
    - 06_PNEUMONIA

  loading_code: |
    # DO NOT MODIFY THIS PATTERN
    model_path = BASE_DIR / "backend" / "models" / "medical_model_final.keras"
    medical_model = tf.keras.models.load_model(str(model_path))

  preprocessing: |
    # DO NOT MODIFY THIS PATTERN
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_arr = np.array(img).astype(np.float32)
    img_preprocessed = preprocess_input(img_arr)  # ResNet preprocess_input
    img_batch = np.expand_dims(img_preprocessed, 0)
Test Command:

Bash

pytest tests/migration/test_backward_compatibility.py::TestModelLoading -v
Whisper Model - DO NOT MODIFY LOADING
YAML

stt_model:
  name: openai/whisper-base
  loading_code: |
    # DO NOT MODIFY
    stt_processor = AutoProcessor.from_pretrained("openai/whisper-base")
    stt_model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-base").to(device)

  preprocessing: |
    # DO NOT MODIFY
    audio_data, sr = sf.read(io.BytesIO(audio_bytes))
    if sr != 16000:
        audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=16000)
    inputs = stt_processor(audio_data, sampling_rate=16000, return_tensors="pt")
Edge-TTS - DO NOT MODIFY
YAML

tts_engine:
  provider: Edge-TTS (cloud-based)
  voice: en-US-ChristopherNeural (from env: TTS_VOICE)
  usage: |
    # DO NOT MODIFY
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    async def audio_stream():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    return StreamingResponse(audio_stream(), media_type="audio/mpeg")
Gemini 2.0 Flash - DO NOT MODIFY
YAML

llm_integration:
  provider: OpenRouter
  model: google/gemini-2.0-flash-001
  base_url: https://openrouter.ai/api/v1
  env_var: OPENROUTER_API_KEY

  usage: |
    # DO NOT MODIFY
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    completion = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=messages,
        temperature=0.4
    )
4️⃣ Frontend Components (React 18)
Core Components - MUST RENDER WITHOUT ERRORS
YAML

components_to_preserve:
  - name: VoiceSection.jsx
    location: frontend/src/components/VoiceSection.jsx
    critical_features:
      - VAD (Voice Activity Detection) using RMS
      - SILENCE_THRESHOLD = 0.025
      - SILENCE_DURATION_MS = 1500
      - MediaRecorder with audio-recorder-polyfill
      - Sterile mode toggle
    modifications_allowed: "Enhancements only, must not break existing"

  - name: XRaySection.jsx
    location: frontend/src/components/XRaySection.jsx
    critical_features:
      - File upload (drag & drop + click)
      - Image preview
      - Prediction display
      - Error handling with Error Boundary
    modifications_allowed: "Enhancements only, must not break existing"

  - name: InteractiveXRayViewer.jsx
    location: frontend/src/components/InteractiveXRayViewer.jsx
    critical_features:
      - Pan/zoom with useSmoothPan/useSmoothZoom
      - Brightness/contrast controls
      - Heatmap overlay
    modifications_allowed: "Enhancements only, must not break existing"

  - name: ErrorBoundary.jsx
    location: frontend/src/components/ErrorBoundary.jsx
    critical_features:
      - Catches React render errors
      - Shows fallback UI
      - Prevents white screen (React #426 fix)
    modifications_allowed: NONE
React Patterns - MUST MAINTAIN
JavaScript

// startTransition usage (React #426 prevention)
// DO NOT REMOVE
startTransition(() => {
  setResult(data);
  setIsLoading(false);
});

// Suspense boundaries
// DO NOT REMOVE
<Suspense fallback={<Loader />}>
  <HeavyComponent />
</Suspense>

// Error boundaries
// DO NOT REMOVE
<ErrorBoundary>
  <Component />
</ErrorBoundary>
Test Command:

Bash

# Frontend tests
npm test -- --watchAll=false

# E2E test (when available)
playwright test tests/e2e/test_critical_workflows.spec.ts
5️⃣ Build & Deployment Configuration
Frontend (Vite + Netlify)
YAML

build_config:
  - file: frontend/vite.config.js
    critical_settings:
      - React plugin configuration
      - Resolve aliases (if any)
      - Build output directory
    modifications_allowed: "Optimization only"

  - file: frontend/package.json
    critical_fields:
      - "scripts.build": "vite build"
      - "scripts.dev": "vite"
      - React version: "^18.3.1"
      - Vite version: "^5.x"
    modifications_allowed: "Add only, do not change existing"

deployment:
  platform: Netlify
  url: https://taupe-baklava-2d4afd.netlify.app
  build_command: npm run build
  publish_directory: dist
  status: MUST REMAIN LIVE during migration
Backend (FastAPI + Hugging Face Spaces)
YAML

backend_config:
  - file: backend/api/main.py
    critical_code:
      - app = FastAPI(title="VoxRay AI API")
      - CORS configuration
      - @app.on_event("startup") for model loading
    modifications_allowed: "Add only, do not remove existing"

  - file: backend/requirements.txt
    critical_packages:
      - fastapi
      - uvicorn
      - tensorflow
      - torch
      - transformers
      - pydicom (if adding DICOM)
      - edge-tts
      - openai (for OpenRouter)
    modifications_allowed: "Add only, do not change versions of existing"

deployment:
  platform: Hugging Face Spaces
  status: MUST REMAIN LIVE during migration
  startup: Uvicorn on port 7860
6️⃣ Environment Variables
Frontend - DO NOT REMOVE
Bash

VITE_STACK_PUBLISHABLE_CLIENT_KEY=
VITE_STACK_PROJECT_ID=
VITE_API_BASE_URL=http://127.0.0.1:8000  # or production URL
Backend - DO NOT REMOVE
Bash

# Authentication
STACK_PROJECT_ID=

# AI Services
OPENROUTER_API_KEY=

# TTS
TTS_VOICE=en-US-ChristopherNeural

# Optional (but preserve if exists)
DEBUG=
LOG_LEVEL=
7️⃣ Critical User Flows
Flow 1: Login → Upload → Predict → View
YAML

flow:
  1_login:
    - User navigates to /login
    - Clicks Stack Auth login button
    - Redirects to Stack Auth
    - Returns to /auth/callback
    - Redirects to /dashboard
    status: MUST WORK

  2_upload:
    - User drags X-ray image to upload area
    - OR clicks upload area
    - Image preview appears
    - "Analyze" button enabled
    status: MUST WORK

  3_predict:
    - User clicks "Analyze"
    - Loading spinner appears
    - Request sent to POST /predict/image with auth token
    - Response received in <5 seconds
    status: MUST WORK

  4_view:
    - Diagnosis displayed (e.g., "PNEUMONIA")
    - Confidence displayed (e.g., "98.3%")
    - No React errors (white screen)
    - Error boundary NOT triggered
    status: MUST WORK
Flow 2: Voice Interaction
YAML

flow:
  1_record:
    - User clicks microphone button
    - Recording starts (red indicator)
    - VAD monitors silence
    - Recording stops after 1.5s silence (or manual stop)
    status: MUST WORK

  2_transcribe:
    - Audio sent to POST /transcribe/audio
    - Transcription appears in chat
    status: MUST WORK

  3_chat:
    - Transcription sent to POST /chat with context
    - AI response received
    - Response sent to POST /generate/speech
    - Audio plays automatically
    status: MUST WORK
Test Command:

Bash

# E2E test covering both flows
pytest tests/e2e/test_critical_workflows.py -v
🚨 Red Flags (Indicators of Breaking Changes)
If you see any of these, STOP and review:

Code Red Flags
❌ Modifying Stack Auth token verification logic
❌ Changing API endpoint URLs (except adding /v2)
❌ Changing response JSON structure for v1 endpoints
❌ Removing CORS middleware
❌ Changing model loading paths
❌ Modifying preprocessing functions for existing models
❌ Removing Error Boundary or Suspense
❌ Removing startTransition wrapper
Test Red Flags
❌ Backward compatibility tests failing
❌ E2E tests failing
❌ 401 errors appearing where they didn't before
❌ Model predictions returning different results
❌ Frontend white screen appearing
❌ API response time increasing >50%
Deployment Red Flags
❌ Netlify build failing
❌ Hugging Face Spaces failing to start
❌ Environment variables missing
❌ CORS errors in browser console
✅ How to Add New Features Safely
DO: Use Feature Flags
Python

# backend/api/main.py
from backend.core.feature_flags import require_feature, FeatureFlag

@app.post("/v2/predict/ensemble")  # New v2 endpoint
@require_feature(FeatureFlag.ENSEMBLE_MODEL)  # Feature flag
async def predict_ensemble(...):
    # New functionality
    pass
DO: Use API Versioning
Python

# Create new endpoint in backend/api/v2/__init__.py
# Leave backend/api/v1/__init__.py unchanged

# Root level endpoints (no version prefix) MUST map to v1
DO: Add Alongside, Not Replace
Python

# ✅ CORRECT: Add new model alongside existing
if feature_flags.is_enabled(FeatureFlag.ENSEMBLE_MODEL):
    result = ensemble_model.predict(image)
else:
    result = medical_model.predict(image)  # Fallback to existing

# ❌ WRONG: Replace existing model
# medical_model = ensemble_model  # DON'T DO THIS
DO: Test Backward Compatibility
Bash

# After every change
pytest tests/migration/test_backward_compatibility.py -v

# If fails, rollback immediately
git checkout HEAD~1 -- [modified-files]
📋 Pre-Deployment Checklist
Before ANY deployment to production:

 All backward compatibility tests pass (100%)
 No modifications to files in "DO NOT MODIFY" sections
 Feature flags verified working
 Rollback procedure tested
 CTX_SYNC.md updated
 Quality gate passed
 Human coordinator approval obtained
Last Updated: 2025-01-31
Maintained By: AG-00 (MigrationLead)
Review Frequency: Before starting each phase
```

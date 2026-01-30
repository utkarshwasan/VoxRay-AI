File 10: SHARED/07_TROUBLESHOOTING.md
Markdown

# VoxRay AI v2.0 - Troubleshooting Guide

**Purpose:** Comprehensive guide to diagnose and fix common issues

---

## 🔍 Quick Diagnostic Commands

Run these first when encountering any issue:

```bash
# Check system health
curl http://localhost:8000/health

# Check feature flags
curl http://localhost:8000/api/feature-flags

# Check backend logs
docker logs voxray-backend --tail 100

# Check frontend build
cd frontend && npm run build

# Run backward compatibility tests
pytest tests/migration/test_backward_compatibility.py -v

# Check model loading
python -c "import tensorflow as tf; model = tf.keras.models.load_model('backend/models/medical_model_final.keras'); print('Model loaded:', model)"
🚨 Critical Issues (Production Blockers)
Issue: React White Screen (Error #426)
Symptoms:

Blank white screen after API response
Console shows "Minified React error #426"
App crashes when displaying results
Causes:

Missing Suspense boundary around lazy-loaded components
State updates not wrapped in startTransition
Hooks called conditionally or in loops
Diagnosis:

Bash

# Check browser console for full error
# Look for stack trace pointing to component

# Check if error boundaries are in place
grep -r "ErrorBoundary" frontend/src/components/
Solution:

React

// 1. Ensure Error Boundary exists
// frontend/src/components/ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong. Please refresh.</div>;
    }
    return this.props.children;
  }
}

// 2. Wrap heavy state updates in startTransition
import { startTransition } from 'react';

// ❌ WRONG
setResult(data);
setIsLoading(false);

// ✅ CORRECT
startTransition(() => {
  setResult(data);
  setIsLoading(false);
});

// 3. Add Suspense boundaries
import { Suspense } from 'react';

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <Dashboard />
      </Suspense>
    </ErrorBoundary>
  );
}
Prevention:

All state updates after API calls use startTransition
All routes wrapped in Suspense
All major sections wrapped in ErrorBoundary
Issue: Authentication Failure (401 Unauthorized)
Symptoms:

All API calls return 401
"Missing token" or "Invalid token" errors
Login works but subsequent requests fail
Diagnosis:

Bash

# Check token is being sent
# In browser DevTools > Network tab
# Look for x-stack-access-token header

# Test token manually
curl -X POST http://localhost:8000/predict/image \
  -H "x-stack-access-token: YOUR_TOKEN" \
  -F "image_file=@test.png"

# Check JWKS configuration
curl https://api.stack-auth.com/api/v1/projects/YOUR_PROJECT_ID/.well-known/jwks.json
Causes & Solutions:

Token not included in request:
JavaScript

// frontend/src/components/XRaySection.jsx
const authData = await user.getAuthJson();
const headers = { 'x-stack-access-token': authData.accessToken };
// Ensure headers are passed to fetch/axios
Token expired:
JavaScript

// Stack Auth should auto-refresh, but verify:
const user = useUser();
if (!user) {
  // Redirect to login
  navigate('/login');
}
JWKS URL incorrect:
Python

# backend/api/deps.py
JWKS_URL = f"https://api.stack-auth.com/api/v1/projects/{STACK_PROJECT_ID}/.well-known/jwks.json"
# Ensure STACK_PROJECT_ID is set in environment
STACK_PROJECT_ID missing:
Bash

# Check environment
echo $STACK_PROJECT_ID

# If empty, set it
export STACK_PROJECT_ID=your_project_id
Issue: Model Not Loading (503 Service Unavailable)
Symptoms:

/predict/image returns 503
Health check shows medical_model: not_loaded
Backend logs show model loading errors
Diagnosis:

Bash

# Check model file exists
ls -la backend/models/medical_model_final.keras

# Check file size (should be ~212 MB)
du -h backend/models/medical_model_final.keras

# Test model loading directly
python -c "
import tensorflow as tf
model = tf.keras.models.load_model('backend/models/medical_model_final.keras')
print('Model loaded successfully')
print('Input shape:', model.input_shape)
print('Output shape:', model.output_shape)
"
Causes & Solutions:

Model file missing:
Bash

# Download from model registry or backup
# If using Git LFS:
git lfs pull

# If file was not tracked:
# Copy from backup location
cp /backup/medical_model_final.keras backend/models/
TensorFlow version mismatch:
Bash

# Check TensorFlow version
python -c "import tensorflow as tf; print(tf.__version__)"

# Model was trained with specific version
# Install compatible version
pip install tensorflow==2.15.0
Keras 3 compatibility:
Python

# If using Keras 3, may need compatibility layer
import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # Before importing TF

import tensorflow as tf
model = tf.keras.models.load_model(model_path)
Memory issues:
Bash

# Check available memory
free -h

# If low memory, increase or use CPU-only
export CUDA_VISIBLE_DEVICES=-1  # Force CPU
GPU issues:
Bash

# Check GPU availability
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# If GPU not detected:
nvidia-smi  # Check driver

# Install CUDA toolkit if missing
Issue: CORS Errors
Symptoms:

Browser console shows "CORS policy" errors
Requests blocked by browser
Works in Postman but not in browser
Diagnosis:

Bash

# Check CORS configuration in backend
grep -A 10 "CORSMiddleware" backend/api/main.py
Solution:

Python

# backend/api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",        # Vite dev server
        "http://127.0.0.1:5173",
        "https://taupe-baklava-2d4afd.netlify.app",  # Production
        # Add your domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Common Mistakes:

Using * for allow_origins with allow_credentials=True (not allowed)
Not including both localhost and 127.0.0.1
Not including production domain
Typo in domain name
⚠️ Phase-Specific Issues
Phase 0: Migration Foundation
Issue: Feature Flags Not Loading
Symptoms:

All feature flags return false
FF_* environment variables ignored
Diagnosis:

Python

# Test in Python shell
import os
print(os.environ.get('FF_ENSEMBLE_MODEL'))

from backend.core.feature_flags import feature_flags
print(feature_flags.get_all_flags())
Solution:

Bash

# Ensure variables are exported (not just set)
export FF_ENSEMBLE_MODEL=true  # ✅ Correct
FF_ENSEMBLE_MODEL=true  # ❌ Not exported

# In Docker, check docker-compose.yml
services:
  backend:
    environment:
      - FF_ENSEMBLE_MODEL=true

# In .env file, ensure no spaces around =
FF_ENSEMBLE_MODEL=true  # ✅ Correct
FF_ENSEMBLE_MODEL = true  # ❌ Wrong
Issue: API Versioning Not Working
Symptoms:

/v1/* or /v2/* routes return 404
Only root-level routes work
Diagnosis:

Bash

# List all routes
curl http://localhost:8000/openapi.json | jq '.paths | keys'
Solution:

Python

# backend/api/main.py
# Ensure router is imported and included
from backend.api.router import setup_versioned_routes

app = FastAPI()
setup_versioned_routes(app)  # Must be called!
Phase 1: ML Core
Issue: Ensemble Model Out of Memory
Symptoms:

CUDA out of memory error
OOM in logs
Prediction crashes
Diagnosis:

Bash

# Check GPU memory usage
nvidia-smi

# Check model memory requirements
python -c "
import tensorflow as tf
model = tf.keras.models.load_model('backend/models/medical_model_final.keras')
print(f'Parameters: {model.count_params():,}')
"
Solution:

Python

# Option 1: Enable memory growth
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

# Option 2: Limit GPU memory
tf.config.set_logical_device_configuration(
    gpus[0],
    [tf.config.LogicalDeviceConfiguration(memory_limit=4096)]  # 4GB
)

# Option 3: Use mixed precision
tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Option 4: Reduce batch size
model.predict(image, batch_size=1)

# Option 5: Sequential inference (not parallel)
for model in ensemble.models:
    result = model.predict(image)  # One at a time
Issue: Uncertainty Estimates All NaN
Symptoms:

Uncertainty values are NaN or inf
MC Dropout not working
Diagnosis:

Python

import numpy as np

predictions = []
for _ in range(10):
    pred = model(image, training=True)  # Enable dropout
    predictions.append(pred.numpy())

predictions = np.array(predictions)
print("Mean:", np.mean(predictions, axis=0))
print("Var:", np.var(predictions, axis=0))
print("Any NaN:", np.isnan(predictions).any())
Solution:

Python

# Ensure model has dropout layers
model.summary()  # Check for Dropout layers

# If no dropout, add during inference
class MCDropout(tf.keras.layers.Layer):
    def __init__(self, rate):
        super().__init__()
        self.rate = rate

    def call(self, inputs, training=None):
        # Always apply dropout during MC inference
        return tf.nn.dropout(inputs, rate=self.rate)

# Add epsilon to avoid division by zero
variance = np.var(predictions, axis=0) + 1e-10
Phase 2: Clinical Integration
Issue: DICOM Parsing Fails
Symptoms:

pydicom throws errors
Some DICOM files not readable
Diagnosis:

Python

import pydicom

try:
    ds = pydicom.dcmread("problem_file.dcm")
except Exception as e:
    print(f"Error: {e}")

    # Try with force flag
    ds = pydicom.dcmread("problem_file.dcm", force=True)
    print("Transfer syntax:", ds.file_meta.TransferSyntaxUID)
Common Causes & Solutions:

Unsupported Transfer Syntax:
Python

# Install extra codec support
pip install pylibjpeg pylibjpeg-libjpeg

# Handle decompression
from pydicom.pixel_data_handlers import convert_color_space
ds.decompress()
Missing DICOM header:
Python

# Force read without header
ds = pydicom.dcmread(file_path, force=True)
Corrupted file:
Python

# Check file integrity
import hashlib
with open(file_path, 'rb') as f:
    checksum = hashlib.md5(f.read()).hexdigest()
print(f"MD5: {checksum}")
Issue: FHIR Connection Fails
Symptoms:

FHIR client returns connection errors
Timeouts when connecting to FHIR server
Diagnosis:

Bash

# Test FHIR server connectivity
curl -v https://fhir-server.example.com/fhir/metadata

# Check authentication
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://fhir-server.example.com/fhir/Patient/123
Solution:

Python

# backend/clinical/fhir/fhir_client.py

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add retry logic
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# Increase timeout
response = session.get(url, timeout=30)

# Handle authentication refresh
if response.status_code == 401:
    self._refresh_token()
    response = session.get(url, timeout=30)
Phase 3: Voice
Issue: Wake Word Not Detecting
Symptoms:

"Hey VoxRay" not recognized
High false positive rate
Diagnosis:

Python

# Test wake word detection
from backend.voice.wake_word import WakeWordDetector

detector = WakeWordDetector(sensitivity=0.5)
detector._detect(audio_chunk)  # Test with sample
Solution:

Python

# Adjust sensitivity
detector = WakeWordDetector(sensitivity=0.7)  # Higher = more sensitive

# Ensure audio format correct
# Wake word models typically need 16kHz, 16-bit, mono
import librosa
audio = librosa.resample(audio, orig_sr=44100, target_sr=16000)
Issue: Medical Terms Not Recognized
Symptoms:

Medical terms like "pneumonia", "consolidation" misheard
High WER on medical vocabulary
Solution:

Python

# Add medical terms to custom vocabulary
MEDICAL_TERMS = {
    "consolidation": ["consultation", "constellation"],
    "pneumonia": ["pneumatic", "ammonia"],
    "pleural": ["plural", "neural"],
    "atelectasis": ["at a lexus is", "athletics"],
}

def post_process_transcription(text):
    for correct, mistakes in MEDICAL_TERMS.items():
        for mistake in mistakes:
            text = text.replace(mistake, correct)
    return text
Issue: Spanish Recognition Poor
Symptoms:

Spanish words transcribed incorrectly
Language detection failing
Solution:

Python

# Use Spanish-specific model
from transformers import WhisperProcessor, WhisperForConditionalGeneration

processor = WhisperProcessor.from_pretrained("openai/whisper-base")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")

# Force Spanish language
forced_decoder_ids = processor.get_decoder_prompt_ids(
    language="spanish",
    task="transcribe"
)
predicted_ids = model.generate(
    input_features,
    forced_decoder_ids=forced_decoder_ids
)
Phase 4: DevOps
Issue: Docker Build Fails
Symptoms:

docker build exits with error
Missing dependencies
Common Errors & Solutions:

Missing system dependencies:
Dockerfile

# Add to Dockerfile
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*
pip install failures:
Dockerfile

# Use specific versions
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# If TensorFlow GPU issues:
RUN pip install tensorflow==2.15.0
Image too large:
Dockerfile

# Use multi-stage build
FROM python:3.11-slim AS builder
# ... build steps ...

FROM python:3.11-slim AS runtime
COPY --from=builder /app /app
# Only copy necessary files
Issue: Kubernetes Pod Crashing
Symptoms:

Pod status: CrashLoopBackOff
Pod keeps restarting
Diagnosis:

Bash

# Check pod status
kubectl get pods

# Check logs
kubectl logs pod-name --previous

# Describe pod for events
kubectl describe pod pod-name
Common Causes & Solutions:

OOMKilled:
YAML

# Increase memory limits
resources:
  limits:
    memory: "8Gi"
  requests:
    memory: "4Gi"
Liveness probe failing:
YAML

# Increase timeout
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 60  # Give time to load models
  periodSeconds: 30
  timeoutSeconds: 10
GPU not available:
YAML

# Ensure GPU node selector
nodeSelector:
  nvidia.com/gpu: "true"
resources:
  limits:
    nvidia.com/gpu: 1
Issue: Prometheus Metrics Not Showing
Symptoms:

Grafana dashboard empty
/metrics endpoint returns 404
Solution:

Python

# backend/api/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Add Prometheus instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Custom metrics
from prometheus_client import Counter, Histogram

prediction_counter = Counter(
    'predictions_total',
    'Total predictions',
    ['diagnosis']
)

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)
Phase 5-7: Integration
Issue: Frontend Build Fails
Symptoms:

npm run build exits with error
TypeScript/ESLint errors
Diagnosis:

Bash

# Check for errors
cd frontend
npm run lint
npm run build 2>&1 | head -50
Common Solutions:

Missing dependencies:
Bash

rm -rf node_modules package-lock.json
npm install
TypeScript errors:
Bash

# Check specific errors
npx tsc --noEmit

# Fix or add to ignore (temporary)
// @ts-ignore
ESLint errors:
Bash

# Auto-fix what's possible
npm run lint -- --fix
Issue: E2E Tests Failing
Symptoms:

Playwright tests timeout
Elements not found
Diagnosis:

Bash

# Run in debug mode
npx playwright test --debug

# Generate trace for failed test
npx playwright test --trace on
Solution:

JavaScript

// Increase timeouts
test.setTimeout(60000);

// Wait for element properly
await page.waitForSelector('[data-testid="result"]', {
  state: 'visible',
  timeout: 30000
});

// Handle loading states
await page.waitForLoadState('networkidle');
Issue: Load Test Failures
Symptoms:

High error rate (>5%)
Timeouts under load
Diagnosis:

Bash

# Run with more logging
locust -f tests/load/locustfile.py --headless -u 10 -r 1 -t 1m --html report.html
Solutions:

Database connection pool exhausted:
Python

# Increase pool size
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10
)
Model inference bottleneck:
Python

# Use async inference
import asyncio

async def predict_async(image):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, model.predict, image)
Insufficient replicas:
YAML

# Scale up
kubectl scale deployment voxray-backend --replicas=5
🛠️ Debugging Tools
Backend Debugging
Python

# Add to backend/api/main.py for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response
Frontend Debugging
JavaScript

// Add to frontend/src/main.jsx
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

// React DevTools
// Install: https://react.dev/learn/react-developer-tools
Performance Profiling
Python

# Backend profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... code to profile ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
📞 Escalation Path
Level 1: Self-Service (This Document)
Search this document for error message
Try suggested solutions
Check CTX_SYNC.md for known issues
Level 2: Agent Coordination
Update CTX_SYNC.md with issue
Tag relevant agent in blockers section
Wait for agent response (max 4 hours)
Level 3: Human Coordinator
Add 🚨 alert to CTX_SYNC.md
Document all attempted solutions
Provide logs and error messages
Level 4: External Support
Stack Auth issues: support@stack-auth.com
OpenRouter issues: support@openrouter.ai
AWS issues: AWS Support Center
📋 Pre-Flight Checklist
Before reporting an issue, verify:

Markdown

- [ ] Read error message completely
- [ ] Searched this document for error
- [ ] Checked logs (backend, frontend, docker)
- [ ] Verified environment variables set
- [ ] Ran backward compatibility tests
- [ ] Tried restarting services
- [ ] Checked CTX_SYNC.md for known issues
- [ ] Documented exact steps to reproduce
- [ ] Collected relevant logs/screenshots
Last Updated: 2025-01-31
Maintained By: All Agents (add issues as discovered)
Review Frequency: Weekly
```

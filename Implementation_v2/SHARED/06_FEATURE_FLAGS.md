## File 9: SHARED/06_FEATURE_FLAGS.md

````markdown
# VoxRay AI v2.0 - Feature Flags Guide

**Purpose:** Complete guide to using feature flags for safe rollout

---

## 🚩 Feature Flag Philosophy

### Why Feature Flags?

1. **Zero-Risk Deployment** - Deploy code without activating features
2. **Gradual Rollout** - Enable for 5% of users, then 20%, then 100%
3. **Instant Rollback** - Disable feature without redeployment
4. **A/B Testing** - Compare old vs. new implementation
5. **Environment Control** - Different flags per environment

---

## 📋 All Feature Flags

### Phase 1: ML Core

```yaml
FF_ENSEMBLE_MODEL:
  name: "Ensemble Model"
  description: "Enable ensemble prediction with ResNet50V2 + EfficientNet + ViT"
  owner: AG-01
  phase: 1
  default: false
  type: boolean
  impact: high
  dependencies: []
  fallback: "Use ResNet50V2 only (v1 behavior)"

  usage:
    backend: |
      from backend.core.feature_flags import feature_flags, FeatureFlag

      if feature_flags.is_enabled(FeatureFlag.ENSEMBLE_MODEL):
          result = ensemble_model.predict(image)
      else:
          result = medical_model.predict(image)

    api_endpoint: |
      @app.post("/v2/predict/ensemble")
      @require_feature(FeatureFlag.ENSEMBLE_MODEL)
      async def predict_ensemble(...):
          # Only accessible if flag enabled
          pass

FF_UNCERTAINTY_QUANTIFICATION:
  name: "Uncertainty Quantification"
  description: "Enable Monte Carlo Dropout uncertainty estimation"
  owner: AG-01
  phase: 1
  default: false
  type: boolean
  impact: medium
  dependencies: [FF_ENSEMBLE_MODEL]
  fallback: "No uncertainty metrics returned"

  usage:
    backend: |
      if feature_flags.is_enabled(FeatureFlag.UNCERTAINTY_QUANTIFICATION):
          uncertainty = uncertainty_estimator.estimate(image)
          result['uncertainty'] = uncertainty

FF_CROSS_VALIDATION:
  name: "Cross Validation"
  description: "Enable K-fold cross-validation for model evaluation"
  owner: AG-01
  phase: 1
  default: false
  type: boolean
  impact: low
  dependencies: []
  fallback: "Single train/test split only"

FF_BENCHMARKING:
  name: "Clinical Benchmarking"
  description: "Enable evaluation on ChestX-ray14, CheXpert datasets"
  owner: AG-01
  phase: 1
  default: false
  type: boolean
  impact: low
  dependencies: []
  fallback: "No external benchmarking"
Phase 2: Clinical Integration
YAML

FF_DICOM_SUPPORT:
  name: "DICOM Support"
  description: "Enable DICOM file upload and parsing"
  owner: AG-03
  phase: 2
  default: false
  type: boolean
  impact: high
  dependencies: []
  fallback: "PNG/JPEG only"

  usage:
    api_endpoint: |
      @app.post("/v2/predict/dicom")
      @require_feature(FeatureFlag.DICOM_SUPPORT)
      async def predict_dicom(...):
          pass

FF_FHIR_INTEGRATION:
  name: "FHIR Integration"
  description: "Enable HL7 FHIR client for EHR integration"
  owner: AG-03
  phase: 2
  default: false
  type: boolean
  impact: high
  dependencies: []
  fallback: "No FHIR connectivity"

FF_AUDIT_LOGGING:
  name: "Audit Logging"
  description: "Enable HIPAA-compliant audit logging"
  owner: AG-03
  phase: 2
  default: true  # Should always be on in production
  type: boolean
  impact: critical
  dependencies: []
  fallback: "Basic logging only (not compliant)"

FF_DATA_ANONYMIZATION:
  name: "Data Anonymization"
  description: "Enable DICOM anonymization (HIPAA Safe Harbor)"
  owner: AG-03
  phase: 2
  default: true  # Should always be on
  type: boolean
  impact: critical
  dependencies: [FF_DICOM_SUPPORT]
  fallback: "No anonymization (DO NOT USE IN PRODUCTION)"
Phase 3: Voice Enhancement
YAML

FF_WAKE_WORD_DETECTION:
  name: "Wake Word Detection"
  description: "Enable 'Hey VoxRay' wake word for hands-free activation"
  owner: AG-04
  phase: 3
  default: false
  type: boolean
  impact: medium
  dependencies: []
  fallback: "Manual push-to-talk only"

  usage:
    backend: |
      if feature_flags.is_enabled(FeatureFlag.WAKE_WORD_DETECTION):
          detector = WakeWordDetector()
          detector.start(on_wake=start_recording)

FF_MULTILINGUAL_VOICE:
  name: "Multilingual Voice"
  description: "Enable Spanish voice recognition and TTS"
  owner: AG-04
  phase: 3
  default: false
  type: boolean
  impact: medium
  dependencies: []
  fallback: "English only"

FF_MEDICAL_VOCABULARY:
  name: "Medical Vocabulary"
  description: "Enable enhanced medical term recognition"
  owner: AG-04
  phase: 3
  default: false
  type: boolean
  impact: low
  dependencies: []
  fallback: "Standard vocabulary"

FF_NOISE_HANDLING:
  name: "Noise Handling"
  description: "Enable adaptive VAD for noisy environments"
  owner: AG-04
  phase: 3
  default: false
  type: boolean
  impact: low
  dependencies: []
  fallback: "Fixed VAD threshold"
Phase 4-7: Frontend & Integration
YAML

FF_ADVANCED_HEATMAP:
  name: "Advanced Heatmap"
  description: "Enable Grad-CAM++ visualization"
  owner: AG-06
  phase: 3
  default: false
  type: boolean
  impact: low
  dependencies: []
  fallback: "Standard Grad-CAM"

FF_WORKLIST_MANAGEMENT:
  name: "Worklist Management"
  description: "Enable radiologist worklist and case prioritization"
  owner: AG-06
  phase: 7
  default: false
  type: boolean
  impact: medium
  dependencies: []
  fallback: "Single-case view only"

FF_BATCH_PROCESSING:
  name: "Batch Processing"
  description: "Enable multi-image batch prediction"
  owner: AG-06
  phase: 7
  default: false
  type: boolean
  impact: medium
  dependencies: []
  fallback: "Single image only"

FF_MOBILE_PWA:
  name: "Mobile PWA"
  description: "Enable Progressive Web App features"
  owner: AG-06
  phase: 7
  default: false
  type: boolean
  impact: low
  dependencies: []
  fallback: "Desktop-only experience"
🔧 Implementation Guide
Backend Implementation
1. Environment Configuration
File: .env.example

Bash

# Phase 1: ML Core
FF_ENSEMBLE_MODEL=false
FF_UNCERTAINTY_QUANTIFICATION=false
FF_CROSS_VALIDATION=false
FF_BENCHMARKING=false

# Phase 2: Clinical
FF_DICOM_SUPPORT=false
FF_FHIR_INTEGRATION=false
FF_AUDIT_LOGGING=true  # Always on in production
FF_DATA_ANONYMIZATION=true  # Always on in production

# Phase 3: Voice
FF_WAKE_WORD_DETECTION=false
FF_MULTILINGUAL_VOICE=false
FF_MEDICAL_VOCABULARY=false
FF_NOISE_HANDLING=false

# Phase 4-7: Frontend
FF_ADVANCED_HEATMAP=false
FF_WORKLIST_MANAGEMENT=false
FF_BATCH_PROCESSING=false
FF_MOBILE_PWA=false
2. Feature Flag Manager (Already Implemented by AG-00)
File: backend/core/feature_flags.py

Python

# This is implemented in Phase 0 by AG-00
# See AG-00 instructions for complete code
from backend.core.feature_flags import feature_flags, FeatureFlag, require_feature
3. Usage Patterns
Pattern 1: Conditional Logic

Python

from backend.core.feature_flags import feature_flags, FeatureFlag

def predict_image(image):
    if feature_flags.is_enabled(FeatureFlag.ENSEMBLE_MODEL):
        # New feature
        result = ensemble_model.predict(image)

        if feature_flags.is_enabled(FeatureFlag.UNCERTAINTY_QUANTIFICATION):
            result['uncertainty'] = uncertainty_estimator.estimate(image)
    else:
        # Fallback to v1 behavior
        result = medical_model.predict(image)

    return result
Pattern 2: Endpoint Gating (Recommended)

Python

from backend.core.feature_flags import require_feature, FeatureFlag
from fastapi import HTTPException

@app.post("/v2/predict/dicom")
@require_feature(FeatureFlag.DICOM_SUPPORT)
async def predict_dicom(file: UploadFile):
    # If flag disabled, decorator returns 503
    # If flag enabled, endpoint is accessible
    result = dicom_handler.process(file)
    return result
Pattern 3: Gradual Rollout (Advanced)

Python

import hashlib

def is_enabled_for_user(flag: FeatureFlag, user_id: str, rollout_percent: int = 100) -> bool:
    """
    Enable feature for percentage of users based on deterministic hash

    rollout_percent: 0-100
    """
    if not feature_flags.is_enabled(flag):
        return False

    if rollout_percent >= 100:
        return True

    # Deterministic hash to ensure same user always gets same result
    hash_value = int(hashlib.md5(f"{flag.value}{user_id}".encode()).hexdigest(), 16)
    bucket = hash_value % 100

    return bucket < rollout_percent

# Usage
if is_enabled_for_user(FeatureFlag.ENSEMBLE_MODEL, user_id, rollout_percent=20):
    # 20% of users get ensemble model
    pass
Frontend Implementation
1. Check Backend Feature Flags
JavaScript

// frontend/src/utils/featureFlags.js

export async function getFeatureFlags() {
  try {
    const response = await fetch(`${API_BASE}/api/feature-flags`);
    const data = await response.json();
    return data.flags;
  } catch (error) {
    console.error('Failed to fetch feature flags:', error);
    return {};
  }
}

// Usage in component
import { useEffect, useState } from 'react';
import { getFeatureFlags } from '../utils/featureFlags';

function XRaySection() {
  const [flags, setFlags] = useState({});

  useEffect(() => {
    getFeatureFlags().then(setFlags);
  }, []);

  const showDicomUpload = flags.dicom_support === true;

  return (
    <div>
      {/* Standard PNG/JPEG upload */}
      <FileUpload accept="image/png,image/jpeg" />

      {/* DICOM upload (only if enabled) */}
      {showDicomUpload && (
        <FileUpload accept="application/dicom" label="Upload DICOM" />
      )}
    </div>
  );
}
2. Feature Flag Context (Recommended)
JavaScript

// frontend/src/contexts/FeatureFlagContext.jsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import { getFeatureFlags } from '../utils/featureFlags';

const FeatureFlagContext = createContext({});

export function FeatureFlagProvider({ children }) {
  const [flags, setFlags] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFeatureFlags()
      .then(setFlags)
      .finally(() => setLoading(false));
  }, []);

  return (
    <FeatureFlagContext.Provider value={{ flags, loading }}>
      {children}
    </FeatureFlagContext.Provider>
  );
}

export function useFeatureFlags() {
  return useContext(FeatureFlagContext);
}

// Usage
function App() {
  return (
    <FeatureFlagProvider>
      <Dashboard />
    </FeatureFlagProvider>
  );
}

function Dashboard() {
  const { flags, loading } = useFeatureFlags();

  if (loading) return <Loader />;

  return (
    <div>
      {flags.worklist_management && <WorklistPanel />}
      {flags.batch_processing && <BatchUpload />}
    </div>
  );
}
🎛️ Feature Flag Lifecycle
1. Development Phase
Bash

# Developer working on ensemble feature
export FF_ENSEMBLE_MODEL=true
export FF_UNCERTAINTY_QUANTIFICATION=true

# All other flags false
npm run dev
2. Testing Phase
Bash

# Staging environment
FF_ENSEMBLE_MODEL=true
FF_UNCERTAINTY_QUANTIFICATION=true
FF_DICOM_SUPPORT=true  # Test clinical features

# Test both enabled and disabled states
3. Production Rollout
Week 1: Canary (5% of users)
Python

# In code
if is_enabled_for_user(FeatureFlag.ENSEMBLE_MODEL, user_id, rollout_percent=5):
    use_ensemble()
Week 2: Expand (20% of users)
Python

rollout_percent = 20
Week 3: Majority (50% of users)
Python

rollout_percent = 50
Week 4: Full Rollout (100%)
Bash

# In production environment
FF_ENSEMBLE_MODEL=true  # Enable for all users
4. Cleanup (After 30 days of stable operation)
Python

# Remove flag checks from code
# Old code:
if feature_flags.is_enabled(FeatureFlag.ENSEMBLE_MODEL):
    result = ensemble_model.predict(image)
else:
    result = medical_model.predict(image)

# New code (after flag removed):
result = ensemble_model.predict(image)  # Now default behavior
🚨 Emergency Procedures
Instant Rollback
If feature causes issues in production:

Bash

# Method 1: Environment variable (no deployment needed)
# On AWS: Update ECS task definition or K8s ConfigMap
kubectl set env deployment/voxray-backend FF_ENSEMBLE_MODEL=false

# Method 2: Runtime toggle (if implemented)
curl -X POST https://api.voxray.ai/admin/feature-flags/disable \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"flag": "ensemble_model"}'

# Changes take effect immediately (next request)
Monitoring
YAML

alerts:
  - name: "Feature Flag Error Rate"
    condition: "error_rate_with_flag_enabled > 5%"
    action: "Auto-disable flag and alert team"

  - name: "Feature Flag Performance"
    condition: "p95_latency_with_flag > 2x baseline"
    action: "Alert team for investigation"
📊 Feature Flag Dashboard
Track flag usage in shared_context/feature_flag_status.json:

JSON

{
  "last_updated": "2025-01-31T12:00:00Z",
  "environment": "production",
  "flags": {
    "ensemble_model": {
      "enabled": true,
      "rollout_percent": 100,
      "users_affected": 10000,
      "enabled_since": "2025-01-20",
      "error_rate": 0.002,
      "p95_latency_ms": 450,
      "owner": "AG-01",
      "ready_for_cleanup": false
    },
    "dicom_support": {
      "enabled": false,
      "rollout_percent": 0,
      "users_affected": 0,
      "planned_rollout": "2025-02-01",
      "owner": "AG-03"
    }
  }
}
✅ Best Practices
DO
✅ Always have a fallback behavior
✅ Test both enabled and disabled states
✅ Use descriptive flag names
✅ Document what each flag controls
✅ Clean up flags after stable (30+ days)
✅ Use flags for risky features
✅ Monitor performance with flags enabled
DON'T
❌ Nest flags too deeply (max 2 levels)
❌ Use flags for non-risky features (overkill)
❌ Leave flags in code forever
❌ Skip fallback implementation
❌ Enable all flags at once
❌ Use flags for configuration (use env vars)
🧪 Testing Feature Flags
Python

# tests/unit/test_feature_flags.py

import pytest
import os
from backend.core.feature_flags import FeatureFlagManager, FeatureFlag

def test_feature_flag_disabled_by_default():
    """All flags should be false by default"""
    os.environ.clear()
    manager = FeatureFlagManager()

    for flag in FeatureFlag:
        assert not manager.is_enabled(flag)

def test_feature_flag_enabled_via_env():
    """Flags can be enabled via environment variable"""
    os.environ['FF_ENSEMBLE_MODEL'] = 'true'
    manager = FeatureFlagManager()

    assert manager.is_enabled(FeatureFlag.ENSEMBLE_MODEL)

def test_feature_flag_runtime_toggle():
    """Flags can be toggled at runtime"""
    manager = FeatureFlagManager()

    manager.enable(FeatureFlag.ENSEMBLE_MODEL)
    assert manager.is_enabled(FeatureFlag.ENSEMBLE_MODEL)

    manager.disable(FeatureFlag.ENSEMBLE_MODEL)
    assert not manager.is_enabled(FeatureFlag.ENSEMBLE_MODEL)

def test_require_feature_decorator():
    """Endpoint decorator blocks when flag disabled"""
    from fastapi.testclient import TestClient
    from backend.api.main import app

    os.environ['FF_DICOM_SUPPORT'] = 'false'
    client = TestClient(app)

    response = client.post("/v2/predict/dicom", files={"file": "test"})
    assert response.status_code == 503
    assert "not enabled" in response.json()['detail']['message']
Last Updated: 2025-01-31
Maintained By: AG-00 (MigrationLead)
Review Frequency: Weekly during rollout, Monthly after stable
```
````

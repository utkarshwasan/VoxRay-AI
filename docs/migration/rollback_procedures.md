# Migration Rollback Procedures (VoxRay AI v2.0)

**Severity:** CRITICAL  
**Last Updated:** 2026-01-31  
**Owner:** AG-00 (Migration Lead)

---

## Overview

This document describes how to quickly revert VoxRay AI from the v2.0 feature set
back to safe v1.0 behavior, or how to disable specific v2 features via feature flags.

Current architecture:

- Frontend: Netlify (`https://taupe-baklava-2d4afd.netlify.app`)
- Backend: Hugging Face Spaces (FastAPI on Uvicorn)
- Auth: Stack Auth (JWT → `x-stack-access-token`)

---

## Scenario A: Feature Malfunction (Non-Destructive)

**Examples:**

- Ensemble model is slow or returns odd results.
- DICOM endpoint unstable.
- Voice enhancements misbehaving.

**Action: Disable v2 features via Feature Flags**

1. Open the backend environment configuration (Hugging Face Space → Settings → Variables and secrets).
2. Find feature flag variables (examples):

   ```bash
   FF_ENSEMBLE_MODEL=true
   FF_UNCERTAINTY_QUANTIFICATION=true
   FF_DICOM_SUPPORT=true
   FF_MULTILINGUAL_VOICE=true
   # ...
   ```

3. Set critical flags to `false`:

   ```bash
   FF_ENSEMBLE_MODEL=false
   FF_UNCERTAINTY_QUANTIFICATION=false
   FF_DICOM_SUPPORT=false
   FF_FHIR_INTEGRATION=false
   FF_WAKE_WORD_DETECTION=false
   FF_MULTILINGUAL_VOICE=false
   FF_MEDICAL_VOCABULARY=false
   FF_NOISE_HANDLING=false
   FF_ADVANCED_HEATMAP=false
   FF_WORKLIST_MANAGEMENT=false
   FF_BATCH_PROCESSING=false
   FF_MOBILE_PWA=false
   ```

4. Restart the backend (Hugging Face will restart on config change).

5. Verify:

   ```bash
   curl https://<your-hf-space-url>/health
   pytest tests/migration/test_backward_compatibility.py -v
   ```

**Expected:** v1 behavior restored, no v2 features active.

---

## Scenario B: Critical Backend Failure

**Examples:**

- `/predict/image` returns 500 for all requests.
- Backend does not start (crash loop).
- Authentication route broken.

### Step 1: Revert Code to Last Known Good Commit

If you keep your backend code in GitHub/GitLab:

```bash
git log --oneline  # find last stable commit
git checkout <stable-commit>
git push origin main --force
# Redeploy Space from stable commit
```

### Step 2: Confirm Health

```bash
curl https://<your-hf-space-url>/health
pytest tests/migration/test_backward_compatibility.py -v
```

---

## Scenario C: Frontend Regression (Netlify)

**Examples:**

- After deploying a new frontend build, the app shows a white screen.
- React error #426 visible in browser console.

### Step 1: Roll Back Netlify Deploy

1. Go to Netlify dashboard → `taupe-baklava-2d4afd`.
2. Go to "Deploys".
3. Select previous successful deploy (green check).
4. Click "Rollback to this deploy".

### Step 2: Clear Browser Cache

Ask users to:

- Hard refresh: `Ctrl+Shift+R` (Windows/Linux), `Cmd+Shift+R` (macOS).

---

## Post-Rollback Checklist

After any rollback:

- [ ] `/predict/image` returns 200 with `{diagnosis, confidence}`.
- [ ] `/transcribe/audio` returns 200 with `{transcription}`.
- [ ] `/chat` returns 200 with `{response}`.
- [ ] `/health` returns 200 and `"status"` appropriate.
- [ ] Protected endpoints return 401/403 without a valid token.
- [ ] Frontend at Netlify loads and can complete an X-ray analysis workflow without crashing.
- [ ] `pytest tests/migration/test_backward_compatibility.py -v` passes.

---

## Recording the Incident

Create a new file under `docs/incidents/` named `YYYY-MM-DD-<short-name>.md`.

Include:

- Summary of the incident.
- Timeline.
- Root cause (if known).
- Actions taken (rollback steps).
- Preventive actions for future.

**Owner:** AG-00 (Migration Lead)  
**Co-Owners:** AG-05 (DevOps), Human Coordinator

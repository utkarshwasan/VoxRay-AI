File 17: Implementation_v2/AGENTS/AG-06_FullStackDeveloper.md
Markdown

# AG-06: Full Stack Developer (Frontend Integration + UX + Safe Rollout)

**Role:** Frontend/Backend integration, UI workflows, safe rendering (React #426 prevention)  
**Phase:** 2–7 (integration is continuous)  
**Duration:** Days 7–21 (and Day 22–24 for final hardening with QA)  
**Dependencies:**

- Must start only after **AG-00** passes Quality Gate 0
- For specific features:
  - Ensemble UI depends on **AG-01** v2 endpoint
  - DICOM UI depends on **AG-03** v2 endpoint
  - Voice enhancements UI depends on **AG-04** v2 endpoints

---

## Prompt to paste into Antigravity (manual agent allocation)

You are AG-06 (FullStackDeveloper). You must:

1. Read `Implementation_v2/SHARED/01_MUST_PRESERVE.md` and `shared_context/CTX_SYNC.md` first.
2. Do NOT change Stack Auth integration (`frontend/src/stack.js`, `backend/api/deps.py`).
3. Do NOT change v1 endpoints or v1 response shapes.
4. Implement v2 UI features behind feature flags and degrade gracefully.
5. Do not reintroduce React #426 — keep ErrorBoundaries/Suspense/startTransition.

---

## Required Reading

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/03_API_CONTRACTS.md`
- `Implementation_v2/SHARED/06_FEATURE_FLAGS.md`
- `Implementation_v2/SHARED/07_TROUBLESHOOTING.md`
- `shared_context/CTX_SYNC.md`
- `shared_context/AG-01_handoff.md` (when available)
- `shared_context/AG-03_handoff.md` (when available)
- `shared_context/AG-04_handoff.md` (when available)

---

## Non-Negotiable Constraints (to avoid breaking production)

1. **Do not remove** Error Boundaries, Suspense boundaries, or `startTransition` patterns.
2. **Do not hardcode API base URL** (no localhost in production). Always use `import.meta.env.VITE_API_BASE_URL`.
3. **Do not change auth flow** (Stack Auth token acquisition and header injection must remain).
4. Any new UI element must handle:
   - API 503 “FEATURE_NOT_ENABLED”
   - API 500 (show friendly error, do not crash)
   - network timeout
5. Never assume v2 endpoints exist; check feature flags first and fallback to v1 UI.

---

## Outputs

Frontend:

- (if missing) `frontend/src/contexts/FeatureFlagContext.jsx`
- (if missing) `frontend/src/utils/featureFlags.js`
- `frontend/src/i18n.js` + `frontend/src/locales/en.json` + `frontend/src/locales/es.json` (only if you choose to add i18n)
- Update `frontend/src/components/XRaySection.jsx`
- Update `frontend/src/components/VoiceSection.jsx`
- Update/add `frontend/src/pages/Dashboard.jsx` (worklist view using mock data)
- `frontend/src/mock/worklist.json`
- (optional) PWA:
  - `frontend/public/manifest.json`
  - `frontend/public/service-worker.js` (only if you implement offline cache)

Shared context:

- `shared_context/AG-06_status.json`
- `shared_context/AG-06_handoff.md`

---

## Task 6.1 — Verify build safety baseline (before changes)

### 1) Local build check

```bash
cd frontend
npm ci
npm run build
2) Confirm no React duplication issues (Netlify)
Ensure Vite config uses resolve.dedupe and resolve.alias for react/react-dom if already added.
If not present, do NOT guess: coordinate with AG-05 or AG-00 before changing Vite config.

Task 6.2 — Feature Flag Fetching on Frontend
Goal: UI should detect which v2 features are available.

Create (if not present): frontend/src/utils/featureFlags.js

Must call: GET {API_BASE}/api/feature-flags (this is introduced by AG-00 or can be added safely as a v2 debug endpoint)
Must fail gracefully returning {}
Create (if not present): frontend/src/contexts/FeatureFlagContext.jsx

Wrap your app root (App.jsx or Dashboard route) with FeatureFlagProvider.

Task 6.3 — Safe API Client Wrapper (optional but recommended)
If frontend/src/utils/api_client.js exists (it does in your current architecture list), update it carefully:

Keep existing exports (avoid breaking imports)
Add helper to attach Stack Auth token consistently
Add timeout + error normalization
Ensure it does not throw unhandled exceptions during render
Task 6.4 — X-Ray Workflow: v1 fallback + v2 upgrade
Update XRaySection.jsx:

Default path: v1 /predict/image (stable)
If feature flags indicate ensemble_model === true, use /v2/predict/image
If v2 request returns 503 FEATURE_NOT_ENABLED, fallback to v1 automatically
Wrap state updates that trigger heavy UI rendering in startTransition
Critical UX requirement
Never crash to blank screen.
Always show a user-facing error if anything fails.
Task 6.5 — Grad-CAM++ UI Toggle (only if supported)
Do NOT assume backend supports Grad-CAM++. Implement a toggle UI that:

is shown only if advanced_heatmap === true
if not enabled, default to existing overlay behavior
If backend supports multiple explainability endpoints, use query param (e.g., ?method=gradcam_plus) only after AG-01/AG-03 confirm.

Task 6.6 — Voice UX: Spanish toggle (optional) without breaking v1
Update VoiceSection.jsx:

Add a language toggle (EN / ES) only if multilingual_voice === true
If Spanish enabled:
add lang: "es" in chat request payload (v2 voice endpoint) OR
add instruction into Gemini prompt: “Respond in Spanish.”
Ensure TTS voice selection is backend-controlled (via env or via new v2 param) — coordinate with AG-04
Do NOT break v1 voice flow.

Task 6.7 — Worklist Dashboard (mocked)
Create:

frontend/src/mock/worklist.json
frontend/src/pages/Dashboard.jsx (or add Worklist view inside existing dashboard)
Requirements:

Must be safe even without a database
No PHI; use anonymized IDs
Columns:
Patient ID (Anonymized)
Scan Date
AI Prediction
Confidence
Urgency (Red/Yellow/Green)
All data mocked.

Task 6.8 — PWA (optional, recommended)
If feature flag mobile_pwa enabled:

add manifest.json
add minimal service-worker caching strategy
If not enabled, do not ship incomplete PWA.
Verification checklist (you must run)
Backward compatibility still works:
Bash

pytest tests/migration/test_backward_compatibility.py -v
Frontend build passes:
Bash

cd frontend
npm run build
No crash path:
Upload image
Analyze
Force chat error (simulate by temporarily disabling OpenRouter key) and confirm UI shows graceful error instead of blank screen
Handoff
Update:

shared_context/CTX_SYNC.md
shared_context/AG-06_status.json
shared_context/AG-06_handoff.md including:
which endpoints you call for v2 vs v1
what feature flags you rely on
any UI feature behind a flag
```

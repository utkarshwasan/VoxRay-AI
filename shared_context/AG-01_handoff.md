# AG-01 Model Architect - Handoff Document

**Agent:** AG-01 (Model Architect)
**Phase:** 1 - ML Core & Architecture
**Status:** ✅ Complete
**Date:** 2026-01-31

## Summary

Phase 1 is complete. Core ML infrastructure (Ensemble, Uncertainty, ModelServer) is deployed and exposed via a modular V2 API.

## Deliverables

### 1. ML Components

- **Ensemble:** `backend/models/ensemble/ensemble_model.py`
- **Uncertainty:** `backend/models/uncertainty/mc_dropout.py`
- **Benchmarks:** `backend/models/benchmarks/clinical_benchmarks.py`
- **Model Server:** `backend/serving/model_server.py` (Singleton)

### 2. V2 API

- **Main Router:** `backend/api/v2.py` (Clean router, uses `include_router`)
- **Prediction Logic:** `backend/api/routes/v2_predict.py`
  - Gated by `FF_ENSEMBLE_MODEL`.
  - Endpoint: `POST /v2/predict/image`.

## Verification

- **Backward Compatibility:** `pytest tests/migration/test_backward_compatibility.py` ✅ PASSED
- **V2 Verification:** `pytest tests/manual_v2_check.py` ✅ PASSED (Mocked auth & model)

## Critical Notes for Next Agents

- **AG-02 (Pipeline):** Use `ModelServer` logic for inference pipeline.
- **AG-03 (Clinical):** Add new routes in `backend/api/routes/v2_clinical.py` and include in `v2.py`.
- **AG-04 (Voice):** Add new routes in `backend/api/routes/v2_voice.py` and include in `v2.py`.
- **AG-08 (QA):** Expand `manual_v2_check.py` into full integration suite.

**Handoff Complete**

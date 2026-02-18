# AG-02 Pipeline Engineer - Handoff Document

**Agent:** AG-02 (Pipeline Engineer)  
**Phase:** 1b - ML Pipeline & MLOps  
**Status:** ✅ Complete (Verified)

**Date:** 2026-02-14

---

## Summary

Implemented basic MLOps pipeline components for drift detection, retraining triggers, and fairness indicators. The system is designed to run locally or in CI, with graceful degradation if optional dependencies (TFDV) are missing.

---

## Deliverables

### 1. Drift Detection (`pipeline/drift_detection/`)

- **`data_validator.py`**: CLI tool to detect drift between new data and a schema.
  - Supports: TFRecords (full stats)
  - Degrades gracefully: Returns "skipped" if TFDV is missing or format unsupported.
- **Tests:** `pipeline/tests/test_drift_detector.py`

### 2. Validation Logic (`pipeline/validation/`)

- **`retraining_trigger.py`**: Logic to decide if retraining is needed based on metrics.
  - Config: `performance_thresholds.yaml`
  - Triggers: Accuracy drop, Drift score spike.
- **`fairness_indicators.py`**: Computes fairness metrics.
  - Skips gracefully if demographic data is missing.
- **Tests:** `pipeline/tests/test_retraining_trigger.py`, `pipeline/tests/test_fairness.py`

### 3. CI/CD (`.github/workflows/`)

- **`tfx-ci.yml`**: GitHub Action to run pipeline tests on push/PR.

---

## How to Use

### Run Drift Detection

```bash
python pipeline/drift_detection/data_validator.py \
  --schema path/to/schema.pbtxt \
  --new_data path/to/data.tfrecord \
  --out report.json
```

### Check Retraining Decision

```python
from pipeline.validation.retraining_trigger import RetrainingTrigger
trigger = RetrainingTrigger("pipeline/validation/performance_thresholds.yaml")
decision = trigger.evaluate({"accuracy": 0.81, "drift_score": 0.5})
if decision.should_retrain:
    print(f"Retrain needed: {decision.reason}")
```

---

## Verification

- **Unit Tests:** ✅ Passed (12/12 tests) via `pytest pipeline/tests/ -v`
- **Manual Check:** Scripts run and handle missing files/dependencies correctly.

---

## Next Steps

- **AG-07 (Data Scientist):** Use `data_validator.py` to analyze new batches of X-ray data.
- **AG-05 (DevOps):** Integrate `tfx-ci.yml` into the main CI pipeline if needed.

---

**Known Issues:**

- TFDV installation is heavy. The module is designed to work without it (returns "skipped") to avoid blocking other lightweight tasks.

# Automated Retraining Triggers

## Overview

The retraining trigger module (`pipeline/validation/retraining_trigger.py`) evaluates model performance metrics against defined thresholds to decide if a new training job should be launched.

## Configuration

Thresholds are defined in `pipeline/validation/performance_thresholds.yaml`:

```yaml
thresholds:
  accuracy_min: 0.85
  drift_score_max: 0.3
  false_positive_rate_max_delta: 0.10
```

## Logic

The evaluator implements the following rules:

1. **Accuracy Breach**: If `accuracy < accuracy_min` -> **RETRAIN**.
2. **Drift Breach**: If `drift_score > drift_score_max` -> **RETRAIN**.
3. **False Positive Spike**: If `fp_delta > max_delta` -> **ALERT** (or retrain if configured).

## Integration

In a CI pipeline, this module consumes the output of the evaluation step:

```bash
python pipeline/validation/retraining_trigger.py \
  --thresholds pipeline/validation/performance_thresholds.yaml \
  --metrics '{"accuracy": 0.82, "drift_score": 0.1}'
```

# Data Drift Detection (MLOps)

## Overview

The drift detection module (`pipeline/drift_detection/data_validator.py`) monitors input data for statistical anomalies compared to a reference schema. It is designed to run in both local and CI environments.

## How it Works

1. **Schema Loading**: Loads a TFDV schema (`.pbtxt`).
2. **Data Ingestion**: Reads new data (supports TFRecords).
3. **Statistics Generation**: Computes stats using `tensorflow-data-validation`.
4. **Validation**: Compares new stats against the schema.
5. **Reporting**: Outputs a JSON report with drift status and score.

## Graceful Degradation

If `tensorflow-data-validation` is not installed or the data format is unsupported (e.g., CSV), the detector returns `status="skipped"`.

## Usage

```bash
python pipeline/drift_detection/data_validator.py \
  --schema models/schema.pbtxt \
  --new_data data/daily_batch.tfrecord \
  --out drift_report.json
```

## interpreting the Report

- **ok**: No anomalies found.
- **drift_detected**: Statistical properties have shifted beyond thresholds.
- **skipped**: Validation could not be performed (missing lib/format).
- **error**: System error occurred.

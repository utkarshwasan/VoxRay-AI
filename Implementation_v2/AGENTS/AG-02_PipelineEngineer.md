File 13: Implementation_v2/AGENTS/AG-02_PipelineEngineer.md
Markdown

# AG-02: Pipeline Engineer (TFX / MLOps / Drift / Retraining)

**Role:** TFX/MLOps & Data Engineering  
**Phase:** 1b (extends Phase 1)  
**Duration:** Days 5–9 (can overlap once AG-01 exposes model interfaces)  
**Dependencies:** AG-01 handoff (model architecture + evaluation artifacts)  
**Blocking:** YES for "production-grade" MLOps; NO for keeping v1 live

---

## Mission

Improve the ML pipeline without breaking the live inference system:

1. Add **data validation & drift detection** (TFDV / TFX ExampleValidator)
2. Add **automated retraining triggers** (threshold-based + drift-based)
3. Add **fairness indicators** (only if demographic metadata exists)
4. Add **CI automation** for pipeline tests

This work MUST NOT modify or disrupt:

- current live inference endpoints in `backend/api/main.py`
- current model artifact `backend/models/medical_model_final.keras`

---

## Required Reading

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/02_QUALITY_GATES.md` (Gate 1 & Gate 5 context)
- `Implementation_v2/SHARED/04_TIMELINE.md`
- `shared_context/CTX_SYNC.md`
- `shared_context/AG-01_handoff.md` (once AG-01 provides it)

---

## Constraints

- Do not assume the presence of demographic labels. If not available, fairness indicators should:
  - detect missing metadata and skip gracefully (exit 0, “SKIPPED”)
- Do not require cloud services (GCP) as mandatory; provide local-compatible pipeline
- Do not block other agents by changing inference code paths

---

## Outputs (Must Create)

pipeline/
├── drift_detection/
│ ├── data_validator.py
│ └── drift_report_schema.json
├── validation/
│ ├── fairness_indicators.py
│ └── performance_thresholds.yaml
└── tests/
├── test_drift_detector.py
├── test_retraining_trigger.py
└── test_fairness.py
.github/workflows/
└── tfx-ci.yml
docs/
└── mlops/
├── drift_detection.md
├── retraining_triggers.md
└── fairness.md
shared_context/
└── pipeline_status.json

text

---

## Task 2.1 — Create Directories

```bash
mkdir -p pipeline/{drift_detection,validation,tests}
mkdir -p docs/mlops
mkdir -p .github/workflows
Update shared_context/CTX_SYNC.md:

AG-02 status → 🔄 In Progress
task → Task 2.1
Task 2.2 — Drift Detection (TFDV) – Local-Compatible
Create: pipeline/drift_detection/data_validator.py

Goal: Provide a library + CLI to:

infer schema from reference/training data
validate new data against schema
compute drift statistics
output JSON report
Important: Because we do not know your dataset format, implement a pluggable loader:

If TFRecords exist → use TFDV directly
Else → allow “SKIPPED: unsupported format” cleanly
Python

# pipeline/drift_detection/data_validator.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from pathlib import Path
import json

@dataclass
class DriftReport:
    status: str  # "ok" | "drift_detected" | "skipped" | "error"
    message: str
    drift_score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class DataDriftDetector:
    """
    Drift detection using TensorFlow Data Validation (TFDV).
    This module must degrade gracefully if data format is not supported.
    """

    def __init__(self, schema_path: str):
        self.schema_path = Path(schema_path)

    def detect_drift(self, new_data_path: str) -> DriftReport:
        new_path = Path(new_data_path)
        if not self.schema_path.exists():
            return DriftReport(
                status="error",
                message=f"Schema file not found at {self.schema_path}"
            )
        if not new_path.exists():
            return DriftReport(
                status="error",
                message=f"New data not found at {new_path}"
            )

        try:
            import tensorflow_data_validation as tfdv
            from tensorflow_metadata.proto.v0 import schema_pb2

            schema = schema_pb2.Schema()
            schema.ParseFromString(self.schema_path.read_bytes())

            # NOTE: This expects TFRecord/TFExample format.
            # If your dataset differs, the function returns "skipped".
            if not str(new_path).endswith((".tfrecord", ".tfrecords")):
                return DriftReport(
                    status="skipped",
                    message="Drift detection skipped: non-TFRecord data format",
                    details={"path": str(new_path)}
                )

            stats = tfdv.generate_statistics_from_tfrecord(
                data_location=str(new_path)
            )

            anomalies = tfdv.validate_statistics(
                statistics=stats,
                schema=schema
            )

            # Simple drift score placeholder: count anomalies
            anomaly_count = len(anomalies.anomaly_info)
            drift_score = float(anomaly_count)

            status = "ok" if anomaly_count == 0 else "drift_detected"
            msg = "No drift detected" if anomaly_count == 0 else f"Drift/anomalies detected: {anomaly_count}"

            return DriftReport(
                status=status,
                message=msg,
                drift_score=drift_score,
                details={"anomaly_info": {k: str(v) for k, v in anomalies.anomaly_info.items()}}
            )

        except ImportError:
            return DriftReport(
                status="skipped",
                message="TFDV not installed. Install tensorflow-data-validation to enable drift detection."
            )
        except Exception as e:
            return DriftReport(status="error", message=str(e))

def save_report(report: DriftReport, output_path: str) -> None:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(asdict(report), indent=2))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True)
    parser.add_argument("--new_data", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    detector = DataDriftDetector(args.schema)
    rep = detector.detect_drift(args.new_data)
    save_report(rep, args.out)
    print(rep.status, rep.message)
Task 2.3 — Define Retraining Triggers (Threshold Policy)
Create: pipeline/validation/performance_thresholds.yaml

YAML

thresholds:
  accuracy_min: 0.85
  drift_score_max: 0.3
  false_positive_rate_max_delta: 0.10

actions:
  on_accuracy_breach: "trigger_retrain"
  on_drift_breach: "trigger_retrain"
  on_fp_rate_breach: "alert_only"
Create: pipeline/validation/retraining_trigger.py

Python

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import yaml
from pathlib import Path

@dataclass
class TriggerDecision:
    should_retrain: bool
    reason: str
    details: Dict[str, Any]

class RetrainingTrigger:
    def __init__(self, thresholds_path: str):
        self.thresholds_path = Path(thresholds_path)
        self.thresholds = yaml.safe_load(self.thresholds_path.read_text())

    def evaluate(self, metrics: Dict[str, Any]) -> TriggerDecision:
        """
        metrics example:
          {"accuracy": 0.83, "drift_score": 0.4, "false_positive_rate_delta": 0.02}
        """
        t = self.thresholds["thresholds"]
        reasons = []
        should = False

        acc = metrics.get("accuracy")
        drift = metrics.get("drift_score")
        fp_delta = metrics.get("false_positive_rate_delta")

        if acc is not None and acc < t["accuracy_min"]:
            should = True
            reasons.append(f"accuracy {acc} < {t['accuracy_min']}")

        if drift is not None and drift > t["drift_score_max"]:
            should = True
            reasons.append(f"drift_score {drift} > {t['drift_score_max']}")

        if fp_delta is not None and fp_delta > t["false_positive_rate_max_delta"]:
            reasons.append(f"false_positive_rate_delta {fp_delta} > {t['false_positive_rate_max_delta']} (alert)")

        if not reasons:
            return TriggerDecision(False, "No triggers activated", metrics)

        return TriggerDecision(should, "; ".join(reasons), metrics)
Task 2.4 — Fairness Indicators (Graceful Skip)
Create: pipeline/validation/fairness_indicators.py

Rule: If demographic fields are missing, return "skipped".

Python

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import json
from pathlib import Path

@dataclass
class FairnessReport:
    status: str  # "ok"|"skipped"|"error"
    message: str
    metrics: Optional[Dict[str, Any]] = None

def compute_fairness(y_true, y_pred, demographics: Optional[Dict[str, Any]]) -> FairnessReport:
    if not demographics:
        return FairnessReport(status="skipped", message="No demographic metadata provided")

    try:
        # Placeholder: implement demographic parity / equalized odds if data exists
        # Keep minimal until confirmed dataset contains these fields.
        return FairnessReport(
            status="ok",
            message="Fairness metrics computed",
            metrics={"note": "Implement demographic parity and equalized odds once demographic schema confirmed"}
        )
    except Exception as e:
        return FairnessReport(status="error", message=str(e))

def save_report(report: FairnessReport, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(asdict(report), indent=2))
Task 2.5 — Pipeline Tests
Create pipeline/tests/test_drift_detector.py, test_retraining_trigger.py, test_fairness.py (simple unit tests validating skip behavior and decisions).

Task 2.6 — CI Workflow (Minimal)
Create .github/workflows/tfx-ci.yml that:

installs dependencies
runs pipeline tests
does not require GPU
Task 2.7 — Update shared_context
Create shared_context/pipeline_status.json after finishing:

JSON

{
  "agent": "AG-02",
  "status": "complete",
  "outputs": [
    "pipeline/drift_detection/data_validator.py",
    "pipeline/validation/retraining_trigger.py",
    "pipeline/validation/fairness_indicators.py",
    ".github/workflows/tfx-ci.yml"
  ],
  "notes": "Drift detection is TFRecord-based; non-TFRecord datasets are skipped gracefully."
}
Verification Checklist
 python pipeline/drift_detection/data_validator.py --schema ... runs
 retraining trigger returns correct decision for sample metrics
 fairness indicators skip gracefully if no demographics
 CI workflow runs pipeline tests
Update shared_context/CTX_SYNC.md and handoff notes to AG-07 and AG-09.
```

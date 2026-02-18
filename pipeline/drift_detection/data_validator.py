from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from pathlib import Path
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    status: str  # "ok" | "drift_detected" | "skipped" | "error"
    message: str
    drift_score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class DataDriftDetector:
    """
    Drift detection using TensorFlow Data Validation (TFDV).
    This module degrades gracefully if data format is not supported or TFDV is missing.
    """

    def __init__(self, schema_path: str):
        self.schema_path = Path(schema_path)

    def detect_drift(self, new_data_path: str) -> DriftReport:
        new_path = Path(new_data_path)

        # 1. Basic Validation
        if not self.schema_path.exists():
            return DriftReport(
                status="error", message=f"Schema file not found at {self.schema_path}"
            )
        if not new_path.exists():
            return DriftReport(
                status="error", message=f"New data not found at {new_path}"
            )

        # 2. Try TFDV Import
        try:
            import tensorflow_data_validation as tfdv
            from tensorflow_metadata.proto.v0 import schema_pb2
        except ImportError:
            logger.warning(
                "tensorflow-data-validation not installed. Skipping drift detection."
            )
            return DriftReport(
                status="skipped",
                message="TFDV not installed. Install tensorflow-data-validation to enable drift detection.",
            )

        try:
            # 3. Load Schema
            schema = schema_pb2.Schema()
            schema.ParseFromString(self.schema_path.read_bytes())

            # 4. Validate Data Format (TFDV works best with TFRecords)
            # We check extension or try to load.
            if not str(new_path).endswith((".tfrecord", ".tfrecords", ".gz")):
                # Fallback: Could try to load CSV if supported, but for now stick to strictly defined formats
                return DriftReport(
                    status="skipped",
                    message="Drift detection skipped: non-TFRecord data format (only .tfrecord supported currently)",
                    details={"path": str(new_path)},
                )

            # 5. Compute Statistics
            stats = tfdv.generate_statistics_from_tfrecord(data_location=str(new_path))

            # 6. Validate against Schema
            anomalies = tfdv.validate_statistics(statistics=stats, schema=schema)

            # 7. Analyze Anomalies
            anomaly_count = len(anomalies.anomaly_info)
            # Simple drift score is just the count of anomalies for now
            drift_score = float(anomaly_count)

            if anomaly_count == 0:
                status = "ok"
                msg = "No drift detected"
            else:
                status = "drift_detected"
                msg = f"Drift/anomalies detected: {anomaly_count}"

            # Convert anomaly info to dict
            anomaly_details = {
                k: str(v.description) for k, v in anomalies.anomaly_info.items()
            }

            return DriftReport(
                status=status,
                message=msg,
                drift_score=drift_score,
                details={"anomaly_info": anomaly_details},
            )

        except Exception as e:
            logger.exception("Error during drift detection")
            return DriftReport(status="error", message=str(e))


def save_report(report: DriftReport, output_path: str) -> None:
    """Saves the drift report to a JSON file."""
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(asdict(report), f, indent=2)
        logger.info(f"Drift report saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save drift report: {e}")


if __name__ == "__main__":
    import argparse
    import sys

    # Setup basic logging to stdout
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Run drift detection on a dataset using a TFDV schema."
    )
    parser.add_argument("--schema", required=True, help="Path to TFDV schema file")
    parser.add_argument("--new_data", required=True, help="Path to new data (TFRecord)")
    parser.add_argument("--out", required=True, help="Output path for JSON report")

    args = parser.parse_args()

    detector = DataDriftDetector(args.schema)
    report = detector.detect_drift(args.new_data)
    save_report(report, args.out)

    print(f"Status: {report.status}")
    print(f"Message: {report.message}")

    # Exit with error code if drift detected or error
    if report.status in ("error", "drift_detected"):
        sys.exit(1)
    sys.exit(0)

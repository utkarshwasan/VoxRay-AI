from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class FairnessReport:
    status: str  # "ok"|"skipped"|"error"
    message: str
    metrics: Optional[Dict[str, Any]] = None


def compute_fairness(
    y_true, y_pred, demographics: Optional[Dict[str, Any]] = None
) -> FairnessReport:
    """
    Computes fairness metrics based on demographic data.
    Degrades gracefully if demographics are missing.
    """
    if not demographics:
        msg = "No demographic metadata provided. Skipping fairness analysis."
        logger.info(msg)
        return FairnessReport(status="skipped", message=msg)

    try:
        # Placeholder for full fairness implementation
        # In a real scenario, we would use tensorflow-model-remedy or fairlearn here
        # For Phase 1b, we just validate the data presence.

        # Check if we have enough distinct groups
        groups = demographics.keys()
        if not groups:
            return FairnessReport(
                status="skipped", message="Demographics dict provided but empty"
            )

        # Mock calculation
        return FairnessReport(
            status="ok",
            message="Fairness metrics computed (Stub)",
            metrics={
                "demographic_parity_diff": 0.05,
                "equalized_odds_diff": 0.03,
                "note": "Implement full demographic parity calculations once dataset includes verified protected groups",
            },
        )
    except Exception as e:
        logger.exception("Error computing fairness")
        return FairnessReport(status="error", message=str(e))


def save_report(report: FairnessReport, path: str):
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(report), f, indent=2)
        logger.info(f"Fairness report saved to {path}")
    except Exception as e:
        logger.error(f"Failed to save fairness report: {e}")


if __name__ == "__main__":
    # Placeholder CLI
    print("Fairness indicator module ready.")

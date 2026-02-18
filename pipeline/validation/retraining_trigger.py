from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class TriggerDecision:
    should_retrain: bool
    reason: str
    details: Dict[str, Any]


class RetrainingTrigger:
    """
    Evaluates new performance metrics against defined thresholds
    to decide if retraining is necessary.
    """

    def __init__(self, thresholds_path: str):
        self.thresholds_path = Path(thresholds_path)
        if not self.thresholds_path.exists():
            raise FileNotFoundError(
                f"Thresholds file not found at {self.thresholds_path}"
            )

        try:
            self.config = yaml.safe_load(self.thresholds_path.read_text())
            self.thresholds = self.config.get("thresholds", {})
        except Exception as e:
            logger.error(f"Failed to load thresholds: {e}")
            raise

    def evaluate(self, metrics: Dict[str, Any]) -> TriggerDecision:
        """
        Evaluates current metrics against thresholds.

        metrics example:
          {"accuracy": 0.83, "drift_score": 0.4, "false_positive_rate_delta": 0.02}
        """
        reasons: List[str] = []
        should_retrain = False

        # 1. Accuracy Check
        accuracy = metrics.get("accuracy")
        min_acc = self.thresholds.get("accuracy_min")
        if accuracy is not None and min_acc is not None:
            if accuracy < min_acc:
                should_retrain = True
                reasons.append(f"accuracy {accuracy:.4f} < {min_acc}")

        # 2. Drift Score Check
        drift = metrics.get("drift_score")
        max_drift = self.thresholds.get("drift_score_max")
        if drift is not None and max_drift is not None:
            if drift > max_drift:
                should_retrain = True
                reasons.append(f"drift_score {drift} > {max_drift}")

        # 3. False Positive Rate Delta Check (Alert only?)
        # Logic depends on 'actions' config, but for now we hardcode the logic
        # based on standard MLOps patterns or the config if we were parsing actions fully.
        fp_delta = metrics.get("false_positive_rate_delta")
        max_fp_delta = self.thresholds.get("false_positive_rate_max_delta")
        if fp_delta is not None and max_fp_delta is not None:
            if fp_delta > max_fp_delta:
                # We might not trigger retrain immediately for FP spike, but we definitely note it.
                # If the policy says on_fp_rate_breach: "alert_only", we won't set should_retrain=True
                # unless we decide to override.
                # Let's check config actions if available
                actions = self.config.get("actions", {})
                action = actions.get("on_fp_rate_breach", "alert_only")

                msg = f"false_positive_rate_delta {fp_delta:.4f} > {max_fp_delta} ({action})"
                reasons.append(msg)

                if action == "trigger_retrain":
                    should_retrain = True

        if not reasons:
            return TriggerDecision(False, "No triggers activated", metrics)

        return TriggerDecision(should_retrain, "; ".join(reasons), metrics)


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--thresholds", required=True)
    parser.add_argument("--metrics", required=True, help="JSON string of metrics")
    args = parser.parse_args()

    import json

    metrics = json.loads(args.metrics)

    trigger = RetrainingTrigger(args.thresholds)
    decision = trigger.evaluate(metrics)

    print(f"Retrain: {decision.should_retrain}")
    print(f"Reason: {decision.reason}")

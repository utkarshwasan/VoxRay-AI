from typing import Optional, Dict


class ClinicalBenchmarks:
    """
    Provides static benchmark data for comparison with model predictions.
    This is heuristic and for contextualization only.
    """

    # Benchmarks keyed by simplified condition names
    BENCHMARKS: Dict[str, Dict[str, float]] = {
        "pneumonia": {
            "radiologist_avg_sensitivity": 0.85,
            "radiologist_avg_specificity": 0.90,
            "sota_ai_auc": 0.96,
        },
        "lung_cancer": {
            "radiologist_avg_sensitivity": 0.78,
            "radiologist_avg_specificity": 0.92,
            "sota_ai_auc": 0.94,
        },
        # Extend as needed
    }

    # Mapping from VoxRay class labels to simplified conditions
    CLASS_TO_CONDITION: Dict[str, str] = {
        "03_NORMAL_PNEUMONIA": "pneumonia",
        "06_PNEUMONIA": "pneumonia",
        "04_LUNG_CANCER": "lung_cancer",
    }

    @classmethod
    def get_condition_for_label(cls, class_label: str) -> Optional[str]:
        return cls.CLASS_TO_CONDITION.get(class_label)

    @classmethod
    def get_benchmark(cls, condition_name: str) -> Optional[Dict[str, float]]:
        return cls.BENCHMARKS.get(condition_name.lower())

    @classmethod
    def compare_score(cls, class_label: str, confidence_score: float) -> str:
        """
        Returns a qualitative string comparing the confidence score
        to approximate benchmarks for the mapped condition.

        Args:
            class_label: VoxRay class label, e.g. "06_PNEUMONIA"
            confidence_score: model confidence in [0,1]

        Returns:
            Human-readable comparison string.
        """
        condition = cls.get_condition_for_label(class_label)
        if not condition:
            return "No benchmark mapping available for this class."

        bm = cls.get_benchmark(condition)
        if not bm:
            return "No benchmark data available."

        threshold = bm["radiologist_avg_sensitivity"]

        if confidence_score >= threshold:
            return "Model confidence meets or exceeds typical radiologist sensitivity."
        elif confidence_score >= max(0.0, threshold - 0.1):
            return "Model confidence approaches typical radiologist sensitivity."
        else:
            return (
                "Model confidence is below typical screening thresholds; "
                "human review is strongly recommended."
            )

import os
import io
import logging
from typing import Dict, Any, List, Optional

import numpy as np
from PIL import Image

# Lazy load placeholders
tf = None
MedicalEnsemble = None
predict_with_uncertainty = None
ClinicalBenchmarks = None

logger = logging.getLogger(__name__)


class ModelServer:
    """
    Central model server for VoxRay AI.

    - Loads one or more Keras models into an ensemble.
    - Provides unified prediction and optional MC Dropout uncertainty.
    """

    _instance: Optional["ModelServer"] = None

    # VoxRay class labels (consistent with backend/api/main.py)
    CLASS_NAMES: List[str] = [
        "01_NORMAL_LUNG",
        "02_NORMAL_BONE",
        "03_NORMAL_PNEUMONIA",
        "04_LUNG_CANCER",
        "05_FRACTURED",
        "06_PNEUMONIA",
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelServer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.ensemble: Optional[Any] = (
            None  # Typed as Any to avoid import error in type hint
        )
        self._initialize()
        self._initialized = True

    def _initialize(self):
        """Load models and prepare ensemble."""
        # Lazy load dependencies
        global tf, MedicalEnsemble, predict_with_uncertainty, ClinicalBenchmarks
        try:
            import tensorflow as _tf
            from backend.models.ensemble.ensemble_model import MedicalEnsemble as _ME
            from backend.models.uncertainty.mc_dropout import (
                predict_with_uncertainty as _pwu,
            )
            from backend.models.benchmarks.clinical_benchmarks import (
                ClinicalBenchmarks as _CB,
            )

            tf = _tf
            MedicalEnsemble = _ME
            predict_with_uncertainty = _pwu
            ClinicalBenchmarks = _CB
        except ImportError as e:
            logger.error(f"[ModelServer] Failed to load ML dependencies: {e}")
            self.ensemble = None
            return

        # Adjust base path relative to this file or CWD
        # Assuming CWD is project root
        base_path = os.path.join("backend", "models")

        # Primary model (existing v1 model)
        candidate_paths = [
            os.path.join(base_path, "medical_model_final.keras"),
            # Add additional ensemble members here in future, if present:
            # os.path.join(base_path, "medical_model_variant.keras"),
        ]

        valid_paths = [p for p in candidate_paths if os.path.exists(p)]

        if not valid_paths:
            logger.error(
                "[ModelServer] No valid model files found in backend/models/. "
                "Prediction will not be available."
            )
            self.ensemble = None
            return

        try:
            self.ensemble = MedicalEnsemble(valid_paths)
            logger.info(
                f"[ModelServer] Ensemble initialized with {len(valid_paths)} model(s)."
            )
        except Exception as e:
            logger.error(f"[ModelServer] Failed to initialize ensemble: {e}")
            self.ensemble = None

    def preprocess_image(
        self, image_bytes: bytes, target_size=(224, 224)
    ) -> np.ndarray:
        """
        Convert raw bytes to tensor using the SAME preprocessing as v1.

        v1 main.py logic:
          - open as RGB
          - resize to (224, 224)
          - np.float32
          - keras.applications.resnet_v2.preprocess_input
          - expand dims
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid image file: {e}")

        image = image.resize(target_size)
        img_arr = np.array(image).astype(np.float32)

        # Lazy load if needed (though _initialize should have triggered tf load)
        if tf is None:
            import tensorflow as tf

        from tensorflow.keras.applications.resnet_v2 import preprocess_input

        img_preprocessed = preprocess_input(img_arr)
        img_batch = np.expand_dims(img_preprocessed, axis=0)  # (1, 224, 224, 3)
        return img_batch

    def predict(
        self, image_bytes: bytes, run_uncertainty: bool = False
    ) -> Dict[str, Any]:
        """
        Predict class, confidence, and optionally uncertainty.

        Args:
            image_bytes: Raw image bytes
            run_uncertainty: Whether to run MC Dropout (slower)

        Returns:
            Dict with:
                - diagnosis (class label)
                - confidence (float)
                - probabilities (mapping class->prob)
                - ensemble (if multiple models)
                - uncertainty (if requested)
                - benchmark_comparison (string)
        """
        if self.ensemble is None:
            return {"error": "ModelServer not initialized: no ensemble models loaded."}

        # 1. Preprocess
        tensor = self.preprocess_image(image_bytes)

        # 2. Ensemble prediction
        ensemble_result = self.ensemble.predict(tensor)
        probs = np.array(ensemble_result["mean_probability"])
        if probs.shape[0] != len(self.CLASS_NAMES):
            logger.warning(
                f"[ModelServer] Probability vector length {probs.shape[0]} "
                f"!= number of classes {len(self.CLASS_NAMES)}"
            )

        n_classes = min(len(self.CLASS_NAMES), probs.shape[0])
        probs = probs[:n_classes]
        class_names = self.CLASS_NAMES[:n_classes]

        top_idx = int(np.argmax(probs))
        diagnosis = class_names[top_idx]
        confidence = float(probs[top_idx])

        response: Dict[str, Any] = {
            "diagnosis": diagnosis,
            "confidence": confidence,
            "probabilities": {cls: float(p) for cls, p in zip(class_names, probs)},
            "ensemble": {
                "model_count": ensemble_result["model_count"],
                "variance": ensemble_result["variance"][:n_classes],
                "individual_predictions": [
                    pred[:n_classes]
                    for pred in ensemble_result["individual_predictions"]
                ],
            },
        }

        # 3. Optional MC Dropout uncertainty
        if run_uncertainty and self.ensemble.models:
            try:
                mc = predict_with_uncertainty(self.ensemble.models[0], tensor)
                mc_probs = np.array(mc["mean_probability"])[:n_classes]
                response["uncertainty"] = {
                    "entropy": mc["entropy"],
                    "epistemic_variance": mc["uncertainty_variance"][:n_classes],
                    "mean_probability": mc_probs.tolist(),
                }
            except Exception as e:
                logger.error(f"[ModelServer] MC Dropout failed: {e}")

        # 4. Benchmark comparison (heuristic)
        try:
            bench_msg = ClinicalBenchmarks.compare_score(diagnosis, confidence)
            response["benchmark_comparison"] = bench_msg
        except Exception as e:
            logger.error(f"[ModelServer] Benchmark comparison failed: {e}")

        return response

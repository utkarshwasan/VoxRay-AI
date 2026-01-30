# AG-01: Model Architect (Core AI Logic & Model Serving)

**Agent ID:** AG-01  
**Role:** Core AI Logic, Ensembling, Uncertainty, Benchmarks, Model Server  
**Phase:** 1  
**Duration:** Days 3–7  
**Dependencies:**

- AG-00 (MigrationLead) MUST have passed Quality Gate 0 (feature flags + versioning in place)

---

## 1. Mission

Upgrade the model serving stack for VoxRay AI v2.0 without breaking v1:

- Add an **ensemble wrapper** around existing and optional models.
- Add **Monte Carlo Dropout** for uncertainty estimation.
- Add **clinical benchmark comparison** for context.
- Add a centralized **ModelServer** class.
- Implement `/v2/predict/image` that uses this enhanced logic and is **feature-flag gated**.

**DO NOT**:

- Change v1 `/predict/image` behavior or response shape.
- Modify `backend/models/medical_model_final.keras`.
- Break current class mapping:  
  `["01_NORMAL_LUNG", "02_NORMAL_BONE", "03_NORMAL_PNEUMONIA", "04_LUNG_CANCER", "05_FRACTURED", "06_PNEUMONIA"]`.

---

## 2. Required Reading

Before coding, read:

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/02_QUALITY_GATES.md` (Gate 1)
- `Implementation_v2/SHARED/03_API_CONTRACTS.md` (v2 prediction contract)
- `Implementation_v2/SHARED/06_FEATURE_FLAGS.md`
- `shared_context/CTX_SYNC.md` (to confirm AG-00 work is done)

---

## 3. Directory Setup

Run:

```bash
mkdir -p backend/models/ensemble
mkdir -p backend/models/uncertainty
mkdir -p backend/models/benchmarks
mkdir -p backend/serving
```

Update `shared_context/CTX_SYNC.md`:

- AG-01 status → 🔄 In Progress
- Current task → "Task 1: Directory setup"

---

## 4. Ensemble Wrapper

**File:** `backend/models/ensemble/ensemble_model.py`

This ensemble:

- Accepts a list of Keras model paths.
- Loads all that exist.
- Returns:
  - `mean_probability` (list[float])
  - `variance` (per-class variance across models)
  - `individual_predictions` (list of per-model logits/probs)
  - `model_count`

```python
import os
import logging
from typing import List, Dict, Any

import numpy as np
import tensorflow as tf

logger = logging.getLogger(__name__)


class MedicalEnsemble:
    """
    Ensemble wrapper for one or more Keras models.

    - If only one model is provided, it behaves as a single-model wrapper.
    - If multiple models are provided, predictions are averaged (soft voting).
    """

    def __init__(self, model_paths: List[str]):
        """
        Initialize the ensemble with a list of file paths to .keras models.

        Args:
            model_paths: A list of filesystem paths to Keras model files.
        """
        self.models: List[tf.keras.Model] = []
        self.model_names: List[str] = []

        for path in model_paths:
            if os.path.exists(path):
                try:
                    logger.info(f"[Ensemble] Loading model from {path} ...")
                    model = tf.keras.models.load_model(path)
                    # Basic sanity: expect output shape (_, 6) for VoxRay classes
                    if len(model.output_shape) != 2 or model.output_shape[1] != 6:
                        logger.warning(
                            f"[Ensemble] Model at {path} has unexpected output shape "
                            f"{model.output_shape}. Expected (_, 6). Including anyway."
                        )
                    self.models.append(model)
                    self.model_names.append(os.path.basename(path))
                    logger.info(f"[Ensemble] Successfully loaded: {path}")
                except Exception as e:
                    logger.error(f"[Ensemble] Failed to load model {path}: {e}")
            else:
                logger.warning(f"[Ensemble] Model path not found, skipping: {path}")

        if not self.models:
            raise RuntimeError(
                "MedicalEnsemble initialization failed: no valid model paths found."
            )

        logger.info(
            f"[Ensemble] Initialized with {len(self.models)} model(s): {self.model_names}"
        )

    def predict(self, image_tensor: np.ndarray) -> Dict[str, Any]:
        """
        Run inference across all loaded models and average the results.

        Args:
            image_tensor: Preprocessed input of shape (1, H, W, C).

        Returns:
            dict containing:
                - mean_probability: list[float] of class probabilities
                - variance: list[float] variance across models
                - individual_predictions: list[list[float]]
                - model_count: int
        """
        if image_tensor.ndim != 4 or image_tensor.shape[0] != 1:
            raise ValueError(
                f"Expected image_tensor with shape (1, H, W, C), got {image_tensor.shape}"
            )

        predictions = []

        for i, model in enumerate(self.models):
            try:
                pred = model.predict(image_tensor, verbose=0)
                if pred.shape[0] != 1:
                    logger.warning(
                        f"[Ensemble] Model {self.model_names[i]} returned "
                        f"unexpected batch shape {pred.shape}, expected (1, num_classes)."
                    )
                predictions.append(pred)
            except Exception as e:
                logger.error(
                    f"[Ensemble] Prediction failed for model {self.model_names[i]}: {e}"
                )

        if not predictions:
            raise RuntimeError("No successful predictions from any ensemble member")

        predictions_arr = np.array(predictions)  # (num_models, 1, num_classes)
        mean_prediction = np.mean(predictions_arr, axis=0)  # (1, num_classes)
        variance = np.var(predictions_arr, axis=0)  # (1, num_classes)

        return {
            "mean_probability": mean_prediction[0].tolist(),
            "variance": variance[0].tolist(),
            "individual_predictions": [p[0].tolist() for p in predictions_arr],
            "model_count": len(self.models),
        }
```

---

## 5. MC Dropout Uncertainty

**File:** `backend/models/uncertainty/mc_dropout.py`

This uses `model(image_tensor, training=True)` to activate Dropout.

```python
import numpy as np
import tensorflow as tf
from typing import Dict, Any


def predict_with_uncertainty(
    model: tf.keras.Model,
    image_tensor: np.ndarray,
    num_iterations: int = 10,
) -> Dict[str, Any]:
    """
    Performs Monte Carlo Dropout inference.

    Args:
        model: The Keras model.
        image_tensor: Preprocessed image input of shape (1, H, W, C).
        num_iterations: Number of forward passes to run.

    Returns:
        dict:
            mean_probability: list[float]
            uncertainty_variance: list[float]
            entropy: float
            samples: list[list[float]]
    """
    if num_iterations < 2:
        raise ValueError("num_iterations must be >= 2 for MC Dropout")

    if image_tensor.ndim != 4 or image_tensor.shape[0] != 1:
        raise ValueError(
            f"Expected image_tensor with shape (1, H, W, C), got {image_tensor.shape}"
        )

    predictions = []

    for _ in range(num_iterations):
        # Force training=True to enable Dropout layers during "inference"
        pred = model(image_tensor, training=True)
        preds_np = pred.numpy()
        predictions.append(preds_np)

    predictions_arr = np.array(predictions)  # (num_iterations, 1, num_classes)

    # Average across iterations
    mean_prediction = np.mean(predictions_arr, axis=0)  # (1, num_classes)

    # Variance across iterations (epistemic proxy)
    uncertainty_variance = np.var(predictions_arr, axis=0)  # (1, num_classes)

    # Entropy of mean distribution
    epsilon = 1e-15
    mean_prob_safe = np.clip(mean_prediction, epsilon, 1.0)
    entropy = -np.sum(mean_prob_safe * np.log(mean_prob_safe), axis=-1)  # (1,)

    return {
        "mean_probability": mean_prediction[0].tolist(),
        "uncertainty_variance": uncertainty_variance[0].tolist(),
        "entropy": float(entropy[0]),
        "samples": predictions_arr[:, 0, :].tolist(),
    }
```

---

## 6. Clinical Benchmarks

**File:** `backend/models/benchmarks/clinical_benchmarks.py`

Maps VoxRay class labels → simplified conditions for context.

```python
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
```

---

## 7. Model Server

**File:** `backend/serving/model_server.py`

This centralizes:

- Model loading (one or more Keras files).
- Preprocessing (aligned with v1: ResNetV2 `preprocess_input`).
- Prediction / ensemble / MC dropout / benchmarks.

```python
import os
import io
import logging
from typing import Dict, Any, List, Optional

import numpy as np
import tensorflow as tf
from PIL import Image

from backend.models.ensemble.ensemble_model import MedicalEnsemble
from backend.models.uncertainty.mc_dropout import predict_with_uncertainty
from backend.models.benchmarks.clinical_benchmarks import ClinicalBenchmarks

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
        self.ensemble: Optional[MedicalEnsemble] = None
        self._initialize()
        self._initialized = True

    def _initialize(self):
        """Load models and prepare ensemble."""
        base_path = "backend/models"
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

    def preprocess_image(self, image_bytes: bytes, target_size=(224, 224)) -> np.ndarray:
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

        from tensorflow.keras.applications.resnet_v2 import preprocess_input
        img_preprocessed = preprocess_input(img_arr)
        img_batch = np.expand_dims(img_preprocessed, axis=0)  # (1, 224, 224, 3)
        return img_batch

    def predict(self, image_bytes: bytes, run_uncertainty: bool = False) -> Dict[str, Any]:
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
            "probabilities": {
                cls: float(p) for cls, p in zip(class_names, probs)
            },
            "ensemble": {
                "model_count": ensemble_result["model_count"],
                "variance": ensemble_result["variance"][:n_classes],
                "individual_predictions": [
                    pred[:n_classes] for pred in ensemble_result["individual_predictions"]
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
```

---

## 8. `/v2/predict/image` Route

**File (v2 router):** `backend/api/v2.py`

Integrate the v2 prediction route into your existing v2 router.

At the top of `backend/api/v2.py`, add:

```python
import logging
from fastapi import UploadFile, File, HTTPException, Query

from backend.serving.model_server import ModelServer
from backend.core.feature_flags import require_feature, FeatureFlag, feature_flags

logger = logging.getLogger(__name__)
model_server = ModelServer()
```

Then add or replace the `/predict/image` handler:

```python
@router.post("/predict/image")
@require_feature(FeatureFlag.ENSEMBLE_MODEL)
async def predict_image_v2(
    file: UploadFile = File(...),
    enable_uncertainty: bool = Query(
        False, description="Run MC Dropout uncertainty (slower)"
    ),
):
    """
    V2 prediction endpoint (ensemble + optional uncertainty).

    - Uses ModelServer (ensemble + MC Dropout).
    - Gated by FF_ENSEMBLE_MODEL.
    - Optional MC Dropout gated by FF_UNCERTAINTY_QUANTIFICATION.

    Does NOT change v1 behavior. v1 /predict/image remains as-is.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG or PNG is supported.",
        )

    if model_server.ensemble is None:
        logger.error("[v2] ModelServer ensemble not initialized.")
        raise HTTPException(
            status_code=503,
            detail="Ensemble model is not available.",
        )

    try:
        image_bytes = await file.read()

        run_uncertainty = bool(enable_uncertainty) and feature_flags.is_enabled(
            FeatureFlag.UNCERTAINTY_QUANTIFICATION
        )

        result = model_server.predict(image_bytes, run_uncertainty=run_uncertainty)

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "diagnosis": result["diagnosis"],
            "confidence": result["confidence"],
            "uncertainty": result.get("uncertainty"),
            "ensemble": result.get("ensemble"),
            "benchmark_comparison": result.get("benchmark_comparison"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[v2] Error in /v2/predict/image: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal Server Error during prediction."
        )
```

> **Note:** This route assumes AG-00 has:
>
> - Created `backend/api/v2.py` with `router = APIRouter()`
> - Wired v2 router with `setup_versioning(app)` in `backend/api/main.py`.

---

## 9. Verification & Quality Gate 1 Preparation

Run:

```bash
# 1. Existing v1 behavior must still pass
pytest tests/migration/test_backward_compatibility.py -v

# 2. (Optional) Add unit tests for ensemble + MC dropout later with AG-08
```

Update `shared_context/AG-01_status.json` and `shared_context/CTX_SYNC.md` with:

- List of files created:
  - `backend/models/ensemble/ensemble_model.py`
  - `backend/models/uncertainty/mc_dropout.py`
  - `backend/models/benchmarks/clinical_benchmarks.py`
  - `backend/serving/model_server.py`
  - Updated `backend/api/v2.py` route `/v2/predict/image`
- Known behavior:
  - Uses existing `medical_model_final.keras`
  - Uses same preprocessing as v1
  - Feature-gated via `FF_ENSEMBLE_MODEL`, `FF_UNCERTAINTY_QUANTIFICATION`

When this is done and tested, you’re ready to proceed toward Quality Gate 1.

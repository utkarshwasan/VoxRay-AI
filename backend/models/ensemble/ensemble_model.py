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
                    # Note: TensorShape objects comparison might differ, so we access tuple
                    output_shape = model.output_shape
                    # output_shape is usually a tuple like (None, 6)
                    if (
                        not output_shape
                        or len(output_shape) != 2
                        or output_shape[1] != 6
                    ):
                        logger.warning(
                            f"[Ensemble] Model at {path} has unexpected output shape "
                            f"{output_shape}. Expected (_, 6). Including anyway."
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

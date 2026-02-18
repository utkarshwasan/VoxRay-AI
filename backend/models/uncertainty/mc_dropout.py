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

import tensorflow as tf
import numpy as np
from PIL import Image
from tensorflow.keras.applications.resnet_v2 import preprocess_input
import sys

# Load model
print("Loading model...")
model = tf.keras.models.load_model('models/medical_model_final.keras')
print(f"Model loaded. Output shape: {model.output_shape}")

# Class names (update these if different)
CLASS_NAMES = [
    "01_NORMAL_LUNG",
    "02_NORMAL_BONE",
    "03_NORMAL_PNEUMONIA",
    "04_LUNG_CANCER",
    "05_FRACTURED",
    "06_PNEUMONIA"
]

if len(sys.argv) < 2:
    print("Usage: python test_prediction.py <image_path>")
    sys.exit(1)

image_path = sys.argv[1]
print(f"\nTesting with image: {image_path}")

# Load and preprocess image
img = Image.open(image_path).convert("RGB")
img = img.resize((224, 224))
img_arr = np.array(img).astype(np.float32)

print(f"Image array shape: {img_arr.shape}")
print(f"Image array range before preprocessing: {img_arr.min():.2f} to {img_arr.max():.2f}")

img_preprocessed = preprocess_input(img_arr)
print(f"Image array range after preprocessing: {img_preprocessed.min():.4f} to {img_preprocessed.max():.4f}")

img_batch = np.expand_dims(img_preprocessed, 0)

# Predict
print("\nPredicting...")
predictions = model.predict(img_batch, verbose=0)
probabilities = predictions[0]  # Already probabilities from model's softmax layer

print("\n📊 Prediction scores:")
for idx, (class_name, prob) in enumerate(zip(CLASS_NAMES, probabilities)):
    print(f"  {idx}: {class_name}: {float(prob)*100:.2f}%")

top_idx = np.argmax(probabilities)
print(f"\n✅ Top prediction: {CLASS_NAMES[top_idx]} ({float(probabilities[top_idx])*100:.1f}%)")

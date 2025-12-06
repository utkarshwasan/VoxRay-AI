import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.applications.resnet_v2 import ResNet50V2, preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.utils.class_weight import compute_class_weight
import os

# ==================== CONFIGURATION ====================
img_width, img_height = 224, 224
batch_size = 32

# ==================== UPDATED PATHS ====================
data_train_path = "consolidated_medical_data/train"
data_val_path = "consolidated_medical_data/val"
data_test_path = "consolidated_medical_data/test"
model_save_path = "models/medical_model_final.keras"
best_model_path = "models/best_model.keras"

if not os.path.exists(data_train_path):
    data_train_path = "consolidated_medical_data/train"
if not os.path.exists(data_val_path):
    data_val_path = "consolidated_medical_data/val"
if not os.path.exists(data_test_path):
    data_test_path = "consolidated_medical_data/test"

# ==================== PRE-TRAINING VERIFICATION ====================
print("🔍 Verifying data directories and class structure...")
for path, name in [(data_train_path, "Train"), (data_val_path, "Val"), (data_test_path, "Test")]:
    if not os.path.exists(path):
        print(f"❌ ERROR: {name} path does not exist: {path}")
        exit()
    classes = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
    image_count = sum([len(os.listdir(os.path.join(path, c))) for c in classes])
    print(f"  {name}: {len(classes)} classes, {image_count} images")

# ==================== DATA GENERATORS WITH AUGMENTATION ====================
print("\n📂 Creating data generators...")

train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
    zoom_range=0.1,
    shear_range=0.05,
    brightness_range=[0.9, 1.1],
    fill_mode='nearest'
)

val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=preprocess_input
)

train_generator = train_datagen.flow_from_directory(
    data_train_path,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='sparse',
    shuffle=True
)

val_generator = val_datagen.flow_from_directory(
    data_val_path,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='sparse',
    shuffle=False
)

# ==================== DYNAMIC CLASS DETECTION ====================
num_classes = train_generator.num_classes
print(f"\n✅ Detected {num_classes} classes from training data")

# ==================== CLASS WEIGHTS FOR IMBALANCE ====================
print("\n⚖️ Computing class weights...")
train_labels = train_generator.classes
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_labels),
    y=train_labels
)
class_weights_dict = dict(enumerate(class_weights))
print(f"Class weights: {class_weights_dict}")

# ==================== BUILD MODEL ====================
print("\n🧠 Building ResNet50V2 model...")

base_model = ResNet50V2(
    input_shape=(img_height, img_width, 3),
    include_top=False,
    weights='imagenet'
)

base_model.trainable = False  # Stage 1: Freeze base

model = Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(1e-4)),
    layers.BatchNormalization(),
    layers.Dense(num_classes, activation='softmax')
])

print(f"Total model parameters: {model.count_params():,}")

# ==================== CALLBACKS ====================
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-6, verbose=1),
    ModelCheckpoint(best_model_path, monitor='val_accuracy', save_best_only=True, verbose=1)
]

# ==================== STAGE 1: WARMUP ====================
print("\n🔥 STAGE 1: Training head (frozen base) - 10 epochs")
model.compile(
    optimizer=keras.optimizers.Adam(
        learning_rate=1e-4,
        clipnorm=1.0,
    ),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

history1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,
    class_weight=class_weights_dict,
    callbacks=callbacks,
    verbose=1
)

# ==================== STAGE 2: PARTIAL FINE-TUNING ====================
print("\n🔥 STAGE 2: Partial Fine-tuning (unfreezing top layers)")
base_model.trainable = True
for layer in base_model.layers:
    if isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
fine_tune_at = max(0, len(base_model.layers) - 40)
for layer in base_model.layers[:fine_tune_at]:
    if not isinstance(layer, tf.keras.layers.BatchNormalization):
        layer.trainable = False
model.summary()

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=5e-6),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

history2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=30,
    initial_epoch=len(history1.epoch),
    class_weight=class_weights_dict,
    callbacks=callbacks,
    verbose=1
)

# ==================== SAVE & EVALUATE ====================
model.save(model_save_path)
print(f"\n✅ Training complete! Final model saved to: {model_save_path}")

print("\n📊 Evaluating on test set...")
test_generator = val_datagen.flow_from_directory(
    data_test_path,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='sparse',
    shuffle=False
)

test_loss, test_accuracy = model.evaluate(test_generator)
print(f"Test Set Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")
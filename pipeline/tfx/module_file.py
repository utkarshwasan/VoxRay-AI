"""
TFX Module File for Medical Image Classification
Implements ResNet50V2 with Transfer Learning, Data Augmentation, and Two-Stage Training
"""

import os
import shutil
import tempfile
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications.resnet_v2 import ResNet50V2, preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

try:
    from tfx.components.trainer.fn_args_utils import FnArgs
except ImportError:
    # Dummy FnArgs for standalone verification when TFX is not installed
    class FnArgs:
        def __init__(self, train_files, eval_files, serving_model_dir, train_steps, eval_steps):
            self.train_files = train_files
            self.eval_files = eval_files
            self.serving_model_dir = serving_model_dir
            self.train_steps = train_steps
            self.eval_steps = eval_steps

# ==================== CLASS WEIGHTS ====================
CLASS_WEIGHTS = {
    0: 17.03003003003003,   # 01_NORMAL_LUNG
    1: 0.582537236774525,   # 02_NORMAL_BONE
    2: 1.7060770156438025,  # 03_NORMAL_PNEUMONIA
    3: 4.182153392330384,   # 04_LUNG_CANCER
    4: 0.5503153808830664,  # 05_FRACTURED
    5: 0.632007132508637    # 06_PNEUMONIA
}

NUM_CLASSES = 6
IMG_HEIGHT = 224
IMG_WIDTH = 224

# ==================== FEATURE SPEC ====================
_FEATURE_SPEC = {
    'image_raw': tf.io.FixedLenFeature([], tf.string),
    'label': tf.io.FixedLenFeature([], tf.int64),
}


def _parse_function(example_proto):
    """Parses a single tf.train.Example."""
    features = tf.io.parse_single_example(example_proto, _FEATURE_SPEC)
    
    # Decode image
    image = tf.io.decode_jpeg(features['image_raw'], channels=3)
    image = tf.image.resize(image, [IMG_HEIGHT, IMG_WIDTH])
    image = tf.cast(image, tf.float32)
    
    # Label
    label = features['label']
    
    return image, label


def _augment(image, label):
    """Data augmentation followed by preprocessing."""
    # Horizontal flip
    image = tf.image.random_flip_left_right(image)
    
    # Brightness adjustment
    image = tf.image.random_brightness(image, max_delta=0.2)
    
    # Contrast adjustment
    image = tf.image.random_contrast(image, lower=0.8, upper=1.2)
    
    # Zoom/Shift approximation via Random Crop + Resize
    image = tf.image.resize_with_crop_or_pad(image, 250, 250)
    image = tf.image.random_crop(image, size=[IMG_HEIGHT, IMG_WIDTH, 3])
    
    # Apply Preprocessing AFTER augmentation
    image = preprocess_input(image)
    
    return image, label


def _preprocess_val(image, label):
    """Helper for validation data: just preprocess, no augmentation."""
    image = preprocess_input(image)
    return image, label


def _input_fn(file_pattern, batch_size=32, is_train=True):
    """Generates features and label for training/evaluation."""
    files = tf.io.gfile.glob(file_pattern)
    compression_type = None
    
    if files:
        with tf.io.gfile.GFile(files[0], 'rb') as f:
            header = f.read(2)
            if header == b'\x1f\x8b':
                compression_type = 'GZIP'
    
    dataset = tf.data.TFRecordDataset(files, compression_type=compression_type)
    dataset = dataset.map(_parse_function, num_parallel_calls=tf.data.AUTOTUNE)
    
    # [Removed .cache() to prevent OOM errors on large dataset]
    # Reliability > Speed
    
    if is_train:
        # Train: Augment -> Preprocess
        dataset = dataset.map(_augment, num_parallel_calls=tf.data.AUTOTUNE)
        
        # Large shuffle buffer to prevent sorted-data bias
        dataset = dataset.shuffle(15000)
    else:
        # Val: Just Preprocess
        dataset = dataset.map(_preprocess_val, num_parallel_calls=tf.data.AUTOTUNE)
    
    dataset = dataset.batch(batch_size).repeat()
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset


def build_model():
    """Builds the ResNet50V2 model."""
    base_model = ResNet50V2(
        input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
        include_top=False,
        weights='imagenet'
    )
    
    base_model.trainable = False
    
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(1e-4)),
        layers.BatchNormalization(),
        layers.Dense(NUM_CLASSES, activation='softmax')
    ])
    
    return model


def run_fn(fn_args: FnArgs):
    """Train the model with two-stage training."""
    
    train_dataset = _input_fn(fn_args.train_files, is_train=True)
    eval_dataset = _input_fn(fn_args.eval_files, is_train=False)
    
    model = build_model()
    base_model = model.layers[0]
    
    # Callbacks
    # Ensure serving_model_dir exists for checkpoint
    if not os.path.exists(fn_args.serving_model_dir):
        os.makedirs(fn_args.serving_model_dir, exist_ok=True)
        
    checkpoint_path = os.path.join(fn_args.serving_model_dir, 'checkpoint.keras')
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-7, verbose=1),
        ModelCheckpoint(filepath=checkpoint_path, monitor='val_loss', save_best_only=True, verbose=1)
    ]
    
    # ==================== STAGE 1: WARMUP ====================
    print("\n" + "="*60)
    print("🔥 STAGE 1: Training head with frozen base (5 epochs)")
    print("="*60)
    
    base_model.trainable = False
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4, clipnorm=1.0),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    warmup_steps = max(fn_args.train_steps // 4, 10)
    eval_steps_stage1 = max(fn_args.eval_steps // 2, 5)
    
    model.fit(
        train_dataset,
        steps_per_epoch=warmup_steps,
        validation_data=eval_dataset,
        validation_steps=eval_steps_stage1,
        epochs=5,
        class_weight=CLASS_WEIGHTS,
        callbacks=callbacks,
        verbose=1
    )
    
    # ==================== STAGE 2: FINE-TUNING ====================
    print("\n" + "="*60)
    print("🔥 STAGE 2: Fine-tuning with unfrozen top layers (5 epochs)")
    print("="*60)
    
    base_model.trainable = True
    for layer in base_model.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
    
    fine_tune_at = max(0, len(base_model.layers) - 40)
    for layer in base_model.layers[:fine_tune_at]:
        if not isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=5e-6),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    finetune_steps = max(fn_args.train_steps - warmup_steps, 10)
    eval_steps_stage2 = max(fn_args.eval_steps, 5)
    
    model.fit(
        train_dataset,
        steps_per_epoch=finetune_steps,
        validation_data=eval_dataset,
        validation_steps=eval_steps_stage2,
        epochs=10, 
        initial_epoch=5,
        class_weight=CLASS_WEIGHTS,
        callbacks=callbacks,
        verbose=1
    )
    
    # ==================== SAVE MODEL ====================
    print("\n" + "="*60)
    print("✅ Saving model artifact...")
    print("="*60)
    
    # Use temp directory to bypass OneDrive locks
    temp_dir = tempfile.mkdtemp()
    print(f"   Saving to temporary location: {temp_dir}")
    
    try:
        # Save in standard TF format
        tf.saved_model.save(model, temp_dir)
        
        # Clear destination if it exists
        if os.path.exists(fn_args.serving_model_dir):
            shutil.rmtree(fn_args.serving_model_dir)
            
        # Copy from Temp to Destination
        shutil.copytree(temp_dir, fn_args.serving_model_dir)
        print(f"✅ Model successfully saved to: {fn_args.serving_model_dir}")
        
    except Exception as e:
        print(f"❌ Standard save failed: {e}")
        # Fallback to .keras
        fallback_path = fn_args.serving_model_dir + ".keras"
        model.save(fallback_path)
        print(f"⚠️ Saved as fallback .keras file: {fallback_path}")
        
    finally:
        # Cleanup temp dir
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

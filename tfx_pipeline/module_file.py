
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
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
import os

# Define feature spec for parsing TFRecords
_FEATURE_SPEC = {
    'image_raw': tf.io.FixedLenFeature([], tf.string),
    'label': tf.io.FixedLenFeature([], tf.int64),
}

def _parse_function(example_proto):
    """Parses a single tf.train.Example."""
    features = tf.io.parse_single_example(example_proto, _FEATURE_SPEC)
    
    # Decode image
    image = tf.io.decode_jpeg(features['image_raw'], channels=3)
    image = tf.image.resize(image, [224, 224])
    image = tf.cast(image, tf.float32) / 255.0  # Normalize
    
    # Label
    label = features['label']
    
    return image, label

def _gzip_reader_fn(filenames):
    """Small utility to return a record reader that can handle gzip."""
    return tf.data.TFRecordDataset(filenames, compression_type='GZIP')

def _input_fn(file_pattern, batch_size=32):
    """Generates features and label for training."""
    # Auto-detect compression
    files = tf.io.gfile.glob(file_pattern)
    compression_type = None
    
    if files:
        # Check first file for GZIP magic bytes (1f 8b)
        with tf.io.gfile.GFile(files[0], 'rb') as f:
            header = f.read(2)
            if header == b'\x1f\x8b':
                print(f"Detected GZIP compression for {files[0]}")
                compression_type = 'GZIP'
            else:
                print(f"Detected NO compression for {files[0]}")
    
    dataset = tf.data.TFRecordDataset(files, compression_type=compression_type)
    dataset = dataset.map(_parse_function, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.shuffle(1000).batch(batch_size).repeat()
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset

def build_model():
    """Builds the Keras model."""
    model = keras.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(6, activation='softmax') # 6 classes
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def run_fn(fn_args: FnArgs):
    """Train the model based on given args."""
    
    # Create datasets
    train_dataset = _input_fn(fn_args.train_files)
    eval_dataset = _input_fn(fn_args.eval_files)
    
    model = build_model()
    
    # Train
    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        epochs=1 # Keep it short for verification
    )
    
    # Save model
    # Use export for SavedModel format in newer Keras/TF
    model.export(fn_args.serving_model_dir)

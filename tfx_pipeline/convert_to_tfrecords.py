import tensorflow as tf
import os
import glob
from PIL import Image
import numpy as np
import io

# Define paths
DATA_ROOT = os.path.join('consolidated_medical_data', 'train')
OUTPUT_DIR = os.path.join('tfx_data', 'train')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'data.tfrecord')

# Define class names (must match the folder structure)
CLASS_NAMES = [
    "01_NORMAL_LUNG",
    "02_NORMAL_BONE",
    "03_NORMAL_PNEUMONIA",
    "04_LUNG_CANCER",
    "05_FRACTURED",
    "06_PNEUMONIA"
]

def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy()
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def create_tf_example(image_path, label):
    """Creates a tf.train.Example proto from an image path and label."""
    try:
        # Load and resize image
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        feature = {
            'image_raw': _bytes_feature(img_bytes),
            'label': _int64_feature(label),
        }
        return tf.train.Example(features=tf.train.Features(feature=feature))
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Scanning {os.path.abspath(DATA_ROOT)}...")
    
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    with tf.io.TFRecordWriter(OUTPUT_FILE) as writer:
        count = 0
        for label, class_name in enumerate(CLASS_NAMES):
            class_dir = os.path.join(DATA_ROOT, class_name)
            if not os.path.exists(class_dir):
                print(f"Warning: Directory {class_dir} not found.")
                continue
                
            print(f"Processing class: {class_name} (Label: {label})")
            
            # Find all images
            image_files = glob.glob(os.path.join(class_dir, "*.*"))
            print(f"  Found {len(image_files)} files in {class_name}")
            
            for image_path in image_files:
                if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    continue
                    
                tf_example = create_tf_example(image_path, label)
                if tf_example:
                    writer.write(tf_example.SerializeToString())
                    count += 1
                    if count % 100 == 0:
                        print(f"  Processed {count} images...")

    print(f"Successfully created TFRecord at {os.path.abspath(OUTPUT_FILE)}")
    print(f"Total images processed: {count}")
    
    if count == 0:
        raise ValueError("No images were processed! Check your DATA_ROOT path and ensure images exist.")

if __name__ == '__main__':
    main()

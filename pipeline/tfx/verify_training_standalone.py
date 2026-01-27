
import tensorflow as tf
import os
import shutil
from pathlib import Path
from module_file import run_fn

# Mock FnArgs to simulate TFX passing arguments
class MockFnArgs:
    def __init__(self, train_files, eval_files, serving_model_dir, train_steps, eval_steps):
        self.train_files = train_files
        self.eval_files = eval_files
        self.serving_model_dir = serving_model_dir
        self.train_steps = train_steps
        self.eval_steps = eval_steps

def main():
    print("Starting standalone verification of training logic...")
    
    # Path resolution: pipeline/tfx/script.py -> pipeline/tfx -> pipeline -> root
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    data_path = str(BASE_DIR / 'tfx_data' / 'train' / 'data.tfrecord')
    serving_model_dir = str(BASE_DIR / 'pipeline' / 'tfx' / 'serving_model_standalone')

    
    # Clean up previous run
    if os.path.exists(serving_model_dir):
        shutil.rmtree(serving_model_dir)
        
    # Check data
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        return

    # Create args
    # PRODUCTION: Use 355 steps/epoch to cover full dataset (11,342 images / 32 batch)
    args = MockFnArgs(
        train_files=[data_path],
        eval_files=[data_path],
        serving_model_dir=serving_model_dir,
        train_steps=355,  # Full dataset coverage
        eval_steps=50     # More robust evaluation
    )
    
    try:
        print("Running run_fn...")
        run_fn(args)
        print("\n✅ Training completed successfully!")
        
        if os.path.exists(os.path.join(serving_model_dir, 'saved_model.pb')):
            print(f"✅ Model saved correctly at {serving_model_dir}")
        else:
            print(f"⚠️ Training finished but 'saved_model.pb' not found in {serving_model_dir}")
            
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


from pathlib import Path
from tfx.orchestration.local.local_dag_runner import LocalDagRunner
from pipeline import create_pipeline

# Path resolution: pipeline/tfx/run_pipeline.py -> pipeline/tfx -> pipeline -> root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

PIPELINE_NAME = 'voxray_diagnosis_pipeline'
PIPELINE_ROOT = str(BASE_DIR / 'pipeline' / 'tfx' / 'pipeline_root')
DATA_ROOT = str(BASE_DIR / 'tfx_data' / 'train')  # Pointing to converted TFRecords
MODULE_FILE = str(BASE_DIR / 'pipeline' / 'tfx' / 'module_file.py')
SERVING_MODEL_DIR = str(BASE_DIR / 'backend' / 'models' / 'serving')

def run():
    tfx_pipeline = create_pipeline(
        pipeline_name=PIPELINE_NAME,
        pipeline_root=PIPELINE_ROOT,
        data_root=DATA_ROOT,
        module_file=MODULE_FILE,
        serving_model_dir=SERVING_MODEL_DIR,
    )
    LocalDagRunner().run(tfx_pipeline)

if __name__ == '__main__':
    run()

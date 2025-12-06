
import os
from tfx.orchestration.local.local_dag_runner import LocalDagRunner
from pipeline import create_pipeline

PIPELINE_NAME = 'voxray_diagnosis_pipeline'
PIPELINE_ROOT = os.path.join('tfx_pipeline', 'pipeline_root')
DATA_ROOT = os.path.join('tfx_data', 'train') # Pointing to converted TFRecords
MODULE_FILE = os.path.join('tfx_pipeline', 'module_file.py')
SERVING_MODEL_DIR = os.path.join('tfx_pipeline', 'serving_model')

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

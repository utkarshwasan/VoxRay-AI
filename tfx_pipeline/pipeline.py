
import os
from tfx import v1 as tfx

def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_root: str,
    module_file: str,
    serving_model_dir: str,
) -> tfx.dsl.Pipeline:
    """Creates a TFX pipeline."""

    # 1. ExampleGen: Ingest data
    example_gen = tfx.components.ImportExampleGen(input_base=data_root)

    # 2. StatisticsGen: Compute statistics
    statistics_gen = tfx.components.StatisticsGen(examples=example_gen.outputs['examples'])

    # 3. SchemaGen: Infer schema
    schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs['statistics'],
        infer_feature_shape=True
    )

    # 4. Trainer: Train the model
    trainer = tfx.components.Trainer(
        module_file=module_file,
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        train_args=tfx.proto.TrainArgs(num_steps=100),
        eval_args=tfx.proto.EvalArgs(num_steps=5)
    )

    # 5. Pusher: Push model to serving directory
    pusher = tfx.components.Pusher(
        model=trainer.outputs['model'],
        push_destination=tfx.proto.PushDestination(
            filesystem=tfx.proto.PushDestination.Filesystem(
                base_directory=serving_model_dir
            )
        )
    )

    components = [
        example_gen,
        statistics_gen,
        schema_gen,
        trainer,
        pusher,
    ]

    return tfx.dsl.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=True,
        metadata_connection_config=tfx.orchestration.metadata.sqlite_metadata_connection_config(
            os.path.join(pipeline_root, 'metadata.sqlite')
        ),
    )

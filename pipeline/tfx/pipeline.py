"""
TFX Pipeline Configuration for Medical Image Classification
Includes: ExampleGen, StatisticsGen, SchemaGen, Trainer, Evaluator, Pusher
"""

import os
from tfx import v1 as tfx
import tensorflow_model_analysis as tfma

def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_root: str,
    module_file: str,
    serving_model_dir: str,
) -> tfx.dsl.Pipeline:
    """Creates a production-grade TFX pipeline with model evaluation."""

    # 1. ExampleGen: Ingest data from TFRecords
    example_gen = tfx.components.ImportExampleGen(input_base=data_root)

    # 2. StatisticsGen: Compute statistics for data validation
    statistics_gen = tfx.components.StatisticsGen(
        examples=example_gen.outputs['examples']
    )

    # 3. SchemaGen: Infer schema from statistics
    schema_gen = tfx.components.SchemaGen(
        statistics=statistics_gen.outputs['statistics'],
        infer_feature_shape=True
    )

    # 4. ExampleValidator: Validate examples against schema
    example_validator = tfx.components.ExampleValidator(
        statistics=statistics_gen.outputs['statistics'],
        schema=schema_gen.outputs['schema']
    )

    # 5. Trainer: Train the ResNet50V2 model with two-stage training
    trainer = tfx.components.Trainer(
        module_file=module_file,
        examples=example_gen.outputs['examples'],
        schema=schema_gen.outputs['schema'],
        train_args=tfx.proto.TrainArgs(num_steps=100),
        eval_args=tfx.proto.EvalArgs(num_steps=20)
    )

    # 6. Evaluator: Evaluate model performance with TFMA
    eval_config = tfma.EvalConfig(
        model_specs=[
            tfma.ModelSpec(label_key='label')
        ],
        slicing_specs=[
            tfma.SlicingSpec(),  # Overall metrics
        ],
        metrics_specs=[
            tfma.MetricsSpec(
                metrics=[
                    tfma.MetricConfig(class_name='SparseCategoricalAccuracy'),
                    tfma.MetricConfig(class_name='ExampleCount'),
                    tfma.MetricConfig(class_name='SparseCategoricalCrossentropy'),
                ]
            )
        ]
    )

    evaluator = tfx.components.Evaluator(
        examples=example_gen.outputs['examples'],
        model=trainer.outputs['model'],
        eval_config=eval_config
    )

    # 7. Pusher: Push validated model to serving directory
    pusher = tfx.components.Pusher(
        model=trainer.outputs['model'],
        model_blessing=evaluator.outputs['blessing'],
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
        example_validator,
        trainer,
        evaluator,
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

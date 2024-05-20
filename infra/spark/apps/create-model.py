import argparse
import json
import os
import sys
import time

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType
from pyspark.ml import Pipeline
from pyspark.ml.tuning import CrossValidator

Estimator_t = CrossValidator | Pipeline

def parse_arguments():
    # create-model.py cross-validator -d datasets/NF-UNSW-NB15-v2.parquet -s setups/SETUP_DTC_NETV2_MODEL_CV -m models/DTC_NETV2_MODEL2
    parent_parser = argparse.ArgumentParser(prog="create-model", add_help=False)

    parent_parser.add_argument("-s", "--setup", help="Path to Setup Folder", required=True)
    # parent_parser.add_argument("--schema", help="Path to Schema JSON", default="schemas/NetV2_schema.json")
    parent_parser.add_argument("-d", "--dataset", help="Path to Dataset", required=True)
    parent_parser.add_argument("-m", "--model", help="Path to Output Model", required=True)

    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers(dest="command", required=True, help="Choose model")

    pipeline = subparser.add_parser("pipeline", help="Pipeline", parents=[parent_parser])
    
    cross_validator = subparser.add_parser("cross-validator", help="CrossValidator", parents=[parent_parser])
    cross_validator.add_argument("-p", "--parallelism", help="Parallelism's Number", type=int, default=1)
    cross_validator.add_argument("-f", "--folds", help="Number of Folds. Must be over 1 fold", type=int, default=2)

    return main_parser.parse_args()


def create_session():
    name = " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:])
    spark: SparkSession = SparkSession.builder \
        .appName(name) \
        .config("spark.sql.debug.maxToStringFields", '100') \
        .getOrCreate()
    return spark


def spark_schema_from_json(spark: SparkSession, path: str) -> StructType:
    schema_json = json.loads(spark.read.text(path).first()[0])
    return StructType.fromJson({"fields": schema_json["fields"]})


def main():    
    args = parse_arguments()
    COMMAND = args.command
    SETUP_PATH = args.setup
    DATASET_PATH = args.dataset
    # SCHEMA_PATH = args.schema
    MODEL_PATH = args.model

    print(" [CONF] ".center(50, "-"))
    print("COMMAND:", COMMAND)
    print("SETUP_PATH:", SETUP_PATH)
    # print("SCHEMA_PATH:", DATASET_PATH)
    print("DATASET_PATH:", DATASET_PATH)
    print("MODEL_PATH:", MODEL_PATH)
    print()

    spark = create_session()

    print(" [SETUP] ".center(50, "-"))
    print(f"Loading {SETUP_PATH}...")
    t0 = time.time()
    if COMMAND == "cross-validator":
        if args.folds < 1: raise Exception(f"Folds must be >= 1, not: {args.folds}")
        estimator: CrossValidator = CrossValidator.load(SETUP_PATH)
        estimator = estimator.setNumFolds(args.folds).setParallelism(args.parallelism)

        target = estimator.getEstimator().getStages()[-1].getLabelCol()
        features = estimator.getEstimator().getStages()[0].getInputCols()
    elif COMMAND == "pipeline":
        estimator: Pipeline = Pipeline.load(SETUP_PATH)
        target = estimator.getStages()[-1].getLabelCol()
        features = estimator.getStages()[0].getInputCols()
    t1 = time.time()
    print(f"OK. Loaded in {t1 - t0}s")
        
    print("TARGET:", target)
    print("FEATURES:", features)
    print()

    # print(" [SCHEMA] ".center(50, "-"))
    # print(f"Loading {SCHEMA_PATH}...")

    # t0 = time.time()
    # schema = spark_schema_from_json(spark, SCHEMA_PATH)
    # t1 = time.time()

    # for field in schema.jsonValue()["fields"]:
        # print(f"{field['name']}: {field['type']}")
    # print(schema.simpleString())
    # print()

    print(" [DATASET] ".center(50, "-"))
    print(f"Loading {DATASET_PATH}...")
    t0 = time.time()
    train_df = spark.read.parquet(DATASET_PATH)
    t1 = time.time()
    print(f"OK. Loaded in {t1 - t0}s")
    print()

    print()

    print(" [MODEL] ".center(50, "-"))
    print("Training model...")
    t0 = time.time()
    model: Estimator_t = estimator.fit(train_df)
    t1 = time.time()
    if COMMAND == "cross-validator": model = model.bestModel
    print(f"OK. Trained in {t1 - t0}s")
    print()
    print(model.stages[-1])
    print()

    print(f"Saving model to {MODEL_PATH}...")
    model.write().overwrite().save(MODEL_PATH)
    print("OK")


if __name__ == "__main__":
    main()

import argparse
import os
import sys
import time

import pyspark.sql.functions as F
from pyspark.sql import SparkSession, DataFrame
from pyspark.ml import PipelineModel
from pyspark.ml.base import Model
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, BinaryClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics



def parse_arguments():
    # evaluate-model.py -m models/UNSW_DTC_CV_PR_AUC -d datasets/NF-UNSW-NB15-v2.parquet
    parser = argparse.ArgumentParser(prog="evaluate-model", description="Evaluates a Model. Expects a PipelineModel")
    parser.add_argument("-m", "--model", help="Path to Model (Input)", default="models/UNNAMED_MODEL")
    parser.add_argument("-d", "--dataset", help="Path to Dataset", default="datasets/NF-UNSW-NB15-v2.parquet", required=True)
    parser.add_argument("--test-ratio", type=float, help="Ratio for test (0.0 to 1.0)", default=1.0)
    parser.add_argument("--seed", type=float, help="Seed Number", default=42)
    return parser.parse_args()


def create_session():
    #    .config("spark.cores.max", '3') \
    name = " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:])
    spark: SparkSession = SparkSession.builder \
        .appName(name) \
        .config("spark.sql.debug.maxToStringFields", '100') \
        .getOrCreate()
    return spark


def show_features_importances(model: PipelineModel, features: list[str]):
    importances = model.stages[-1].featureImportances
    feature_list = features

    print("Feature Importances:")
    for feature, importance in zip(feature_list, importances):
        print(f"{feature}: {importance:.4f}")


def show_confusion_matrix(pred_labels: DataFrame, target: str):
    print("x=real value, y=prediction")
    confusion_matrix = pred_labels.groupBy(target).pivot("prediction").agg(F.count("prediction")).na.fill(0).orderBy(target)
    confusion_matrix.show()


def show_confusion_matrix2(pred_labels: DataFrame, target: str):
    p_values = pred_labels.select("prediction", target).rdd.map(lambda x: (float(x[0]), float(x[1])))
    metrics = MulticlassMetrics(p_values)
    confusion_matrix = metrics.confusionMatrix().toArray()
    print(confusion_matrix)


def show_binary_metrics(predictions, target):
    evaluator = BinaryClassificationEvaluator(labelCol=target, rawPredictionCol="rawPrediction")

    # areaUnderROC (balanced) | areaUnderPR (imbalanced)
    metrics = [
        "areaUnderROC",
        "areaUnderPR",
    ]

    for metric in metrics:
        score = evaluator.evaluate(predictions, {evaluator.metricName: metric})
        print(f"{metric}: {score}")


def show_multiclass_metrics(predictions, target):
    evaluator = MulticlassClassificationEvaluator(labelCol=target)

    # f1|accuracy|weightedPrecision|weightedRecall|weightedTruePositiveRate|weightedFalsePositiveRate|weightedFMeasure|truePositiveRateByLabel|falsePositiveRateByLabel|precisionByLabel|recallByLabel|fMeasureByLabel|logLoss|hammingLoss
    metrics = [
        "accuracy",
        "f1",
        "truePositiveRateByLabel",
        "falsePositiveRateByLabel",
        # "weightedPrecision",
        # "weightedRecall",
        # "weightedTruePositiveRate",
        # "weightedFalsePositiveRate"
    ]

    for metric in metrics:
        score = evaluator.evaluate(predictions, {evaluator.metricName: metric})
        print(f"{metric}: {score}")


def main():    
    args = parse_arguments()
    DATASET_PATH = args.dataset
    MODEL_PATH = args.model
    TEST_RATIO = args.test_ratio
    SEED = args.seed

    print(" [CONF] ".center(50, "-"))
    print("MODEL_PATH:", MODEL_PATH)
    print("DATASET_PATH:", DATASET_PATH)
    print("TEST_RATIO:", TEST_RATIO)
    print()

    spark = create_session()

    print(" [MODEL] ".center(50, "-"))
    print(f"Loading {MODEL_PATH}...")
    t0 = time.time()
    model: Model = PipelineModel.load(MODEL_PATH)
    t1 = time.time()
    print(f"OK. Loaded in {t1 - t0}s")
    target = model.stages[-1].getLabelCol()
    features = model.stages[-1].getFeaturesCol()
        
    print("TARGET:", target)
    print("FEATURES:", features)
    print()

    print(" [FEATURES IMPORTANCES] ".center(50, "-"))
    show_features_importances(model, features)
    print()

    print(" [DATASET] ".center(50, "-"))
    print(f"Loading {DATASET_PATH}")
    t0 = time.time()
    df = spark.read.parquet(DATASET_PATH)
    t1 = time.time()
    print(f"OK. Loaded in {t1 - t0}s")
    print()

    print(f"Splitting data into TEST: {TEST_RATIO}")
    _, test_df = df.randomSplit((1 - TEST_RATIO, TEST_RATIO), seed=SEED)
    print()

    print(" [PREDICTIONS] ".center(50, "-"))
    print("Making predictions...")
    t0 = time.time()
    predictions = model.transform(test_df)
    t1 = time.time()
    print(f"OK. Predicted in {t1 - t0}s")
    print()

    pred_labels = predictions.select(features, "probability", "prediction", "label")
    pred_labels.show(20)
    print()

    print(" [CONFUSION MATRIX] ".center(50, "-"))
    t0 = time.time()
    show_confusion_matrix(pred_labels, target)
    t1 = time.time()
    print(f"OK in {t1 - t0}s")
    print()

    print(" [METRICS] ".center(50, "-"))
    print("Binary Metrics:")
    t0 = time.time()
    show_binary_metrics(predictions, target)
    t1 = time.time()
    print(f"OK in {t1 - t0}s")
    print()
    print("Multiclass Metrics")
    t0 = time.time()
    show_multiclass_metrics(predictions, target)
    t1 = time.time()
    print(f"OK in {t1 - t0}s")
    print()


if __name__ == "__main__":
    main()
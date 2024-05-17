import argparse
import time

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.mllib.evaluation import MulticlassMetrics
from pyspark.ml.tuning import CrossValidator


def parse_arguments():
    # setup_to_model.py -d datasets/NF-UNSW-NB15-v2.parquet -s setups/DTC_NETV2_MODEL_CV_SETUP -t CrossValidator -m models/DTC_NETV2_MODEL
    parser = argparse.ArgumentParser(description="TrainModelFromSetup")
    parser.add_argument("-d", "--dataset", help="Path to Dataset", default="datasets/NF-UNSW-NB15-v2.parquet", required=True)
    parser.add_argument("-s", "--setup", help="Path to Setup File", required=True)
    parser.add_argument("-t", "--setup-type", help="Setup (CrossValidator or Pipeline)", required=True, choices=["CrossValidator", "Pipeline"])
    parser.add_argument("-m", "--model", help="Path to Model (Output)", default="models/UNAMED_MODEL")
    parser.add_argument("--train-split", type=float, help="split for training (0.0 to 1.0)", default=0.7)
    parser.add_argument("--seed", type=float, help="Seed Number", default=42)
    return parser.parse_args()


def show_confusion_matrix(pred_labels, target):
    p_values = pred_labels.select("prediction", target).rdd.map(lambda x: (float(x[0]), float(x[1])))
    metrics = MulticlassMetrics(p_values)
    confusion_matrix = metrics.confusionMatrix().toArray()
    print(confusion_matrix)


def show_metrics(predictions, target):
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
    SETUP_PATH = args.setup
    SETUP_TYPE = args.setup_type
    MODEL_PATH = args.model
    TRAIN_SPLIT = args.train_split
    TEST_SPLIT = float(1-TRAIN_SPLIT)
    SEED = args.seed

    print(" [CONF] ".center(50, "-"))
    print("DATA_PATH:", DATASET_PATH)
    print("SETUP_PATH:", SETUP_PATH)
    print("SETUP_TYPE:", SETUP_TYPE)
    print("MODEL_PATH:", MODEL_PATH)
    print("TRAIN_SPLIT:", TRAIN_SPLIT)
    print()

    print(" [SESSION] ".center(50, "-"))
    spark: SparkSession = SparkSession.builder \
        .appName("TrainModelFromSetup") \
        .config("spark.cores.max", '3') \
        .getOrCreate()
    sc = spark.sparkContext

    print(f"Loading {SETUP_PATH}...")
    if SETUP_TYPE == "CrossValidator":
        fitter = CrossValidator.load(SETUP_PATH)
        TARGET = fitter.getEvaluator().getLabelCol()
        FEATURES = fitter.getEstimator().getStages()[0].getInputCols()
    elif SETUP_TYPE == "Pipeline":
        fitter = Pipeline.load(SETUP_PATH)
        TARGET = fitter.getStages()[-1].getLabelCol()
        FEATURES = fitter.getStages()[0].getInputCols()
    print("TARGET:", TARGET)
    print("FEATURES:", FEATURES)
    print()

    print(f"Loading {DATASET_PATH}...")
    df = spark.read.parquet(DATASET_PATH)
    print()

    print(f"Splitting data into train/test: {TRAIN_SPLIT}/{TEST_SPLIT}...")
    train_df, test_df = df.randomSplit((TRAIN_SPLIT, TEST_SPLIT), seed=SEED)
    print()

    print(" [MODEL] ".center(50, "-"))
    print("Training model...")
    t0 = time.time()
    model = fitter.fit(train_df).bestModel
    t1 = time.time()
    print(f"OK. Trained in {t1 - t0}s")
    print()
    print(model.stages[-1])
    print()

    print(f"Saving model to {MODEL_PATH}...")
    model.write().overwrite().save(MODEL_PATH)
    print("OK")

    print(" [PREDICTIONS] ".center(50, "-"))
    print("Making predictions...")
    predictions = model.transform(test_df)
    print("OK.")
    print()

    pred_labels = predictions.select("features", "probability", "prediction", "label")
    pred_labels.show(20)
    print()

    print(" [CONFUSION MATRIX] ".center(50, "-"))
    show_confusion_matrix(pred_labels, TARGET)
    print()

    print(" [METRICS] ".center(50, "-"))
    show_metrics(predictions, TARGET)


if __name__ == "__main__":
    main()

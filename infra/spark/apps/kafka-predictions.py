import argparse
import json

import pyspark.sql.functions as F
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.pipeline import PipelineModel
from pyspark.sql.types import StructType


def parse_arguments():
    parser = argparse.ArgumentParser(description="KafkaPredictions")
    parser.add_argument("-s", "--servers", nargs="+", help="kafka.bootstrap.servers (i.e. <ip1>:<host1> <ip2>:<host2> ... <ipN>:<hostN>)", default=["kafka:9092"])
    parser.add_argument("-t", "--topic", help="Kafka Topic (i.e. topic1)", default="NetV2")
    parser.add_argument("-m", "--model", help="Path to Model", default="models/DecisionTreeClassifier_NF-UNSW-NB15-v2_MODEL")
    parser.add_argument("--schema", help="Path to Schema JSON", default="schemas/NetV2_schema.json")
    return parser.parse_args()


def spark_schema_from_json(spark: SparkSession, path: str) -> StructType:
    schema_json = spark.read.text(path).first()[0]
    return StructType.fromJson(json.loads(schema_json))


def main() -> None:
    args = parse_arguments()
    servers: str = ",".join(args.servers)
    topic: str = args.topic
    model_path: str = args.model
    schema_path: str = args.schema

    #.config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    spark: SparkSession = SparkSession.builder \
                        .appName("NetV2Predictions") \
                        .config("spark.cores.max", '3') \
                        .getOrCreate()
    
    sc: SparkContext = spark.sparkContext
    sc.setLogLevel("WARN")

    model = PipelineModel.load(model_path)
    # sc.broadcast(model)

    schema = spark_schema_from_json(spark, schema_path)

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load()

    features = df \
            .selectExpr("CAST(value AS STRING)") \
            .select(F.from_csv("value", schema.simpleString()).alias("features")) \
            .select("features.*")

    # features = df \
    #     .selectExpr("CAST(value AS STRING) AS value") \
    #     .selectExpr(f"from_csv(value, '{schema.simpleString()}') AS features") \
    #     .select("features.*")

    predictions = model.transform(features).select("features", "prediction", "probability")

    query = predictions.writeStream \
            .queryName("NetV2 Predictions Writer") \
            .format("console") \
            .outputMode("append") \
            .start()
    query.awaitTermination()

    spark.close()


if __name__ == "__main__":
    main()

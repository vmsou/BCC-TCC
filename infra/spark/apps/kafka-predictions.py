import json
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.ml.pipeline import PipelineModel
import pyspark.sql.functions as F
from pyspark.sql.types import StructType


def spark_schema_from_json(spark: SparkSession, path: str) -> StructType:
    schema_json = spark.read.text(path).first()[0]
    return StructType.fromJson(json.loads(schema_json))

def schema_to_DDL(schema: StructType) -> str:
    ddl_fields = []
    for field in schema.fields:
        ddl_field = f"{field.name} {field.dataType.simpleString()}"
        ddl_fields.append(ddl_field)
    return ", ".join(ddl_fields)


def main() -> None:
    spark: SparkSession = SparkSession.builder \
                        .appName("NetV2Predictions") \
                        .config("spark.cores.max", '3') \
                        .getOrCreate()
    sc: SparkContext = spark.sparkContext
    sc.setLogLevel("WARN")

    model = PipelineModel.load("./models/DecisionTreeClassifier_NF-UNSW-NB15-v2_MODEL")
    schema = spark_schema_from_json(spark, "./NetV2_schema.json")

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "netV2") \
        .option("startingOffsets", "earliest") \
        .load()

    features = df \
            .selectExpr("CAST(value AS STRING)") \
            .select(F.from_csv("value", schema.simpleString()).alias("features")) \
            .select("features.*")

    predictions = model.transform(features).select("features", "prediction", "probability")

    query = predictions.writeStream \
            .format("console") \
            .outputMode("update") \
            .start()
    query.awaitTermination()

    sc.close()


if __name__ == "__main__":
    main()

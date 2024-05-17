#!/usr/bin/env python

import argparse
import json
import time
from pathlib import Path

import pyspark.sql.functions as F
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType


def parse_arguments():
    # kafka-producer.py -d datasets/NF-UNSW-NB15-v2.parquet --schema schemas/NetV2_schema.json --topic NetV2 -n 10 --delay 1
    parser = argparse.ArgumentParser(description="CSV Producer")
    parser.add_argument("-d", "--dataset", help="Data Source", default="datasets/NF-UNSW-NB15-v2.parquet")
    parser.add_argument("--schema", help="Path to Schema JSON", default="schemas/NetV2_schema.json")
    parser.add_argument("-s", "--servers", nargs="+", help="bootstrap_servers (i.e. <ip1>:<host1> <ip2>:<host2> ... <ipN>:<hostN>)", default=["localhost:9092"])
    parser.add_argument("-t", "--topic", help="Topic name", default="NetV2")
    parser.add_argument("--output-type", help="Send message type (i.e., csv, ...)", default="csv", choices=["csv"])
    parser.add_argument("-n", help="Total number of rows (-1 for all)", default=-1, type=int)
    parser.add_argument("--delay", help="Seconds of delay for each row to be sent", default=1, type=int)
    return parser.parse_args()


def spark_schema_from_json(spark: SparkSession, path: str) -> StructType:
    schema_json = spark.read.text(path).first()[0]
    return StructType.fromJson(json.loads(schema_json))


def main():
    args = parse_arguments()
    dataset: str = args.dataset
    schema_path: str = args.schema
    dataset_ext = Path(dataset).suffix
    servers: list = ",".join(args.servers)
    topic: str = args.topic
    output_type = args.output_type
    N: int = args.n
    delay: int = args.delay
	
    print("[ CONF ]".center(50, "-"))
    print("Dataset:", dataset)
    print("Schema Path:", schema_path)
    print("Servers:", servers)
    print("Topic:", topic)
    print("Output Type:", output_type)
    print("N:", N)
    print("delay:", delay)

    spark: SparkSession = SparkSession.builder \
        .appName("RandomRowKafkaWriter") \
        .config("spark.cores.max", '1') \
        .getOrCreate()
                            
    df: DataFrame = None
    schema = spark_schema_from_json(spark, schema_path)
    if dataset_ext == ".csv": df = spark.readStream.schema(schema).csv(dataset)
    elif dataset_ext == ".parquet": df = spark.readStream.schema(schema).parquet(dataset)
    else: raise Exception(f"File type: {dataset_ext} not supported.")
    schema = df.schema

    def write_row(df: DataFrame, df_id):
        for row in df.collect():
            row_df = spark.createDataFrame([row], schema=schema)
            row_df.selectExpr("CAST(concat_ws(',', *) AS STRING) AS value") \
                .write \
                .format("kafka") \
                .option("kafka.bootstrap.servers", servers) \
                .option("topic", topic) \
                .save()
            time.sleep(delay)

    rand_df = df.orderBy(F.rand())
    if N > 0: rand_df = df.limit(int(N))

    query = rand_df \
            .writeStream \
            .queryName("CSV Kafka Writer") \
            .foreachBatch(write_row) \
            .outputMode("append") \
            .trigger(once=True) \
            .start()
    query.awaitTermination()


if __name__ == "__main__":
	main()

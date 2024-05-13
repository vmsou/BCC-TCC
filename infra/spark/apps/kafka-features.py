from pyspark.sql import SparkSession
import pyspark.sql.functions as funcs

#.config("spark.streaming.stopGracefullyOnShutdown", True) \  # needs hadoop create /tmp
spark: SparkSession = SparkSession.builder \
                    .appName("FeaturesKafkaTest") \
                    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3") \
                    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-server:9092") \
    .option("subscribe", "features") \
    .option("startingOffsets", "latest") \
    .load()

expanded_df = df.selectExpr("CAST(value AS STRING)").map(lambda row: row.split(","))

query = expanded_df.writeStream \
        .format("console") \
        .outputMode("update") \
        .start() \
        .awaitTermination()

def predict_batch(batch_df, batch_id):
    print(f"Processing {batch_id}")
    # df = df.selectExpr("CAST(value AS STRING)")

    predictions_df = batch_df
    
    predictions_df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka-server:9092") \
        .option("topic", "predictions") \
        .start()


query = expanded_df.writeStream \
        .trigger(processingTime="2 seconds") \
        .foreachBatch(predict_batch) \
        .outputMode("update") \
        .start() \
        .awaitTermination()

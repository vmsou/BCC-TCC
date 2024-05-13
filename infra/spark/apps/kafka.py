from pyspark.sql import SparkSession, DataFrame

def process_micro_batch(batch_df: DataFrame, batch_id):
    processed_df = batch_df

    try:
        processed_df.write \
            .format("parquet") \
            .mode("append") \
            .save("test.parquet")
    except Exception as e:
        print(f"Error: {str(e)}")

spark: SparkSession = SparkSession.builder.appName("KafkaTest").getOrCreate()

# .option("startingOffsets", "earliest")
kafka_df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", "host1:port1,host2:port2") \
  .option("subscribe", "topic1") \
  .load()

kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

# .option("checkpointLocation", "/checkpoints/") \
query = kafka_df \
    .writeStream \
    .foreachBatch(process_micro_batch) \
    .trigger(processingTime="1 minute") \
    .start()

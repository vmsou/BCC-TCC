from pyspark.sql import SparkSession
import pyspark.sql.functions as funcs

#.config("spark.streaming.stopGracefullyOnShutdown", True) \  # needs hadoop create /tmp
spark: SparkSession = SparkSession.builder \
                    .appName("ConsoleKafkaTest") \
                    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.3") \
                    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka-server:9092") \
    .option("subscribe", "words") \
    .option("startingOffsets", "earliest") \
    .load()

query = df.writeStream \
        .format("console") \
        .outputMode("update") \
        .start() \
        .awaitTermination()

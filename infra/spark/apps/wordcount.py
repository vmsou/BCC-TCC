from pyspark.sql import SparkSession
import pyspark.sql.functions as funcs

#.config("spark.streaming.stopGracefullyOnShutdown", True) \  # needs hadoop create /tmp
spark: SparkSession = SparkSession.builder \
                    .appName("WordCountKafkaTest") \
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

words = df.select(
    funcs.explode(
        funcs.split(df['value'], " ")
    ).alias("word")
)

words_count = words.groupBy("word").count()


query = words_count.writeStream \
        .format("console") \
        .outputMode("complete") \
        .trigger(processingTime='10 seconds') \
        .start() \
        .awaitTermination()

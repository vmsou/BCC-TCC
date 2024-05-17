from pyspark import SparkContext
from pyspark.sql import SparkSession
import pyspark.sql.functions as F


def main() -> None:
    spark: SparkSession = SparkSession.builder \
                        .appName("WordCountKafkaTest") \
                        .config("spark.cores.max", '3') \
                        .getOrCreate()

    sc: SparkContext = spark.sparkContext
    sc.setLogLevel("WARN")
    # sc.setCheckpointDir("hdfs:///user/spark/tmp/")

    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "words") \
        .option("startingOffsets", "earliest") \
        .load()

    words = df.select(
        F.explode(
            F.split(F.col("value"), " ")
        ).alias("word")
    )

    words_count = words.groupBy("word").count()

    query = words_count.writeStream \
            .format("console") \
            .outputMode("complete") \
            .start()
    query.awaitTermination()

    spark.close()


if __name__ == "__main__":
    main()

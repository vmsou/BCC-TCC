from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Submitted") \
    .getOrCreate()

sc = spark.sparkContext
columns = ["language","users_count"]
data = [("Java", "20000"), ("Python", "100000"), ("Scala", "3000")]

rdd = spark.sparkContext.parallelize(data)

df = rdd.toDF()

df.show()
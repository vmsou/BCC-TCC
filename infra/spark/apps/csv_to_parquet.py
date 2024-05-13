import argparse 

from pyspark.sql import SparkSession

def parse_arguments():
	parser = argparse.ArgumentParser(description="CSV to Parquet")
	parser.add_argument("--source", help="Data Source URL", default="https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv")
	parser.add_argument("--output", help="Data Output URL")
	return parser.parse_args()


def main():
    args = parse_arguments()
    source: str = args.source
    output: str = args.output

    spark = SparkSession.builder.appName("CSVtoParquet").getOrCreate()
    df = spark.read.options(delimiter=',', header=True, inferSchema=True).csv(source)
    df.write.mode("overwrite").parquet(output)

if __name__ == "__main__":
    main()
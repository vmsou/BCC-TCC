import argparse 
from pathlib import Path

from pyspark.sql import SparkSession

def parse_arguments():
	parser = argparse.ArgumentParser(description="CSV to Parquet")
	parser.add_argument("-s", "--source", help="Data Source URL", default="https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv")
	parser.add_argument("-o", "--output", help="Data Output Folder URL", default=".")
	return parser.parse_args()


def main():
    args = parse_arguments()
    source: str = args.source
    output: str = args.output

    file_path = Path(source)
    output_path = (Path(output) / file_path.name).with_suffix(".parquet")

    spark: SparkSession = SparkSession.builder.appName("CSVtoParquet").getOrCreate()
    df = spark.read.options(delimiter=',', header=True, inferSchema=True).csv(str(file_path))
    df.write.mode("overwrite").parquet(str(output_path))


if __name__ == "__main__":
    main()
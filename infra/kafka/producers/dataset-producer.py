#!/usr/bin/env python

import argparse
import random
import time
from pathlib import Path

import pandas
from kafka import KafkaProducer


def parse_arguments():
	parser = argparse.ArgumentParser(description="CSV Producer")
	parser.add_argument("-s", "--servers", nargs="+", help="bootstrap_servers (i.e. <ip1>:<host1> <ip2>:<host2> ... <ipN>:<hostN>)", default=["localhost:9092"])
	parser.add_argument("-t", "--topic", help="Topic name", default="topic1")
	parser.add_argument("-d", "--dataset", help="Data Source", default="https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv")
	parser.add_argument("--drop-columns", nargs="+", required=False)
	parser.add_argument("--output-type", help="Send message type (i.e., csv, json, ...)", default="csv")
	return parser.parse_args()


def main():
	args = parse_arguments()
	servers: list = args.servers
	topic: str = args.topic
	dataset: str = args.dataset
	dataset_ext = Path(dataset).suffix
	drop_columns: list[str] | None = args.drop_columns
	output_type = args.output_type

	print("Servers:", servers)
	print("Topic:", topic)
	print("Dataset:", dataset)
	if drop_columns: print("Drop columns:", drop_columns)

	time.sleep(5)
	producer = KafkaProducer(bootstrap_servers=servers, max_block_ms=5000)

	df: pandas.DataFrame = None
	if dataset_ext == ".csv": df = pandas.read_csv(dataset)
	elif dataset_ext == ".parquet": df = pandas.read_parquet(dataset)
	else: raise Exception(f"File type: {dataset_ext} not supported.")

	if drop_columns: df.drop(columns=drop_columns, inplace=True)

	def get_row_csv(row: int):
		return ",".join([str(x) for x in df.iloc[row].values])  # or:df.iloc[idx].to_csv(header=False, index=False, sep=',', lineterminator=',')

	def get_row_json(row: int):
		return df.iloc[row].to_json()
	
	get_row_func = None

	if output_type == "csv": get_row_func = get_row_csv
	elif output_type == "json": get_row_func = get_row_json
	else: raise Exception(f"Output type: {output_type} not supported.")
	
	while True:
		raw_msg = get_row_func(random.randint(0, len(df) - 1))

		# send to Kafka topic
		print(f"{topic} << {raw_msg}")
		producer.send(topic, raw_msg.encode("utf-8"))
		time.sleep(1)


if __name__ == "__main__":
	main()

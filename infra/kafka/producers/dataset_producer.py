#!/usr/bin/env python

import argparse
import json
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

	if dataset_ext == ".csv": df = pandas.read_csv(dataset)
	elif dataset_ext == ".parquet": df = pandas.read_parquet(dataset)
	else: raise Exception(f"File type: {dataset_ext} not supported.")

	if drop_columns: df.drop(columns=drop_columns, inplace=True)

	def get_random_row_csv():
		idx = random.randint(0, len(df) - 1)
		return ",".join(map(str, df.iloc[idx].values))

	def get_random_row_json():
		idx = random.randint(0, len(df) - 1)
		return df.iloc[idx].to_json()
	
	output_func = None

	if output_type == "csv": output_func = get_random_row_csv
	elif output_type == "json": output_func = get_random_row_json
	
	while True:
		row_json = output_func()
		msg = row_json

		# send to Kafka topic
		print(f"{topic} << {msg}")
		producer.send(topic, msg.encode("utf-8"))
		time.sleep(1)


if __name__ == "__main__":
	main()

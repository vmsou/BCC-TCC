#!/usr/bin/env python

import argparse
import json
import time
import random

import pandas
from kafka import KafkaProducer

def parse_arguments():
	parser = argparse.ArgumentParser(description="CSV Producer")
	parser.add_argument("--servers", nargs="+", help="bootstrap_servers (i.e. <ip1>:<host1> <ip2>:<host2> ... <ipN>:<hostN>)", default=["localhost:9092"])
	parser.add_argument("--topic", help="Topic name", default="topic1")
	parser.add_argument("--dataset", help="Data Source", default="https://web.stanford.edu/class/archive/cs/cs109/cs109.1166/stuff/titanic.csv")
	return parser.parse_args()


def main():
	args = parse_arguments()
	servers: list = args.servers
	topic: str = args.topic
	dataset: str = args.dataset

	print("Servers:", servers)
	print("Topic:", topic)
	print("Dataset:", dataset)

	time.sleep(5)
	producer = KafkaProducer(bootstrap_servers=servers, max_block_ms=5000)

	df = pandas.read_csv(dataset)

	def get_random_row():
		idx = random.randint(0, len(df) - 1)
		return df.iloc[idx].to_json()
    
	while True:
		row = get_random_row()

		# send to Kafka topic
		print(f"{topic} << {row}")
		producer.send(topic, bytes(row, encoding='utf8'))
		time.sleep(1)


if __name__ == "__main__":
	main()

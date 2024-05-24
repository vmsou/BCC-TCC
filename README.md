# Distributed NIDS

## Quick Start


### Deploy
To deploy the NIDS cluster, run:
```bash
make compose-up workers=3 datanodes=3
```
or
```bash
docker compose up --scale datanode=3 --scale worker=3 -d
```

### Interface URLs
- HDFS UI: http://localhost:9870
- Spark Master UI: http://localhost:8080
- Spark Jobs UI: http://localhost:4040

## Run on Docker
```bash
> docker exec -it spark-master-1 bash
```

### Example #1 - hdfs
```bash
> docker exec -it hdfs-namenode-1 bash
bash-4.2$ hadoop fs -mkdir -p /user/spark/
bash-4.2$ hadoop fs -chown spark:spark /user/spark

bash-4.2$ wget <url>
...
bash-4.2$ hdfs dfs -put <filename> /user/spark/
bash-4.2$ hdfs dfs -ls /user/spark/
```

### Example #2 - Kafka Topic
```bash
> docker exec -it kafka-broker-1 bash
bash-4.2$ kafka-topics.sh --create --topic words --bootstrap-server broker-1:9092
bash-4.2$ kafka-topics.sh --list --bootstrap-server broker-1:9092
bash-4.2$ kafka-console-producer.sh --broker-list broker-1:9092 broker-2:9092 broker-3:9092 --topic words
>
```

### Example #3 - Submit Spark
```bash
> make submit app="train-model.py cross-validator --folds 4 --parallelism 5 -s setups/<setup-name> --schema schemas/<schema-name>.json -d datasets/<dataset-name> -m models/<model-name>" cores=10 memory=1g
> make submit app="evaluate-model.py -m models/<model-name> -d datasets/<dataset-name>" cores=7 memory=1g
> make kafka-submit app="kafka-predictions.py --brokers broker-1:9092 --model models/<model-name> --schema schemas/<schema-name>.json --topic NetV2" cores=8
```


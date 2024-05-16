# Distributed NIDS

## Quick Start


### Deploy
To deploy the NIDS cluster, run:
```bash
make compose-up workers=3 datanodes=3
```
or
```bash
docker-compose up --scale datanode=3 --scale worker=3 -d
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
> docker exec -it kafka-server-1 bash
bash-4.2$ kafka-topics.sh --create --topic words --bootstrap-server kafka:9092
bash-4.2$ kafka-topics.sh --list --bootstrap-server kafka:9092
bash-4.2$ kafka-console-producer.sh --broker-list kafka:9092 --topic words
>
```

### Example #3 - Submit Spark
```bash
> make kafka-submit app=wordcount.py
```


# Distributed NIDS

## Quick Start

To deploy the NIDS cluster, run:
```bash
docker-compose up -d
```

### Interface URLs
- Namenode: http://localhost:9870
- History server: http://localhost:8188
- Datanode: http://localhost:9864
- Nodemanager: http://localhost:8042
- Resource manager: http://localhost:8088
- Master: http://localhost:8080
- Worker: http://localhost:8081


## Run on Docker
```bash
> docker exec -it nids-master bash
```

### Example #1 - hdfs
```bash
mkdir /opt/data
wget <url> -P /opt/data
bash-4.2$ hdfs dfs -put /opt/data/<filename> /<filename>
bash-4.2$ hdfs dfs -ls /
```

### Example #2 - pyspark
```bash
bash-4.2$ /opt/spark/bin/pyspark --master yarn --name <app_name>
...
>>> df = spark.read.options(delimiter=',', header=True, inferSchema=True).csv("hdfs:///<filename>")
```


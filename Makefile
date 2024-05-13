workers ?= 1
datanodes ?= 1
localN ?= *

# All
compose-up: create-network up-hdfs up-kafka up-spark

compose-down: down-spark down-kafka down-hdfs delete-network

compose-start: start-hdfs up-kafka start-spark

compose-stop: stop-spark stop-kafka stop-hdfs


# Network
create-network: 
	docker network create nids_network --driver bridge || true
delete-network: 
	docker network rm nids_network

# HDFS
build-hdfs:
	docker build -t nids/hdfs ./docker/hdfs
up-hdfs: 
	docker-compose -f ./infra/hdfs/compose.yml up --scale datanode=${datanodes} -d
down-hdfs: 
	docker-compose -f ./infra/hdfs/compose.yml down --volumes
start-hdfs: 
	docker-compose -f ./infra/hdfs/compose.yml start
stop-hdfs: 
	docker-compose -f ./infra/hdfs/compose.yml stop

# Spark
up-spark: 
	docker-compose -f ./infra/spark/compose.yml up --scale worker=${workers} -d
down-spark: 
	docker-compose -f ./infra/spark/compose.yml down --volumes
start-spark: 
	docker-compose -f ./infra/spark/compose.yml start
stop-spark: 
	docker-compose -f ./infra/spark/compose.yml stop

# spark-submit
kafka-submit:
	docker exec spark-master-1 spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 ./apps/$(app)
scala-submit:
	docker exec spark-master-1 spark-submit --class $(class) ./apps/$(app)
local-submit:
	docker exec spark-master-1 spark-submit --master local[${localN}] ./apps/$(app)
submit:
	docker exec spark-master-1 spark-submit ./apps/$(app)

# Kafka
up-kafka: 
	docker-compose -f ./infra/kafka/compose.yml up -d
down-kafka: 
	docker-compose -f ./infra/kafka/compose.yml down --volumes
start-kafka: 
	docker-compose -f ./infra/kafka/compose.yml start
stop-kafka: 
	docker-compose -f ./infra/kafka/compose.yml stop
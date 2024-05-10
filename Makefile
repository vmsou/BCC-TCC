install-spark:
	sudo wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz --no-check-certificate
	tar -zxvf spark-3.5.0-bin-hadoop3.tgz
	mv spark-3.5.0-bin-hadoop3 /opt/spark
	rm spark-3.5.0-bin-hadoop3.tgz

install-python3:
	sudo yum install -y python3
	sudo unlink /usr/bin/python
	sudo ln -s /usr/bin/python3 /usr/bin/python
 
start-namenode:
	hdfs namenode
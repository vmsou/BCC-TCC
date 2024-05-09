FROM ubuntu:22.04

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y wget default-jre

WORKDIR /opt

# Instalar: Hadoop
RUN wget https://dlcdn.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz && \
    tar -xzf hadoop-3.4.0.tar.gz && \
    rm hadoop-3.4.0.tar.gz && \
    mv ./hadoop-3.4.0 ./hadoop

# Configurar: Hadoop
RUN mkdir -p /opt/hdfs/datanode
RUN mkdir -p /opt/hdfs/namenode
COPY hadoop-config/* /opt/hadoop/etc/hadoop/
RUN /opt/hadoop/bin/hdfs namenode -format

# Instalar: Spark
#RUN wget https://dlcdn.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz && \
#    tar -xzf spark-3.5.1-bin-hadoop3.tgz && \
#    rm spark-3.5.1-bin-hadoop3.tgz && \
#    mv ./spark-3.5.1-bin-hadoop3 ./spark


# Configurar: Spark
#COPY spark-config/* /opt/spark/conf/

# Copie o arquivo de configuração do Hadoop para o contêiner
#COPY ./hadoop-config/core-site.xml /opt/spark/conf/
#COPY ./hadoop-config/hdfs-site.xml /opt/spark/conf/

# Copie o código Spark para o contêiner
#COPY ./spark-app /app

# Define o diretório de trabalho no contêiner
#WORKDIR /app

# Configurações adicionais, como instalação de dependências e comandos de inicialização, podem ser adicionadas aqui""""

# Expor: Portas
EXPOSE 9870 9000

CMD ["/opt/hadoop/sbin/start-dfs.sh"]
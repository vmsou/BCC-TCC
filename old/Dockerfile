FROM ubuntu:22.04
USER root

ARG HADOOP_VERSION=3.4.0
ARG HADOOP_URL=https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
ENV HADOOP_HOME=/home/hadoop/hadoop

ARG SPARK_VERSION=3.5.1
ARG SPARK_URL=https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz
ENV SPARK_HOME=/home/hadoop/spark

RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker

WORKDIR /tmp

RUN apt-get update && \
    apt-get install -y \
    sudo \
    nano \
    neovim \
    openssh-server \
    wget \
    python3 \
    default-jre

RUN rm -rf /var/lib/apt/lists/*

RUN groupadd hadoop
RUN useradd -d /home/hadoop -g hadoop -m hadoop --shell /bin/bash

# Configurar: SSH
RUN mkdir /home/hadoop/.ssh
RUN ssh-keygen -t rsa -f /home/hadoop/.ssh/id_rsa -P '' && \
    cat /home/hadoop/.ssh/id_rsa.pub >> /home/hadoop/.ssh/authorized_keys

# Instalar: Hadoop
RUN wget $HADOOP_URL
RUN tar -xzf hadoop-${HADOOP_VERSION}.tar.gz && \
    mv hadoop-${HADOOP_VERSION} /home/hadoop/hadoop


# Configurar: Hadoop
#ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
#COPY hadoop-config/* /home/hadoop/hadoop/etc/hadoop/
#RUN mkdir -p /home/hadoop/hdfs/datanode &&  \
#    mkdir -p /home/hadoop/hdfs/namenode

# Instalar: Spark
RUN wget $SPARK_URL
RUN tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop3 /home/hadoop/spark

# Configurar: Spark
COPY spark-config/* /home/hadoop/spark/conf/

#RUN /home/hadoop/hadoop/bin/hdfs namenode -format
RUN rm -rf /tmp/*

# Portas
WORKDIR /root

EXPOSE 9870 9000 8088

COPY entrypoint.sh /usr/local/sbin/entrypoint.sh
RUN sudo chmod +x /usr/local/sbin/entrypoint.sh

# ENTRYPOINT ["entrypoint.sh"]
ENTRYPOINT [ "bash" ]
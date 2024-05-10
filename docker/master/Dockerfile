FROM apache/hadoop:3.3.6

RUN wget https://dlcdn.apache.org/spark/spark-3.5.1/spark-3.5.1-bin-hadoop3.tgz --no-check-certificate
RUN tar -xzf spark-3.5.1-bin-hadoop3.tgz && \
    mv spark-3.5.1-bin-hadoop3 /opt/spark && \
    rm spark-3.5.1-bin-hadoop3.tgz
    
RUN sudo yum install -y python3
RUN sudo unlink /usr/bin/python
RUN sudo ln -s /usr/bin/python3 /usr/bin/python

ENV PATH="${PATH}:/opt/spark/bin"
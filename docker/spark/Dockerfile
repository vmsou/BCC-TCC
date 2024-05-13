FROM bitnami/spark:3.4.3

USER root

COPY /bin/* /opt/bitnami/spark/bin/
RUN chmod +x /opt/bitnami/spark/bin/pyspark

COPY /.ivy2.tar.gz /opt/bitnami/spark/
RUN tar -xzf /opt/bitnami/spark/.ivy2.tar.gz #&& rm .ivy2.tar.gz

USER 1001
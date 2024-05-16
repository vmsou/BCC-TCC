FROM bitnami/spark:3.5.1

USER root

RUN pip install --no-cache numpy

COPY /bin/* /opt/bitnami/spark/bin/
RUN chmod +x /opt/bitnami/spark/bin/*

COPY /.ivy2.tar.gz /opt/bitnami/spark/
RUN tar -xzf /opt/bitnami/spark/.ivy2.tar.gz && rm .ivy2.tar.gz

USER 1001
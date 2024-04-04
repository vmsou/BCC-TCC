FROM python:3.9-slim-buster

RUN mkdir -p /home/notebooks
WORKDIR /home/notebooks

RUN pip install --upgrade pip

RUN pip install numpy \
                pandas \
                scikit-learn \
                seaborn \
                matplotlib \
                jupyter \
                notebook

EXPOSE 8888

ENTRYPOINT [ "jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--no-browser" ]
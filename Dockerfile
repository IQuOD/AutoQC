FROM ubuntu:18.04

# configure environment for install
RUN apt-get update
RUN apt-get install -y git

# install AutoQC and all deps
COPY . /AutoQC/
WORKDIR /AutoQC
RUN sed -i -e 's/sudo //g' install.sh
RUN chmod 777 install.sh
RUN ./install.sh

# set default environment variables
ENV OCEANSDB_DIR /AutoQC/data/

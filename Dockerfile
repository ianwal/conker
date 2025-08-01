FROM ubuntu:24.04 AS build

ENV DEBIAN_FRONTEND=noninteractive

COPY /packages.txt /

RUN apt-get update && apt-get install -y $(cat /packages.txt)

RUN mkdir /conker
WORKDIR /conker

# Ubuntu tries to prevent installing pip packages locally, so we make
# a venv install packages there.
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /conker
RUN python3 -m pip install -r /conker/requirements.txt --no-cache-dir

COPY .bash_aliases /root/.bash_aliases

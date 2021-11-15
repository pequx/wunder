# syntax = docker/dockerfile:experimental

FROM python:3.10.0-slim-buster as base
ENV HUNDI_ENVIRONMENT=base
USER root
RUN apt-get -qqy update && \
    apt-get -qqy install wait-for-it && \
    apt-get -qqy install make && \
    apt-get -qqy install build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN useradd -d /home/app -m -s /bin/sh app
RUN install -d -o app -g app /app

ENV PYTHONPATH=/app
ENV PATH=/home/app/.local/bin:/usr/local/bin:/usr/bin:/bin

USER app
WORKDIR /app



FROM base as build
ENV HUNDI_ENVIRONMENT=build
ADD requirements.txt ./
RUN pip install -r requirements.txt



FROM base as development
ENV HUNDI_ENVIRONMENT=development
ADD requirements.txt ./
ADD requirements-dev.txt ./
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt
USER root
RUN chmod 0777 cli.py
USER app
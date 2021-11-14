# syntax = docker/dockerfile:experimental

FROM python:3.9.8-alpine3.14 AS base
ENV HUNDI_ENVIRON=base
USER root
RUN apt-get -qqy update && \
    apt-get -qqy install wait-for-it && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN useradd -d /home/app -m -s /bin/bash app && \
    install -d -o app -g app /app

WORKDIR /app

ENV PYTHONPATH=/app
ENV PATH=/home/app/.local/bin:/usr/local/bin:/usr/bin:/bin


FROM base as build
ENV HUNDI_ENVIRON=build
USER app
ADD requirements.txt ./
RUN pip install -r requirements.txt


FROM base as development
ENV HUNDI_ENVIRON=development
USER app
ADD requirements.txt ./
RUN pip install -r requirements.txt
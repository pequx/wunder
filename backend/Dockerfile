# syntax = docker/dockerfile:experimental

FROM python:3.9.7-slim-buster as base
ENV HUNDI_ENVIRONMENT=base
USER root
RUN apt-get -qqy update && \
    apt-get -qqy install wait-for-it && \
    apt-get -qqy install make && \
    apt-get -qqy install build-essential && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN useradd -d /home/app -m -r app
RUN chown app /home/app
RUN install -d -o app -g app /app
RUN chown app /app

ENV PATH=/home/app/.local/bin:/usr/local/bin:/usr/bin:/bin:/app:/app/hundi


FROM base as build
ENV HUNDI_ENVIRONMENT=build
USER app
ADD ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt


FROM build as development
ENV HUNDI_ENVIRONMENT=development
USER app
ADD ./requirements-dev.txt /app/requirements-dev.txt
WORKDIR /app
RUN pip install -r requirements-dev.txt
COPY . .
USER root
RUN chmod 0777 ./cli.py
USER app
ENTRYPOINT ["./cli.py", "--debug", "observe"]
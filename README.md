# Wunder

This repository provides a Kubernetes infrastructure configuration and the necessary codebase required for collecting and near-real-time data-series processing for high-frequency cryptocurrencies trading.

## Background

Wunder was developed for research and training purposes. At some point, it has become clear that Cryptohopper provides virtually everything one may require for algorithmically enhanced and data-driven trading.

Wunder's infrastructure incorporates a proven technological stack:

- Apache Cassandara, an open-source NoSQL distributed database – ensures optimal performance and state of the art processing capabilities.
- KairosDB, a client Java library utilising the HttpClient class – causes sending metrics and querying the server as a simple task.
- Jupyter, a web-based interactive development environment for notebooks, code, and data – useful for running simulations, processing large datasets and solving mathematical formulas.
- Grafana, a log aggregation and storage system – visualises the collected data.

The codebase incorporates the asyncio and multi-threaded design patterns over Python 3.9 – we focus on its intrinsic data structures and utilise the WebSocket connector.

## Composition

### Data transformation

The data transformation layer originates on Numpy and Pandas libraries.

They provide respectively:
- support for large, multi-dimensional arrays and matrices, along with patterns for collecting high-level mathematical functions
- fast, powerful, flexible and easy to use open-source data analysis and manipulation tool

### Backend

The backend is composed of the following modules:
- Action module – containing action definitions for the command line interface's initialiser
- Config module – containing settings and necessary configuration for the KairosDB queries and data formulation
- Controler module – containing WebSocket authentication handler along with the order and ticker data processors. It handles the WebSocket message validation, data transformations and provides error handling.
- Lib module – containing WebSocket's executor and helper methods for KairosDB data processing and querying asynchronously.
- Model module – contains data models.
- Reader and Writer modules – contains classes for asynchronous data reading and writing.
- Test module – contains the initial testing configuration.

### Command-line Interface

In order to provide command-line support, we utilise the Click library.

### Makefile

### Docker build system

Docker-based backend build system provides flexibility over the experimental syntax – especially for separating development and production environments. Its configuration allows persistent volume delegation: changes to our local codebase mirror ones in the running container.

## Configuration

Before starting Kubernetes orchestration, configuration, and subsequent Docker build, we must provide the necessary environment and secret files.

In the repository root, please create the following files:

### .cassandra.env

The config map will generate Cassandra enviromental variables over the shell script.
Additional variables may be included in this file.

```
CASSANDRA_SEEDS=cassandra-0.cassandra.backend.svc.cluster.local
CASSANDRA_CLUSTER_NAME=<name>
CASSANDRA_DC=<dc_name>
CASSANDRA_RACK=<rack_name>
MALLOC_ARENA_MAX=4
MAX_HEAP_SIZE=512M
HEAP_NEWSIZE=100M
```

We are going to adjust Java heap memory area and allocation variables later in accordance with post start script generated values - it will improve the performance.

### .kairosdb.env

The config map will generate KairosDB enviromental variables over the shell script.
Additional variables may be included in this file.

```
KAIROSDB_SAMPLE_VARIABLE=0
```

### .jupyter.env
```
JUPYTER_ENABLE_LAB=True
JUPYTER_AUTO_RELOAD=True
```

### .hundi.env
```
KAIROSDB_URL=http://localhost:8080
KAIROSDB_API_DATAPOINTS=/api/v1/datapoints
KAIROSDB_TTL=473040000
HUNDI_LOG_PATH=/home/hundi/logs/hundi.log
HUNDI_LOG_QUEUE_MAX_SIZE=100
HUNDI_LOG_UPDATE_INTERVAL=0.5
HUNDI_LOG_MAX_LINES=1000
```

### .secret.cassandra.env
```
CASSANDRA_USER=<username>
CASSANDRA_PASSWORD=<password>
```

### .secret.grafana.env
```
GF_SECURITY_ADMIN_PASSWORD=<password>
```

### .secret.jupyter.env
```
JUPYTER_TOKEN=<token>
```

## Setup: Infrastructure as-a-code

```
$ make backend-namespace
$ make frontend-namespace
$ make cassandra
$ make kairosdb
```

## Setup: Local development

Please switch your location to backend located in the repository root.
You may consider using pipx for running and managing your development enviroment in a isolated manner.

https://pypi.org/project/pipx/

Before we proceed an virtal enviroment

```
$ pipx install virtualenv
$ make hundi-venv-install
$ make hundi-venv-bootstrap
$ make hundi-install
```

If you use Visual Studio Code please also run the debugger, linting and tests enviroment setup.
```
$ make hundi-vscode-bootstrap
```

## Build: Docker development build

Please switch your location to backend located in the repository root.

```
$ make hundi-up
```

Please refer to Makefile for more commands.

## Debugging

Please use the make command as follows:
```
$ make hundi-debug file=<file> args=<args>
```

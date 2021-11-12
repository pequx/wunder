CONFIG_CASSANDRA =? cassandra

SECRET_CASSANDRA =? cassandra
SECRET_GRAFANA =? grafana

ENV_CASSANDRA := "./.cassandra.env"
ENV_SECRET_CASSANDRA := "./.secret.cassandra.env"
ENV_SECRET_GRAFANA := "./.secret.grafana.env"

NAMESPACE_BACKEND ?= backend

KUBI := kubectl --namespace $(NAMESPACE)

bootstrap-venv:
	virtualenv -p `which python3.10` venv

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} \;

clean-build:
	rm --force --recursive build/ 
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

### CASANDRA

cassandra-secret:
	$(KUBI) create secret generic $(SECRET_CASSANDRA) --from-env-file=$(ENV_SECRET_CASSANDRA)

cassandra-config:
	$(KUBI) create configmap $(CONFIG_CASSANDRA) --from-env-file=$(ENV_CASSANDRA)

cassandra-storage:
	$(KUBI) apply -f ./k8s/cassandra.storageClass.yaml

cassandra-volume:
	$(KUBI) apply -f ./k8s/cassandra.persistentVolumeClaim.yaml

cassandra-service:
	$(KUBI) apply -f ./k8s/cassandra.service.yaml

cassandra-deployment:
	$(KUBI) apply -f ./k8s/cassandra.statefulSet.yaml

### GRAFANA

grafana-secret:
	$(KUBI) create secret generic $(SECRET_GRAFANA) --from-env-file=$(ENV_SECRET_GRAFANA)

grafana-volume:
	$(KUBI) apply -f ./k8s/grafana.persistentVolumeClaim.yaml

grafana-service:
	$(KUBI) apply -f ./k8s/grafana.service.yaml

grafana-deployment:
	$(KUBI) apply -f ./k8s/grafana.deployment.yaml

### KAIROSDB

kairosdb-config:
	$(KUBI) apply -f ./k8s/kairosdb.configMap.yaml

kairosdb-service:
	$(KUBI) apply -f ./k8s/kairosdb.service.yaml

kairosdb-deployment:
	$(KUBI) apply -f ./k8s/kairosdb.deployment.yaml
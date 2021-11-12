CONFIG_CASSANDRA ?= cassandra

SECRET_CASSANDRA ?= cassandra
SECRET_GRAFANA ?= grafana

ENV_CASSANDRA := "./.cassandra.env"
ENV_SECRET_CASSANDRA := "./.secret.cassandra.env"
ENV_SECRET_GRAFANA := "./.secret.grafana.env"

NAMESPACE_BACKEND ?= backend

KUBI_BACKEND := kubectl --namespace $(NAMESPACE_BACKEND)

bootstrap-venv:
	virtualenv -p `which python3.10` venv

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} \;

clean-build:
	rm --force --recursive build/ 
	rm --force --recursive dist/
	rm --force --recursive *.egg-info


## BACKEND
backend-namespace:
	$(KUBI_BACKEND) create namespace $(NAMESPACE_BACKEND) 

backend-namespace-clean:
	$(KUBI_BACKEND) delete namespace $(NAMESPACE_BACKEND) 


### CASANDRA

cassandra-secret:
	$(KUBI_BACKEND) create secret generic $(SECRET_CASSANDRA) --from-env-file=$(ENV_SECRET_CASSANDRA)

cassandra-secret-clean:
	$(KUBI_BACKEND) delete secret $(SECRET_CASSANDRA)

cassandra-account:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/cassandra.serviceAccount.yaml

cassandra-account-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/cassandra.serviceAccount.yaml

cassandra-config:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/cassandra.configMap.yaml
	$(KUBI_BACKEND) create configmap $(CONFIG_CASSANDRA) --from-env-file=$(ENV_CASSANDRA)

cassandra-config-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/cassandra.configMap.yaml
	$(KUBI_BACKEND) delete configmap $(CONFIG_CASSANDRA)

cassandra-storage:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/cassandra.storageClass.yaml

cassandra-storage-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/cassandra.storageClass.yaml

# cassandra-volume:
# 	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/cassandra.persistentVolumeClaim.yaml

# cassandra-volume-clean:
# 	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/cassandra.persistentVolumeClaim.yaml

cassandra-service:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/cassandra.service.yaml

cassandra-service-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/cassandra.service.yaml

cassandra-deployment:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/cassandra.statefulSet.yaml

cassandra-deployment-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/cassandra.statefulSet.yaml


### KAIROSDB

kairosdb-config:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.configMap.yaml

kairosdb-config-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.configMap.yaml

kairosdb-account:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.serviceAccount.yaml

kairosdb-account-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.serviceAccount.yaml

kairosdb-service:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.service.yaml

kairosdb-service-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.service.yaml

kairosdb-deployment:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.deployment.yaml

kairosdb-deployment-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/kairosdb.deployment.yaml


### GRAFANA

grafana-secret:
	$(KUBI_BACKEND) create secret generic $(SECRET_GRAFANA) --from-env-file=$(ENV_SECRET_GRAFANA)

grafana-secret-clean:
	$(KUBI_BACKEND) delete secret $(SECRET_GRAFANA)

grafana-account:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.serviceAccount.yaml

grafana-account-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.serviceAccount.yaml

grafana-volume:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.persistentVolumeClaim.yaml

grafana-volume-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.persistentVolumeClaim.yaml

grafana-service:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.service.yaml

grafana-service-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.service.yaml

grafana-deployment:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.deployment.yaml

grafana-deployment-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.deployment.yaml
CONFIG_CASSANDRA ?= cassandra
CONFIG_JUPYTER ?= jupyter

SECRET_CASSANDRA ?= cassandra
SECRET_GRAFANA ?= grafana
SECRET_JUPYTER ?= jupyter

ENV_CASSANDRA := "./.cassandra.env"
ENV_JUPYTER := "./.jupyter.env"

ENV_SECRET_CASSANDRA := "./.secret.cassandra.env"
ENV_SECRET_GRAFANA := "./.secret.grafana.env"
ENV_SECRET_JUPYTER := "./.secret.jupyter.env"

NAMESPACE_BACKEND ?= backend
NAMESPACE_FRONTEND ?= frontend

KUBI_BACKEND := kubectl --namespace $(NAMESPACE_BACKEND)
KUBI_FRONTEND := kubectl --namespace $(NAMESPACE_FRONTEND)

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
	kubectl create namespace $(NAMESPACE_BACKEND) 

backend-namespace-clean:
	kubectl delete namespace $(NAMESPACE_BACKEND) 

frontend-namespace:
	kubectl create namespace $(NAMESPACE_FRONTEND) 

frontend-namespace-clean:
	kubectl delete namespace $(NAMESPACE_FRONTEND) 


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

cassandra:
	make cassandra-secret
	make cassandra-account
	make cassandra-config
	make cassandra-storage
	make cassandra-service
	make cassandra-deployment

cassandra-clean:
	make cassandra-secret-clean
	make cassandra-account-clean
	make cassandra-config-clean
	make cassandra-storage-clean
	make cassandra-service-clean
	make cassandra-deployment-clean


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

kairosdb:
	make kairosdb-config
	make kairosdb-account
	make kairosdb-service
	make kairosdb-deployment

kairosdb-clean:
	make kairosdb-config-clean
	make kairosdb-account-clean
	make kairosdb-service-clean
	make kairosdb-deployment-clean


### GRAFANA

grafana-secret:
	$(KUBI_BACKEND) create secret generic $(SECRET_GRAFANA) --from-env-file=$(ENV_SECRET_GRAFANA)

grafana-secret-clean:
	$(KUBI_BACKEND) delete secret $(SECRET_GRAFANA)

grafana-account:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.serviceAccount.yaml

grafana-account-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.serviceAccount.yaml

grafana-service:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.service.yaml

grafana-service-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.service.yaml

grafana-volume:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.persistentVolumeClaim.yaml

grafana-volume-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.persistentVolumeClaim.yaml

grafana-deployment:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/grafana.deployment.yaml

grafana-deployment-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/grafana.deployment.yaml

grafana:
	make grafana-secret
	make grafana-account
	make grafana-service
	make grafana-volume
	make grafana-deployment

grafana-clean:
	make grafana-secret-clean
	make grafana-account-clean
	make grafana-service-clean
	# make grafana-volume-clean
	make grafana-deployment-clean


### JUPYTER

jupyter-secret:
	$(KUBI_BACKEND) create secret generic $(SECRET_JUPYTER) --from-env-file=$(ENV_SECRET_JUPYTER)

jupyter-secret-clean:
	$(KUBI_BACKEND) delete secret $(SECRET_JUPYTER)

jupyter-config:
	$(KUBI_BACKEND) create configmap $(CONFIG_JUPYTER) --from-env-file=$(ENV_JUPYTER)

jupyter-config-clean:
	$(KUBI_BACKEND) delete configmap $(CONFIG_JUPYTER)

jupyter-account:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/jupyter.serviceAccount.yaml

jupyter-account-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/jupyter.serviceAccount.yaml

jupyter-service:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/jupyter.service.yaml

jupyter-service-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/jupyter.service.yaml

jupyter-deployment:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/jupyter.deployment.yaml

jupyter-deployment-clean:
	$(KUBI_BACKEND) delete -f ./k8s/${NAMESPACE_BACKEND}/jupyter.deployment.yaml

jupyter-volume:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/jupyter.volume.yaml

jupyter-volume-clean:
	$(KUBI_BACKEND) apply -f ./k8s/${NAMESPACE_BACKEND}/jupyter.volume.yaml

jupyter:
	make jupyter-secret
	make jupyter-config
	make jupyter-account
	make jupyter-service
	make jupyter-volume
	make jupyter-deployment

jupyter-clean:
	make jupyter-secret-clean
	make jupyter-config-clean
	make jupyter-account-clean
	make jupyter-service-clean
	make jupyter-deployment-clean
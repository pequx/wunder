NAMESPACE ?= hundi
NETWORK ?= main
IMAGE ?= python/python:3.10.0-alpine3.14

DOCKER_BUILD := DOCKER_BUILDKIT=1 docker build
COMPOSE := docker-compose --project-name $(NAMESPACE)
REMOVE_NETWORK := docker newtork rm $(NETWORK)

hundi-venv-bootstrap:
	virtualenv -p `pyenv which python3.10` venv
	venv/bin/python -m pip install --upgrade pip

# hundi-venv-activate:
# 	source venv/bin/activate

# hundi-venv-deactivate:
# 	deactivate
# 	rm -r venv

hundi-vscode-bootstrap:
	mkdir ../../.vscode
	cp .vscode.settings.json ../../.vscode/settings.json

hundi-up:
	$(COMPOSE) up

hundi-stop:
	$(COMPOSE) stop

hundi-own:
	$(COMPOSE) down

hundi-clean:
	$(COMPOSE) down -v --remove-orphans

hundi-network-clean:
	$(REMOVE_NETWORK)

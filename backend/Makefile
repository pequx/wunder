NAMESPACE ?= hundi
NETWORK ?= main
IMAGE ?= python/python:3.10.0-alpine3.14

DOCKER_BUILD := DOCKER_BUILDKIT=1 docker build
COMPOSE := docker-compose --project-name $(NAMESPACE)
REMOVE_NETWORK := docker newtork rm $(NETWORK)

hundi-venv-bootstrap:
	pyenv local 3.9.7
	virtualenv -p `pyenv which python` venv
	venv/bin/python -m pip install --upgrade pip

# hundi-venv-activate:
# 	source venv/bin/activate

# hundi-venv-deactivate:
# 	deactivate
# 	rm -r venv

hundi-vscode-bootstrap:
	mkdir ../../.vscode
	cp .vscode.settings.json ../../.vscode/settings.json
	cp .vscode.launch.json ../../.vscode/launch.json

debug-python:
	venv/bin/python3.9 -m debugpy --listen 5678 --wait-for-client $(file) $(args)

hundi-up:
	$(COMPOSE) up

hundi-stop:
	$(COMPOSE) stop

hundi-down:
	$(COMPOSE) down

hundi-clean:
	$(COMPOSE) down -v --remove-orphans

hundi-network-clean:
	$(REMOVE_NETWORK)

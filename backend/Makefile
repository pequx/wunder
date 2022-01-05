NAMESPACE ?= hundi
NETWORK ?= main
IMAGE ?= python/python:3.10.0-alpine3.14

DOCKER_BUILD := DOCKER_BUILDKIT=1 docker build
COMPOSE := docker-compose --project-name $(NAMESPACE)
REMOVE_NETWORK := docker newtork rm $(NETWORK)

hundi-venv-install:
	pyenv install 3.9.7

hundi-venv-bootstrap:
	pyenv local 3.9.7
	virtualenv -p `pyenv which python` venv
	venv/bin/python -m pip install --upgrade pip

hundi-install:
	venv/bin/python -m pip install -r requirements.txt
	venv/bin/python -m pip install -r requirements-dev.txt

# hundi-venv-activate:
# 	source venv/bin/activate

# hundi-venv-deactivate:
# 	deactivate
# 	rm -r venv

hundi-vscode-bootstrap:
	cp vscode.settings.json ../.vscode/settings.json
	cp vscode.launch.json ../.vscode/launch.json

hundi-debug:
	venv/bin/python3.9 -m debugpy --listen 5678 --wait-for-client $(file) $(args)

hundi-up:
	$(COMPOSE) up

hundi-stop:
	$(COMPOSE) stop

hundi-down:
	$(COMPOSE) down

hundi-build:
	$(COMPOSE) build

hundi-rebuild:
	$(COMPOSE) up --build

hundi-clean:
	$(COMPOSE) down -v --remove-orphans

hundi-network-clean:
	$(REMOVE_NETWORK)

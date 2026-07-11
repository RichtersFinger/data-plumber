SHELL := /bin/bash
PWD := ${shell pwd}

PYTHON_CONTAINER_NAME := data-plumber-dev
PYTHON_CONTAINER_START := docker run --rm -t -d \
	-v "${PWD}:${PWD}" \
	-w "${PWD}" \
	-e PYTHONUSERBASE=/tmp/docker-python-base \
	-e PIP_NO_CACHE_DIR=true \
	--user ${shell id -u}:${shell id -g} \
	--name ${PYTHON_CONTAINER_NAME} \
	python:3.12.13-alpine@sha256:aa679aa4eed6eb56c1dc6ad3f1b98b7d2d788fd961596779d188fdedad97fb38 \
	sleep infinity
PYTHON_CONTAINER_RUNNING := docker ps -q -f name=$(PYTHON_CONTAINER_NAME)
PYTHON_SHELL := docker exec -it ${PYTHON_CONTAINER_NAME}

up:
	@if [ -z "$$(${PYTHON_CONTAINER_RUNNING})" ]; then \
		$(PYTHON_CONTAINER_START) > /dev/null; \
		until [ -n "$$($(PYTHON_CONTAINER_RUNNING))" ]; do printf "."; sleep 0.2; done; \
		echo " Ready."; \
	fi

down:
	@if [ -n "$$($(PYTHON_CONTAINER_RUNNING))" ]; then \
		docker kill $(PYTHON_CONTAINER_NAME); \
	fi

shell: up
	${PYTHON_SHELL} sh

install: up
	${PYTHON_SHELL} pip install .

test: up
	${PYTHON_SHELL} sh -c "pip install -r test_data_plumber/test_requirements.txt && /tmp/docker-python-base/bin/pytest $(ARGS)"

build-dist: up
	${PYTHON_SHELL} sh -c "pip install wheel==0.47.0 setuptools==82.0.1 && python3 setup.py sdist bdist_wheel"

publish: up
	${PYTHON_SHELL} sh -c "pip install --upgrade pip twine==6.2.0 && python3 -m twine upload dist/*"

clean:
	@echo "The following files/directories will be permanently removed:"
	@git clean -dfXn
	@echo "--------------------------------------------------"
	@read -p "Are you sure you want to proceed? [y/N]: " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		git clean -dfX; \
		echo "Cleanup complete."; \
	else \
		echo "Cleanup aborted."; \
		exit 1; \
	fi

SHELL := /bin/bash

COMMON_DOCKER_COMPOSE := common.yaml
PYTHON_DOCKER_COMPOSE := python/docker-compose.yaml
PYTHON_OTEL_DOCKER_COMPOSE := python/docker-compose-otel.yaml
GO_DOCKER_COMPOSE := go/docker-compose.yaml
GO_OTEL_DOCKER_COMPOSE := go/docker-compose-otel.yaml

# Function to build docker-compose
define docker_build
	docker-compose -f $(COMMON_DOCKER_COMPOSE) -f $1 build --no-cache
endef

# Function to run docker-compose
define docker_compose
	docker-compose -f $(COMMON_DOCKER_COMPOSE) -f $1 up --force-recreate $(if $2,$2,)
endef

# All
all: python-all go-all

# Python targets
python-build:
	$(call docker_build,$(PYTHON_DOCKER_COMPOSE))

python-compose:
	$(call docker_compose,$(PYTHON_DOCKER_COMPOSE),-d)

python-build-otel:
	$(call docker_build,$(PYTHON_OTEL_DOCKER_COMPOSE))

python-compose-otel:
	$(call docker_compose,$(PYTHON_OTEL_DOCKER_COMPOSE),-d)

python-all: python-compose python-compose-otel

# Go targets
go-build:
	$(call docker_build,$(GO_DOCKER_COMPOSE))

go-compose:
	$(call docker_compose,$(GO_DOCKER_COMPOSE))

go-build-otel:
	$(call docker_build,$(GO_OTEL_DOCKER_COMPOSE)-d)

go-compose-otel:
	$(call docker_compose,$(GO_OTEL_DOCKER_COMPOSE)-d)

go-all: go-build go-build-otel go-compose go-compose-otel


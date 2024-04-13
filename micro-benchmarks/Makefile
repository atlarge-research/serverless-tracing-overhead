SHELL := /bin/bash

DOCKER_COMPOSE_FOLDER         := docker-compose
JAEGER_DOCKER_COMPOSE         := $(DOCKER_COMPOSE_FOLDER)/jaeger.yaml
ELASTIC_DOCKER_COMPOSE        := $(DOCKER_COMPOSE_FOLDER)/telemetry.yaml
POSTGRES_DOCKER_COMPOSE       := $(DOCKER_COMPOSE_FOLDER)/postgres.yaml
# Python
PYTHON_DOCKER_COMPOSE         := python/docker-compose.yaml
PYTHON_OTEL_DOCKER_COMPOSE    := python/docker-compose-otel.yaml
PYTHON_ELASTIC_DOCKER_COMPOSE := python/docker-compose-elastic.yaml
# Go
GO_DOCKER_COMPOSE             := go/docker-compose.yaml
GO_OTEL_DOCKER_COMPOSE        := go/docker-compose-otel.yaml
GO_ELASTIC_DOCKER_COMPOSE     := go/docker-compose-elastic.yaml
# Java
JAVA_DOCKER_COMPOSE           := java/docker-compose.yaml

# Function to build docker-compose
define docker_build
	docker-compose -f $1 build --no-cache
endef

# Function to run docker-compose
define docker_compose
	docker-compose -f $1 up --force-recreate $(if $2,$2,)
endef

# All
all: psql jaeger python-all go-all

psql:
	$(call docker_compose,$(POSTGRES_DOCKER_COMPOSE),-d)

jaeger:
	$(call docker_compose,$(JAEGER_DOCKER_COMPOSE),-d)

elastic:
	$(call docker_compose,$(ELASTIC_DOCKER_COMPOSE),-d)

# Python targets
python-build:
	$(call docker_build,$(PYTHON_DOCKER_COMPOSE))

python:
	$(call docker_compose,$(PYTHON_DOCKER_COMPOSE),-d)

python-build-otel:
	$(call docker_build,$(PYTHON_OTEL_DOCKER_COMPOSE))

python-otel:
	$(call docker_compose,$(PYTHON_OTEL_DOCKER_COMPOSE),-d)

python-all: python-build python-build-otel python python-otel

# Go targets
go-build:
	$(call docker_build,$(GO_DOCKER_COMPOSE))

go-compose:
	$(call docker_compose,$(GO_DOCKER_COMPOSE),-d)

go-build-otel:
	$(call docker_build,$(GO_OTEL_DOCKER_COMPOSE))

go-otel:
	$(call docker_compose,$(GO_OTEL_DOCKER_COMPOSE),-d)

go-otel: go-build-otel go-otel

go-all: go-build go-build-otel go-compose go-otel

# Elastic
python-elastic:
	$(call docker_compose,$(PYTHON_ELASTIC_DOCKER_COMPOSE),-d)

python-elastic-build:
	$(call docker_build,$(PYTHON_ELASTIC_DOCKER_COMPOSE))

go-elastic:
	$(call docker_compose,$(GO_ELASTIC_DOCKER_COMPOSE),-d)

go-elastic-build:
	$(call docker_build,$(GO_ELASTIC_DOCKER_COMPOSE))

# Java
java-spring:
	$(call docker_compose,$(JAVA_DOCKER_COMPOSE),-d)

java-spring-build:
	$(call docker_build,$(JAVA_DOCKER_COMPOSE))
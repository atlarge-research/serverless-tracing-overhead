SHELL := /bin/bash

.PHONY: all app-all psql jaeger elastic python-all python python-otel python-elastic go-all go go-otel go-elastic java-all java-spring java-spring-otel java-spring-elastic

# Directories
DOCKER_COMPOSE_FOLDER         := docker-compose
PYTHON_FOLDER                 := python
GO_FOLDER                     := go
JAVA_FOLDER                   := java

# Docker Compose Files
POSTGRES_DOCKER_COMPOSE       := $(DOCKER_COMPOSE_FOLDER)/postgres.yaml
JAEGER_DOCKER_COMPOSE         := $(DOCKER_COMPOSE_FOLDER)/jaeger.yaml
ELASTIC_DOCKER_COMPOSE        := $(DOCKER_COMPOSE_FOLDER)/telemetry.yaml

PYTHON_DOCKER_COMPOSE         := $(PYTHON_FOLDER)/docker-compose.yaml
PYTHON_OTEL_DOCKER_COMPOSE    := $(PYTHON_FOLDER)/docker-compose-otel.yaml
PYTHON_ELASTIC_DOCKER_COMPOSE := $(PYTHON_FOLDER)/docker-compose-elastic.yaml

GO_DOCKER_COMPOSE             := $(GO_FOLDER)/docker-compose.yaml
GO_OTEL_DOCKER_COMPOSE        := $(GO_FOLDER)/docker-compose-otel.yaml
GO_ELASTIC_DOCKER_COMPOSE     := $(GO_FOLDER)/docker-compose-elastic.yaml

JAVA_DOCKER_COMPOSE           := $(JAVA_FOLDER)/docker-compose.yaml
JAVA_OTEL_DOCKER_COMPOSE      := $(JAVA_FOLDER)/docker-compose-otel.yaml
JAVA_ELASTIC_DOCKER_COMPOSE   := $(JAVA_FOLDER)/docker-compose-elastic.yaml

# Helper to build docker-compose
define docker_build
	@docker-compose -f $1 build --no-cache
endef

# Helper to run docker-compose
define docker_compose
	@docker-compose -f $1 up --force-recreate -d
endef


# All together
all: psql elastic app-all

app-all: python-all go-all java-all

psql:
	$(call docker_compose,$(POSTGRES_DOCKER_COMPOSE))

jaeger:
	$(call docker_compose,$(JAEGER_DOCKER_COMPOSE))

elastic:
	$(call docker_compose,$(ELASTIC_DOCKER_COMPOSE))

# Python Targets
python-all: python python-otel python-elastic

python:
	$(call docker_build,$(PYTHON_DOCKER_COMPOSE))
	$(call docker_compose,$(PYTHON_DOCKER_COMPOSE))

python-otel:
	$(call docker_build,$(PYTHON_OTEL_DOCKER_COMPOSE))
	$(call docker_compose,$(PYTHON_OTEL_DOCKER_COMPOSE))

python-elastic:
	$(call docker_build,$(PYTHON_ELASTIC_DOCKER_COMPOSE))
	$(call docker_compose,$(PYTHON_ELASTIC_DOCKER_COMPOSE))

# Go Targets
go-all: go go-otel go-elastic

go:
	$(call docker_build,$(GO_DOCKER_COMPOSE))
	$(call docker_compose,$(GO_DOCKER_COMPOSE))

go-otel:
	$(call docker_build,$(GO_OTEL_DOCKER_COMPOSE))
	$(call docker_compose,$(GO_OTEL_DOCKER_COMPOSE))

go-elastic:
	$(call docker_build,$(GO_ELASTIC_DOCKER_COMPOSE))
	$(call docker_compose,$(GO_ELASTIC_DOCKER_COMPOSE))

# Java Targets
java-all: java-spring java-spring-otel java-spring-elastic

java-spring:
	$(call docker_build,$(JAVA_DOCKER_COMPOSE))
	$(call docker_compose,$(JAVA_DOCKER_COMPOSE))

java-spring-otel:
	$(call docker_build,$(JAVA_OTEL_DOCKER_COMPOSE))
	$(call docker_compose,$(JAVA_OTEL_DOCKER_COMPOSE))

java-spring-elastic:
	$(call docker_build,$(JAVA_ELASTIC_DOCKER_COMPOSE))
	$(call docker_compose,$(JAVA_ELASTIC_DOCKER_COMPOSE))

# Help
help:
	@echo "Available commands:"
	@echo "  all                  - Run all services (Postgres, Jaeger, Elastic, and all app configurations)"
	@echo "  app-all              - Run all application configurations (Python, Go, Java)"
	@echo "  psql                 - Start the PostgreSQL service"
	@echo "  jaeger               - Start the Jaeger service"
	@echo "  elastic              - Start the Elastic service"
	@echo "  python-all           - Build and run all Python configurations (standard, OpenTelemetry, Elastic APM)"
	@echo "  python               - Build and run the standard Python Docker Compose setup"
	@echo "  python-otel          - Build and run the Python Docker Compose setup with OpenTelemetry"
	@echo "  python-elastic       - Build and run the Python Docker Compose setup with Elastic APM"
	@echo "  go-all               - Build and run all Go configurations (standard, OpenTelemetry, Elastic APM)"
	@echo "  go                   - Build and run the standard Go Docker Compose setup"
	@echo "  go-otel              - Build and run the Go Docker Compose setup with OpenTelemetry"
	@echo "  go-elastic           - Build and run the Go Docker Compose setup with Elastic APM"
	@echo "  java-all             - Build and run all Java configurations (standard, OpenTelemetry, Elastic APM)"
	@echo "  java-spring          - Build and run the standard Java Docker Compose setup"
	@echo "  java-spring-otel     - Build and run the Java Docker Compose setup with OpenTelemetry"
	@echo "  java-spring-elastic  - Build and run the Java Docker Compose setup with Elastic APM"

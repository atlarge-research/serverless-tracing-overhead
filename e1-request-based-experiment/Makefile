SHELL := /bin/bash

.PHONY: all benchmark app-all psql postgres jaeger telemetry rps-calibrator python-all python python-otel python-elastic go-all go go-otel go-elastic java-all java java-otel java-elastic

# Directories
TELEMETRY_FOLDER := telemetry
PYTHON_FOLDER    := python
GO_FOLDER        := go
JAVA_FOLDER      := java
JAVASCRIPT_FOLDER := javascript

# Docker Compose Files
POSTGRES_DOCKER_COMPOSE       := postgres/postgres.yaml
JAEGER_DOCKER_COMPOSE         := $(TELEMETRY_FOLDER)/jaeger.yaml
TELEMETRY_DOCKER_COMPOSE      := $(TELEMETRY_FOLDER)/telemetry.yaml

## Benchmark
BENCHMARK_DOCKER_COMPOSE      := benchmarker/docker/docker-compose.yaml

## Applications
PYTHON_DOCKER_COMPOSE         := $(PYTHON_FOLDER)/docker-compose.yaml
PYTHON_OTEL_DOCKER_COMPOSE    := $(PYTHON_FOLDER)/docker-compose-otel.yaml
PYTHON_ELASTIC_DOCKER_COMPOSE := $(PYTHON_FOLDER)/docker-compose-elastic.yaml

GO_DOCKER_COMPOSE             := $(GO_FOLDER)/docker-compose.yaml
GO_OTEL_DOCKER_COMPOSE        := $(GO_FOLDER)/docker-compose-otel.yaml
GO_ELASTIC_DOCKER_COMPOSE     := $(GO_FOLDER)/docker-compose-elastic.yaml

JAVA_DOCKER_COMPOSE           := $(JAVA_FOLDER)/docker-compose.yaml
JAVA_OTEL_DOCKER_COMPOSE      := $(JAVA_FOLDER)/docker-compose-otel.yaml
JAVA_ELASTIC_DOCKER_COMPOSE   := $(JAVA_FOLDER)/docker-compose-elastic.yaml

NODEJS_DOCKER_COMPOSE         := $(JAVASCRIPT_FOLDER)/docker-compose.yaml
NODEJS_OTEL_DOCKER_COMPOSE    := $(JAVASCRIPT_FOLDER)/docker-compose-otel.yaml
NODEJS_ELASTIC_DOCKER_COMPOSE := $(JAVASCRIPT_FOLDER)/docker-compose-elastic.yaml

CALIBRATOR_DOCKER_COMPOSE        := rps-calibrator/docker-compose.yaml
CALIBRATOR_NODEJS_DOCKER_COMPOSE := rps-calibrator/docker-compose-nodejs.yaml
CALIBRATOR_PYTHON_DOCKER_COMPOSE := rps-calibrator/docker-compose-python.yaml
CALIBRATOR_JAVA_DOCKER_COMPOSE := rps-calibrator/docker-compose-java.yaml
CALIBRATOR_GO_DOCKER_COMPOSE := rps-calibrator/docker-compose-go.yaml

# Helper to build docker-compose
define docker_build
	@docker compose -f $1 build --no-cache
endef

# Helper to run docker-compose
define docker_compose
	@docker compose -f $1 up --force-recreate -d
endef

define docker_down
	@docker compose -f $1 down --volumes --remove-orphans
endef


# All together
all: telemetry psql app-all

app-all: python-all go-all java-all

telemetry:
	$(call docker_compose,$(TELEMETRY_DOCKER_COMPOSE))

psql:
	$(call docker_build,$(POSTGRES_DOCKER_COMPOSE))
	$(call docker_compose,$(POSTGRES_DOCKER_COMPOSE))

postgres:
	$(call docker_build,$(POSTGRES_DOCKER_COMPOSE))
	$(call docker_compose,$(POSTGRES_DOCKER_COMPOSE))

jaeger:
	$(call docker_compose,$(JAEGER_DOCKER_COMPOSE))

# Benchmark
benchmark:
	$(call docker_build,$(BENCHMARK_DOCKER_COMPOSE))
	$(call docker_compose,$(BENCHMARK_DOCKER_COMPOSE))

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
java-all: java java-otel java-elastic

java:
	$(call docker_build,$(JAVA_DOCKER_COMPOSE))
	$(call docker_compose,$(JAVA_DOCKER_COMPOSE))

java-otel:
	$(call docker_build,$(JAVA_OTEL_DOCKER_COMPOSE))
	$(call docker_compose,$(JAVA_OTEL_DOCKER_COMPOSE))

java-elastic:
	$(call docker_build,$(JAVA_ELASTIC_DOCKER_COMPOSE))
	$(call docker_compose,$(JAVA_ELASTIC_DOCKER_COMPOSE))

nodejs:
	$(call docker_build,$(NODEJS_DOCKER_COMPOSE))
	$(call docker_compose,$(NODEJS_DOCKER_COMPOSE))

nodejs-otel:
	$(call docker_build,$(NODEJS_OTEL_DOCKER_COMPOSE))
	$(call docker_compose,$(NODEJS_OTEL_DOCKER_COMPOSE))

nodejs-elastic:
	$(call docker_build,$(NODEJS_ELASTIC_DOCKER_COMPOSE))
	$(call docker_compose,$(NODEJS_ELASTIC_DOCKER_COMPOSE))

rps-calibrator:
	$(call docker_build,$(CALIBRATOR_DOCKER_COMPOSE))
	$(call docker_compose,$(CALIBRATOR_DOCKER_COMPOSE))

rps-calibrator-nodejs:
	$(call docker_build,$(CALIBRATOR_NODEJS_DOCKER_COMPOSE))
	$(call docker_compose,$(CALIBRATOR_NODEJS_DOCKER_COMPOSE))

rps-calibrator-python:
	$(call docker_build,$(CALIBRATOR_NODEJS_DOCKER_COMPOSE))
	$(call docker_compose,$(CALIBRATOR_PYTHON_DOCKER_COMPOSE))

rps-calibrator-java:
	$(call docker_build,$(CALIBRATOR_NODEJS_DOCKER_COMPOSE))
	$(call docker_compose,$(CALIBRATOR_JAVA_DOCKER_COMPOSE))

rps-calibrator-go:
	$(call docker_build,$(CALIBRATOR_NODEJS_DOCKER_COMPOSE))
	$(call docker_compose,$(CALIBRATOR_GO_DOCKER_COMPOSE))

# Destroy all Docker Compose resources
destroy:
	$(call docker_down,$(TELEMETRY_DOCKER_COMPOSE))
	$(call docker_down,$(POSTGRES_DOCKER_COMPOSE))
	$(call docker_down,$(JAEGER_DOCKER_COMPOSE))
	$(call docker_down,$(PYTHON_DOCKER_COMPOSE))
	$(call docker_down,$(PYTHON_OTEL_DOCKER_COMPOSE))
	$(call docker_down,$(PYTHON_ELASTIC_DOCKER_COMPOSE))
	$(call docker_down,$(GO_DOCKER_COMPOSE))
	$(call docker_down,$(GO_OTEL_DOCKER_COMPOSE))
	$(call docker_down,$(GO_ELASTIC_DOCKER_COMPOSE))
	$(call docker_down,$(JAVA_DOCKER_COMPOSE))
	$(call docker_down,$(JAVA_OTEL_DOCKER_COMPOSE))
	$(call docker_down,$(JAVA_ELASTIC_DOCKER_COMPOSE))
	$(call docker_down,$(CALIBRATOR_DOCKER_COMPOSE))

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
	@echo "  java          - Build and run the standard Java Docker Compose setup"
	@echo "  java-otel     - Build and run the Java Docker Compose setup with OpenTelemetry"
	@echo "  java-elastic  - Build and run the Java Docker Compose setup with Elastic APM"

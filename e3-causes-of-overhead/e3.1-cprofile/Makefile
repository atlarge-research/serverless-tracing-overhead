# Makefile

EXPERIMENT_NAME ?= dynamic-html
START_MODE ?= cold

# Define the output directory for the flamegraphs and profiling files
OUTPUT_DIR ?= flamegraphs
PROFILE_DIR ?= profiles

# Ensure the output directories exist
$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

$(PROFILE_DIR):
	mkdir -p $(PROFILE_DIR)

# Define targets for each configuration
flamegraph-dynamic-html-cold: $(OUTPUT_DIR) $(PROFILE_DIR)
	EXPERIMENT_NAME=dynamic-html START_MODE=cold python main.py && \
	flameprof $(PROFILE_DIR)/workload-dynamic-html-cold.prof > $(OUTPUT_DIR)/flamegraph-dynamic-html-cold.svg

flamegraph-dynamic-html-warm: $(OUTPUT_DIR) $(PROFILE_DIR)
	EXPERIMENT_NAME=dynamic-html START_MODE=warm python main.py && \
	flameprof $(PROFILE_DIR)/workload-dynamic-html-warm.prof > $(OUTPUT_DIR)/flamegraph-dynamic-html-warm.svg

flamegraph-graph-pagerank-cold: $(OUTPUT_DIR) $(PROFILE_DIR)
	EXPERIMENT_NAME=graph-pagerank START_MODE=cold python main.py && \
	flameprof $(PROFILE_DIR)/workload-graph-pagerank-cold.prof > $(OUTPUT_DIR)/flamegraph-graph-pagerank-cold.svg

flamegraph-graph-pagerank-warm: $(OUTPUT_DIR) $(PROFILE_DIR)
	EXPERIMENT_NAME=graph-pagerank START_MODE=warm python main.py && \
	flameprof $(PROFILE_DIR)/workload-graph-pagerank-warm.prof > $(OUTPUT_DIR)/flamegraph-graph-pagerank-warm.svg

# Combined targets to run all configurations
flamegraphs: flamegraph-dynamic-html-cold flamegraph-dynamic-html-warm flamegraph-graph-pagerank-cold flamegraph-graph-pagerank-warm


dynamic-html-cold:
	docker compose -f docker-compose/dynamic-html-cold.yaml up -d

dynamic-html-warm:
	docker compose -f docker-compose/dynamic-html-warm.yaml up -d

graph-pagerank-cold:
	docker compose -f docker-compose/graph-pagerank-cold.yaml up -d

graph-pagerank-warm:
	docker compose -f docker-compose/graph-pagerank-warm.yaml up -d


.PHONY: flamegraph-dynamic-html-cold flamegraph-dynamic-html-warm flamegraph-graph-pagerank-cold flamegraph-graph-pagerank-warm flamegraphs dynamic-html-cold dynamic-html-warm graph-pagerank-cold graph-pagerank-warm

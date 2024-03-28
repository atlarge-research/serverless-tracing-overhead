SHELL := /bin/bash
DATE := $(shell date +%Y-%m-%d)
DATETIME := $(shell date +%Y-%m-%d_%H-%M)

export K6_WEB_DASHBOARD=true

RESULTS_DIR := results/$(DATE)
JSON_TEST := json
PLAINTEXT_TEST := plaintext
DB_TEST := db
QUERY_TEST := query

# Target-specific variable values
RESULT_FILE_PREFIX := testresults
python: RESULT_FILE_PREFIX := python
java: RESULT_FILE_PREFIX := java

define run_tests
	@mkdir -p $(RESULTS_DIR)/$(DATE)
	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(DATETIME).csv benchmark_test.js
#	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(PLAINTEXT_TEST)_$(DATETIME).csv plaintext_test.js
#	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(JSON_TEST)_$(DATETIME).csv json_test.js
#	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(DB_TEST)_$(DATETIME).csv db_test.js
#	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(QUERY_TEST)_$(DATETIME).csv queries_test.js
endef

python:
	@echo Running Python tests...
	$(call run_tests)

java:
	@echo Running Java tests...
	$(call run_tests)

go:
	@echo Running Go tests...
	$(call run_tests)

c++:
	@echo Running C++ tests...
	$(call run_tests)

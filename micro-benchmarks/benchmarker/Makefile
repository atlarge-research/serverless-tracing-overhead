SHELL := /bin/bash
DATE := $(shell date +%Y-%m-%d)
DATETIME := $(shell date +%Y-%m-%d_%H-%M)

export K6_WEB_DASHBOARD=true

RESULTS_DIR := results/$(DATE)
JSON_TEST := json
PLAINTEXT_TEST := plaintext
DB_TEST := db
QUERY_TEST := query

RESULT_FILE_PREFIX := testresults

# Target-specific variable values
plain: RESULT_FILE_PREFIX := plaintext
plain: TEST_FILENAME := plain_test.js

json: RESULT_FILE_PREFIX := json
json: TEST_FILENAME := json_test.js

db: RESULT_FILE_PREFIX := db
db: TEST_FILENAME := db_test.js

queries: RESULT_FILE_PREFIX := queries
queries: TEST_FILENAME := queries_test.js

updates: RESULT_FILE_PREFIX := updates
updates: TEST_FILENAME := updates_test.js

define run_test
	mkdir -p $(RESULTS_DIR)
	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(DATETIME).csv $(TEST_FILENAME)
endef

all: plain json db queries updates

plain json db queries updates:
	$(call run_test)

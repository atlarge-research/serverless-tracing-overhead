SHELL := /bin/bash
DATE := $(shell date +%Y-%m-%d)
DATETIME := $(shell date +%Y-%m-%d_%H-%M)

RESULTS_DIR := results/$(DATE)
TECHEMPOWER_TEST_DIR := techempower-tests
TESTS_DIR := tests
JSON_TEST := json
PLAINTEXT_TEST := plaintext
DB_TEST := db
QUERY_TEST := query

RESULT_FILE_PREFIX := testresults

run:
	docker compose -f docker-compose.yaml build
	docker compose -f docker-compose.yaml up -d

# Target-specific variable values
plain: RESULT_FILE_PREFIX := plaintext
te-plain: TEST_FILENAME := $(TECHEMPOWER_TEST_DIR)/plain_test.js

json: RESULT_FILE_PREFIX := json
te-json: TEST_FILENAME   := $(TECHEMPOWER_TEST_DIR)/json_test.js

db: RESULT_FILE_PREFIX := db
te-db: TEST_FILENAME := $(TECHEMPOWER_TEST_DIR)/db_test.js

queries: RESULT_FILE_PREFIX := queries
te-queries: TEST_FILENAME := $(TECHEMPOWER_TEST_DIR)/queries_test.js

updates: RESULT_FILE_PREFIX := updates
te-updates: TEST_FILENAME := $(TECHEMPOWER_TEST_DIR)/updates_test.js

test: RESULT_FILE_PREFIX := test
test: TEST_FILENAME := $(TESTS_DIR)/test.js

define run_test
	mkdir -p $(RESULTS_DIR)
	k6 run --out csv=$(RESULTS_DIR)/$(RESULT_FILE_PREFIX)_$(DATETIME).csv $(TEST_FILENAME)
endef



# te = TechEmpower
te-all: te-plain te-json te-db te-queries te-updates

te-plain te-json te-db te-queries te-updates test:
	$(call run_test)

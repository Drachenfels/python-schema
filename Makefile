TEST ?= tests

tests:
	./bin/run-tests.sh $(TEST)

.PHONY: tests

TEST ?= tests

tests:
	pytest -sv $(TEST)

.PHONY: tests

# The virtual environment is used when it exists
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python)

run:
	$(PYTHON) accountancy-manager.py

# The output of the app (SQL, debug prints) is only shown for the tests that fail
test:
	$(PYTHON) -m unittest discover -s test -t . -b

run_tests: test

.PHONY: run test run_tests

# Git variables

GIT_REPOSITORY_NAME := $(shell basename `git rev-parse --show-toplevel`)
GIT_VERSION := $(shell git describe --always --tags --long --dirty | sed -e 's/\-0//' -e 's/\-g.......//')

TARGET_DIRECTORY := ./dist

# -----------------------------------------------------------------------------
# The first "make" target runs as default.
# -----------------------------------------------------------------------------

.PHONY: default
default: help

# -----------------------------------------------------------------------------
# build
# -----------------------------------------------------------------------------

.PHONY: package
package: clean
	python3 -m build

# -----------------------------------------------------------------------------
# publish
# -----------------------------------------------------------------------------

.PHONY: test-publish
test-publish: package
	python3 -m twine upload --repository testpypi dist/*

.PHONY: publish
publish: package
    python3 -m twine upload dist/*	
	
# -----------------------------------------------------------------------------
# install
# -----------------------------------------------------------------------------

.PHONY: file-install
file-install: package
	pip3 install \
		--no-index \
		--find-links dist/ \
		--force-reinstall \
		senzing

.PHONY: test-install
test-install:
	pip3 install --index-url https://test.pypi.org/simple/ --no-deps senzing

# -----------------------------------------------------------------------------
# test
# -----------------------------------------------------------------------------

.PHONY: test
test:
	tests/test-imports.py

# -----------------------------------------------------------------------------
# Clean up targets
# -----------------------------------------------------------------------------

.PHONY: clean
clean:
	@rm -rf $(TARGET_DIRECTORY) || true

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------

.PHONY: help
help:
	@echo "List of make targets:"
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs

SHELL := /bin/sh

ifneq ("$(wildcard .env)", "")
	include .env
	export $(shell sed 's/=.*//' .env)
endif

check_defined = \
    $(strip $(foreach 1,$1, \
        $(call __check_defined,$1,$(strip $(value 2)))))
__check_defined = \
    $(if $(value $1),, \
        $(error Undefined $1$(if $2, ($2))$(if $(value @), \
                required by target `$@')))

.PHONY: install
install: ## Install requirements
	pipenv install

.PHONY: install-dev
install-dev: ## Install dev requirements
	pipenv install --dev

.PHONY: clean-pyc
clean-pyc: ## Remove python artifacts
	find pressbrief/ -name "__pycache__" -exec rm -rf {} +
	find pressbrief/ -name "*.pyc" -exec rm -f {} +
	find pressbrief/ -name "*.pyo" -exec rm -f {} +
	find pressbrief/ -name "*~" -exec rm -f {} +

.PHONY: clean-build
clean-build: ## Remove build artifact
	rm -rf pressbrief/build/
	rm -rf pressbrief/dist/
	rm -rf pressbrief/*.egg-info

.PHONY: isort
isort: ## Sort import statements
	pipenv run python -m isort --skip-glob=.tox --recursive pressbrief/

.PHONY: black
black: ## Check style with black
	pipenv run python -m black --line-length=119 --exclude=.tox pressbrief/

.DEFAULT_GOAL := help
.PHONY: help
help:
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
    printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
    }' $(MAKEFILE_LIST)

modules = src/ tests/


.PHONY: init
init:
	poetry install
	pip install -r docs/requirements.txt

.PHONY: clean
clean:
	rm -rf .coverage .hypothesis .mypy_cache .pytest_cache .tox *.egg-info
	rm -rf dist
	find . | grep -E "(__pycache__|docs_.*$$|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: format
format:
	poetry run black $(modules)
	poetry run isort $(modules)

.PHONY: mypy
mypy:
	poetry run mypy --pretty $(modules) --strict

.PHONY: flake8
flake8:
	poetry run flake8 $(modules)

.PHONY: format-check
format-check:
	poetry run black --check --diff $(modules)
	poetry run isort --check-only --diff $(modules)

.PHONY: check
check: format-check flake8 mypy

nice: format check

.PHONY: test
test:
	poetry run pytest --cov=pyintervals --cov-fail-under=95

.PHONY: docs
docs:
	@touch docs/api.rst
	make -C docs/ html

.PHONY: publish
publish:
	rm -rf dist/*
	poetry build
	twine upload dist/*

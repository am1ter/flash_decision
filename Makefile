.PHONY: help
help:  # Show help
		echo 'TBD'

.PHONY: run-prod
run-prod:  # Lint backend code
		cd flash_backend \
		&& export ENVIRONMENT=production \
		&& export WORK_DIR=. \
		&& poetry run python -m main

.PHONY: run-dev
run-dev:  # Lint backend code
		cd flash_backend \
		&& export ENVIRONMENT=development \
		&& export WORK_DIR=. \
		&& poetry run python -m main

.PHONY: lint-backend
lint-backend:  # Lint backend code
		poetry run ruff ./flash_backend

.PHONY: lint-tests
lint-tests:  # Lint tests code
		poetry run ruff ./tests
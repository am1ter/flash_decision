.PHONY: run-prod
run-prod:  # Run backend in production environment
		cd flash_backend \
		&& export ENVIRONMENT=production \
		&& poetry run python -m main

.PHONY: run-dev
run-dev:  # Run backend in dev environment
		cd flash_backend \
		&& export ENVIRONMENT=development \
		&& poetry run python -m main

.PHONY: run-debug
run-debug:  # Run backend in debug mode (dev environment + additional logs)
		cd flash_backend \
		&& export ENVIRONMENT=development \
		&& export DEBUG_MODE=True \
		&& poetry run python -m main

.PHONY: run-tests-unit
run-tests-unit:  # Run backend server in prod environment and run unit tests
		cd flash_backend/ \
		&& export ENVIRONMENT=production \
		&& poetry run python -m unittest discover -v -s ./tests -p test_unit_*.py -t . \

.PHONY: run-tests-integration
run-tests-integration:  # Run backend server in prod environment and run integration tests
		cd flash_backend/ \
		&& export ENVIRONMENT=production \
		&& poetry run python -m unittest discover -v -s ./tests -p test_integration_*.py -t . \

.PHONY: shutdown
shutdown:  # Shutdown python backend server
		kill $$(lsof -i :$(BACKEND_PORT) | grep "^python" |  awk '{print $$2}') || true \
		&& clear \
		&& echo "Shutdown server completed"

.PHONY: pre-commit
pre-commit:  # Run pre-commit checks
		cd flash_backend \
		&& pre-commit run --all-files --config ./flash_backend/.pre-commit-config.yaml

.PHONY: migrate-create
migrate-create:  # Create db migations using db scheme from env. Use args: `env=` to `msg=`
		cd flash_backend \
		&& export ENVIRONMENT=$(env) \
		&& alembic --name $(env) revision --autogenerate -m "$(msg)"

.PHONY: migrate-apply
migrate-apply:  # Apply alembic migrations using db scheme from env. Use args: `env=`
		cd flash_backend \
		&& export ENVIRONMENT=$(env) \
		&& alembic --name $(env) upgrade head

# Default environments variables
BACKEND_PORT ?= 8001

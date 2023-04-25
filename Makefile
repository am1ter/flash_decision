.PHONY: run-prod
run-prod:  # Run backend in production environment
		cd flash_backend \
		&& export ENVIRONMENT=production \
		&& export WORK_DIR=. \
		&& poetry run python -m main

.PHONY: run-dev
run-dev:  # Run backend in dev environment
		cd flash_backend \
		&& export ENVIRONMENT=development \
		&& export WORK_DIR=. \
		&& poetry run python -m main

.PHONY: run-debug
run-debug:  # Run backend in debug mode (dev environment + additional logs)
		cd flash_backend \
		&& export ENVIRONMENT=development \
		&& export WORK_DIR=. \
		&& export DEBUG_MODE=True \
		&& poetry run python -m main

.PHONY: run-tests-unit
run-tests-unit:  # Run backend server in prod environment and run unit tests
		make run-prod \
		& poetry run python -m unittest discover ./tests/unit/ \
		&& make shutdown

.PHONY: shutdown
shutdown:  # Shutdown python backend server
		kill $$(lsof -i :$(PORT_BACKEND) | grep "^python" |  awk '{print $$2}') || true \
		&& echo "Shutdown server completed"

.PHONY: pre-commit
pre-commit:  # Run pre-commit checks
		pre-commit run --all-files

.PHONY: migrate-create
migrate-create:  # Create db migations using db scheme from env. Use arg `msg=` to set message text
		cd flash_backend/db \
		&& alembic revision --autogenerate -m "$(msg)"


.PHONY: migrate-apply
migrate-apply:  # Apply alembic migrations using db scheme from env.
		cd flash_backend/db \
		&& alembic upgrade head

# Default environments variables
PORT_BACKEND ?= 8001

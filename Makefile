.PHONY: run-prod
run-prod:  # Run backend in production environment
		cd backend;
		export ENVIRONMENT=production;
		poetry run python -m main

.PHONY: run-dev
run-dev:  # Run backend in dev environment
		cd backend;
		export ENVIRONMENT=development;
		poetry run python -m main

.PHONY: run-debug
run-debug:  # Run backend in debug mode (dev environment + additional logs)
		cd backend;
		export ENVIRONMENT=development;
		export DEBUG_MODE=True;
		poetry run python -m main

.PHONY: run-tests-unit
run-tests-unit:  # Run backend server in prod environment and run unit tests
		export ENVIRONMENT=production;
		poetry run python -m unittest discover -v -s ./backend/tests -p test_unit_*.py -t ./backend \

.PHONY: docker-run-tests
.IGNORE:
docker-run-tests:  # Run docker compose to tests create test environment and run tests
		docker compose -f ./docker-compose.tests.yaml up -d --build \
		&& sleep 1 \
		&& docker compose -f ./docker-compose.tests.yaml run --rm \
			tests_backend poetry run python -m unittest discover -v -s ./tests -p test_*.py -t . ;
		docker compose -f ./docker-compose.tests.yaml down;

.PHONY: shutdown
shutdown:  # Shutdown python backend server
		kill $$(lsof -i :$(BACKEND_PORT) | grep "^python" |  awk '{print $$2}') || true \
		&& clear \
		&& echo "Shutdown server completed"

.PHONY: pre-commit
pre-commit:  # Run pre-commit checks
		cd backend;
		pre-commit run --all-files --config ./backend/.pre-commit-config.yaml

.PHONY: migrate-create
migrate-create:  # Create db migations using db scheme from env. Use args: `env=` to `msg=`
		cd backend;
		export ENVIRONMENT=$(env);
		poetry run alembic --name $(env) revision --autogenerate -m "$(msg)"

.PHONY: migrate-apply
migrate-apply:  # Apply alembic migrations using db scheme from env. Use args: `env=`
		cd backend;
		export ENVIRONMENT=$(env);
		poetry run alembic --name $(env) upgrade head

# Default environments variables
BACKEND_PORT ?= 8001

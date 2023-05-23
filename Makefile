.PHONY: docker-up-db
docker-up-db:  # Run docker compose to run db
		docker compose --env-file=.env.prod -f ./docker-compose.prod.yaml --profile db up -d --build

.PHONY: docker-up-prod
docker-up-prod:  # Run docker compose to run backend in prod environment
		docker compose --env-file=.env.prod -f ./docker-compose.prod.yaml --profile backend up -d --build

.PHONY: docker-up-dev
docker-up-dev:  # Run docker compose to run backend in dev environment
		docker compose --env-file=.env.dev -f ./docker-compose.prod.yaml -f ./docker-compose.dev.yaml --profile backend up -d --build

.PHONY: docker-run-tests
.IGNORE:
docker-run-tests:  # Run docker compose to tests create test environment and run tests
		docker compose --env-file=.env.tests -f ./docker-compose.tests.yaml run --rm fd_tests;
		docker compose --env-file=.env.tests -f ./docker-compose.tests.yaml down --rmi local

.PHONY: docker-down
docker-down:  # Shutdown and remove containers for backend in prod environment
		docker compose --env-file=.env.prod -f ./docker-compose.prod.yaml --profile backend --profile db down;
		docker compose --env-file=.env.tests -f ./docker-compose.tests.yaml down --rmi local

.PHONY: run-tests-unit
run-tests-unit:  # Run backend server in prod environment and run unit tests
		export ENVIRONMENT=production;
		poetry -C ./backend run \
			python -m unittest discover -v -s ./backend/tests -p test_unit_*.py -t ./backend

.PHONY: shutdown
shutdown:  # Shutdown local python backend server
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

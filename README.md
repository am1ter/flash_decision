# Flash decision

## Description

Flash Decision - an application designed to enhance your securities trading skills through comprehensive training.

## Solution Architecture

- Backend: Python 3.11
- Frontend: Vue.js 3
- SQL Database: PostgreSQL
- NoSQL Database: MongoDb
- Cache: Redis
- Observability: Grafana & Loki
- CI/CD: Docker containers & GitHub Actions

## Backend highlights

- Built with a focus on high maintainability, scalability, and testability, utilizing architectural patterns like Clean Architecture and Domain-Driven Design (DDD).
- Employs a modern technology stack: FastAPI, SQLAlchemy 2.0 with async ORM, Pandas 2.0 and Pydantic 2.0.
- Implements powerful logging using `structlog` and `rich`. JSON-based logs for production and aesthetically pleasing RICH logs for development.
- Offers database flexibility through `alembic` database migrations, with two separate schemas for production and development data.
- Embraces code conciseness using the `attrs` and `pydantic` libraries.
- Ensures high code cohesion and low coupling by applying the dependency inversion principle and employing various software design patterns:
  - Classic patterns: Factory, Singleton, Command, State, Observer, Facade.
  - DDD patterns: ValueObject, Aggregate, Repository, UnitOfWork.
- Enhances code quality by utilizing rich types through Generics and other techniques.
- Simplifies high-level configuration with the `Bootstrap` and `Config` modules, along with the use of environment variables via dot-env.
- Maintains a high-quality codebase with linters such as `mypy`, `ruff`, `black`, and `isort`.
- Minimizes low-quality code commits with `pre-commit` hooks.
- Ensures code reliability with extensive testing, covering 94% of the codebase through a combination of 98 integration and unit tests, evaluated using `pytest-cov`.

## Project highlights

- Over 100 tickets on the [project's Backend Kanban board](https://github.com/users/am1ter/projects/1) and [project's Frontend Kanban board](https://github.com/users/am1ter/projects/2)
- More than 180 uniform Git commits with detailed descriptions that are linked to Kanban tickets.
- The app can operate in 2 modes: production or development.
- A useful Makefile is included to automate and streamline the build process.

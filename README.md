# Flash decision
## Description
Flash Decision - an application designed to enhance your securities trading skills through comprehensive training.

## Backend highlights
- Built with a focus on high maintainability, scalability, and testability, utilizing architectural patterns like Clean Architecture and Domain-Driven Design (DDD).
- Employs a modern technology stack: FastAPI with async support, SQLAlchemy 2.0, and Pandas 2.0.
- Implements powerful logging using `structlog` and `rich`. JSON-based logs for production and aesthetically pleasing RICH logs for development.
- Offers database flexibility through `alembic` database migrations, with two separate schemas for production and development data.
- Embraces code conciseness using the `attrs` and `pydantic` libraries.
- Ensures high code cohesion and low coupling by applying the dependency inversion principle and employing various software design patterns:
    - Classic patterns: Factory, Singleton, Command, State, Observer, Facade.
    - DDD patterns: ValueObject, Aggregate, Repository, UnitOfWork.
- Simplifies high-level configuration with the `Bootstrap` and `Config` modules, along with the use of environment variables via dot-env.
- Maintains a high-quality codebase with linters such as `mypy`, `ruff`, `black`, and `isort`.
- Minimizes low-quality code commits with `pre-commit` hooks.
- Ensures code reliability with extensive testing, covering 94% of the codebase through a combination of 98 integration and unit tests, evaluated using `pytest-cov`.

## Solution Architecture
- Backend: Python
- Frontend: Vue.js
- SQL Database: PostgreSQL
- NoSQL Database: MongoDB
- Cache: Redis
- Observability: Grafana & Loki
- Deployment: Docker containers

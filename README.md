# Flash decision
Web application for testing & training securities trading skills.

### Solution Architecture
Application use microservice architecture and splitted into 2 services:
- Frontend app is a SPA based on Vue.js framework. Frontend is connected to backend via RESTful API.
- Backend app uses python with Flask and connected to database with SQLAlchemy.

Every service runs in a personal docker container.

### Setup
Use `docker-compose` to setup the solution

### Code cases
- Backend: snake_case
- Frontend: camelCase
- SQL: PascalCase
- API urls: kebab-case

# Flash decision
Web application for testing & training securities trading skills.

### Solution Architecture
Application use microservice architecture and splitted into the following services:
- Frontend app is a SPA based on Vue.js framework. Frontend is connected to backend via RESTful API.
- Backend app uses python with Flask and connected to main database with SQLAlchemy.
- PostgreSQL is used as a main database to store user-related data. Database migrations are served by Alembic.

Every service runs in a personal docker container.

### Setup using docker containers
1. Install docker and docker-compose 
   `sudo apt-get install docker`
   `sudo pip install docker-compose`
2. Clone repository `git clone https://github.com/am1ter/flash_decision.git`
3. Change directoryls `cd flash_decision`
4. Use command `docker-compose up -d` to setup the solution

### Code cases
- Backend: snake_case
- Frontend: camelCase
- SQL: PascalCase
- API urls: kebab-case
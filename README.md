# Flash decision
Web application for testing & training securities trading skills.

### Solution Architecture
Application use microservice architecture and splitted into the following services:
- Frontend app is a SPA based on Vue.js framework. Frontend is connected to backend via RESTful API.
- Backend app uses python with Flask and connected to main database with [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy).
- PostgreSQL is used as a main database to store user-related data. Database migrations are served by [SQLAlchemy Alembic](https://github.com/sqlalchemy/alembic).

Every service runs in a personal docker container.

### Setup using docker containers
1. Install docker and docker-compose
   ```
   sudo apt update
   sudo apt-get install docker
   sudo pip install docker-compose
   ```
2. Clone repository 
    ```
    git clone https://github.com/am1ter/flash_decision.git
    ```
3. Go to local copy of repository 
    ```
    cd flash_decision
    ```
4. Change default network settings: ports and custom nginx routing options
    ```
    nano .env
    ```
5. Use docker-compose command to setup the solution
    ```
    docker-compose up -d
    ```

### Code cases
- Backend: snake_case
- Frontend: camelCase
- SQL: PascalCase
- API urls: kebab-case
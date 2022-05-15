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

   sudo apt-get install ca-certificates curl gnupg lsb-release

   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   sudo apt update
   
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
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
    docker compose up -d
    ```

### Codebase features
- All python code formatted with ["The Black code style"](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html). Line length is enlarged up to 100 symblos. Single quotes are used instead of double quotes.
- All API endpoints designed according JSON:API specification (as RESTful as possible).
- The app is adapted to mobile devices (responsive design).
- 100% of code covered by comments.
- All use cases covered by end2end tests.
- Uniform code cases: 
    - Python: snake_case
    - API routes: kebab-case
    - SQL: PascalCase
    - JS: camelCase
    - CSS: kebab-case
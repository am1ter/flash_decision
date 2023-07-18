FROM postgres:latest

# Copy the script with sql initialization commands
COPY ./db/sql_init/init.sql /docker-entrypoint-initdb.d/

# Grant permissions to the script
RUN chmod +r /docker-entrypoint-initdb.d/init.sql

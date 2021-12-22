FROM python:3.8

# Copy requirements list to container to install it
WORKDIR /var/tmp
COPY ../requirements.txt /var/tmp

# Install all requirements
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

# Create app folder and copy app's files
RUN mkdir -p /usr/src/flash_backend
WORKDIR /usr/src/flash_backend

# Copy app files
COPY . .

# Install required python's libs
RUN pip install --no-cache-dir -r requirements.txt

# Open port
EXPOSE 8001

# Use db migrations and create default user
RUN chmod 777 ./entrypoint.sh
ENTRYPOINT ./entrypoint.sh
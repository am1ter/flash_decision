FROM python:3.8

# Install all requirements
RUN apt-get update \
    && apt-get install unixodbc -y \
    && apt-get install unixodbc-dev -y \
    && apt-get install -y unzip xvfb libxi6 libgconf-2-4 default-jdk dbus xvfb

# Download chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"
RUN apt -y update
RUN apt -y install google-chrome-stable

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
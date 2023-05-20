FROM python:3.8

# Read environment variables from docker-compose file
ARG BACKEND_URL
ARG FRONTEND_URL
ENV BACKEND_URL=${BACKEND_URL}
ENV FRONTEND_URL=${FRONTEND_URL}

# Install selenium requirements (chromedriver)
RUN apt-get update \
    && apt-get install -y unzip xvfb libxi6 libgconf-2-4 default-jdk wget
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"
RUN apt -y update
RUN apt -y install google-chrome-stable

# Create app folder and copy app's files
RUN mkdir -p /usr/src/flash_tests
WORKDIR /usr/src/flash_tests

# Copy app files
COPY . .

# Install required python's libs
RUN pip install --no-cache-dir -r requirements.txt

# Run app
CMD ["python", "test_e2e.py"]

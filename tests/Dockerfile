FROM python:3.8

# Read environment variables from docker-compose file
ARG URL_BACKEND
ARG URL_FRONTEND
ENV URL_BACKEND=${URL_BACKEND}
ENV URL_FRONTEND=${URL_FRONTEND}

# Install selenium requirements (chromedriver)
RUN apt-get update
RUN apt-get install -y unzip xvfb libxi6 libgconf-2-4 default-jdk 
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
# CMD ["python"]
CMD ["python", "test_e2e.py"]
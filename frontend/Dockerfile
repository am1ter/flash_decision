FROM node:14

# Read environment variables from docker-compose file
ARG BACKEND_URL
ENV VUE_APP_BACKEND_URL=${BACKEND_URL}

# Install simple http server for serving static content
RUN npm install -g http-server

# Create app folder and copy files
WORKDIR /usr/src/app

# Copy app
COPY . .

# Install project dependencies
RUN npm install

# Build app for production with minification
RUN npm run build

# Open port
EXPOSE 8000

# Run app
CMD ["http-server", "dist", "--cors" , "-p 8000"]
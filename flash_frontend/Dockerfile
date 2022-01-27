FROM node:14

# Read environment variables from docker-compose file
ARG PORT_BACKEND
ARG FORCE_AJAX_API_DEF_PORT
ENV VUE_APP_PORT_BACKEND=${PORT_BACKEND}
ENV VUE_APP_FORCE_AJAX_API_DEF_PORT=${FORCE_AJAX_API_DEF_PORT}

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
CMD ["http-server", "dist" , "-p 8000"]
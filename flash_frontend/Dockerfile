FROM node:14

# Install simple http server for serving static content
RUN npm install -g http-server

# Create app folder and copy files
WORKDIR /usr/src/app

# Install project dependencies
COPY package*.json ./
RUN npm install

# Copy app
COPY . .

# Build app for production with minification
RUN npm run build

# Open port
EXPOSE 8000

# Run app
CMD [ "http-server", "dist" , "-p 8000"]
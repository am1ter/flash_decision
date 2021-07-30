# Base image
FROM python

# Copy requirements list to container to install it
WORKDIR /var/tmp
COPY ../requirements.txt /var/tmp

# Install all requirements
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

RUN pip install --no-cache-dir -r requirements.txt
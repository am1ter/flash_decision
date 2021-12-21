FROM python

# Copy requirements list to container to install it
WORKDIR /var/tmp
COPY ../requirements.txt /var/tmp

# Install all requirements
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

# Create app folder and copy app's files
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Install required python's libs
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Open port
EXPOSE 8001

# Run app
CMD ["python", "flash_decision.py"]
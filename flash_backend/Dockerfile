# Load base image with all required libraries
FROM am1ter/flash_backend_baseimage:v1

# Create app folder and copy app's files
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .
COPY ../requirements.txt .

# Redundancy actions (in default case they won't have any affect)
# All required software has been already included in the base image
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

# Install required python's libs
RUN pip install --no-cache-dir -r requirements.txt

# Open port
EXPOSE 8001

# Run app
CMD ["python", "flash_decision.py"]
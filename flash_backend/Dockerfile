# Load base image with all required libraries
FROM am1ter/flash_backend_baseimage:v1

# Create app folder and copy files
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

# Redundancy actions (all requirements should be included in base image)
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

RUN pip install --no-cache-dir -r requirements.txt

# Open port
EXPOSE 8001

# Run app
CMD ["python", "flash_decision.py"]
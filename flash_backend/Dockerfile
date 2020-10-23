FROM flash_backend_baseimage

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "flash_decision.py"]
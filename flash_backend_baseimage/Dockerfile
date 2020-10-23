FROM python

WORKDIR /var/tmp
COPY ./requirements.txt /var/tmp

RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y

RUN pip install --no-cache-dir -r requirements.txt
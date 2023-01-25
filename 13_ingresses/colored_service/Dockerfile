FROM python:3.10-bullseye
ENV PYTHONUNBUFFERED=1

ENV LISTEN_PORT=8080
ENV PROM_LISTEN_PORT=9999
ENV DATABASE_HOST=mysql
ENV DATABASE_PORT=3306
ENV SHARED_STORAGE_PATH=/shared

WORKDIR /usr/src/app
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY my_webserver.py ./

CMD ["python", "./my_webserver.py"]
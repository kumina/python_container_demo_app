FROM python:3.6-stretch
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app
COPY requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
COPY my_webserver.py ./
CMD ["python", "./my_webserver.py"]
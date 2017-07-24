# Base our Python image off Alpine Linux. In this case we're using an
# unstable version of Alpine, called 'edge'. In practice, it may make
# more sense to pick a stable release, as long as effort is taken to
# stick to a recent version.
FROM alpine:edge

# Linux's <stdio.h> uses buffering when streams don't correspond to
# terminals (e.g., files). This is impractical for stdout and stderr, as
# it means logging output is not flushed immediately. By setting this
# environment variable, Python will disable stdout's and stderr's
# buffering.
ENV PYTHONUNBUFFERED=1

# It's easy to provide an application with additional environment
# variables for setting up a 12 factor app.
ENV LISTEN_PORT=80
ENV PROM_LISTEN_PORT=8080
ENV DATABASE_HOST=mysql
ENV DATABASE_PORT=3306
ENV SHARED_STORAGE_PATH=/shared

# Explicitly declare our requirements
COPY requirements.txt /requirements.txt

# Install dependencies of our web application from Alpine's package
# manager, APK. In this case we also depend on a Python module,
# prometheus_client, that is only available through Python's own package
# manager, Pip.
RUN echo http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories \
 && apk --update upgrade \
 && apk add python3 \
 && rm -rf /var/cache/apk/* \
 && pip3 install -r /requirements.txt

# Copy our simple web server into the container image.
COPY my_webserver.py /bin/my_webserver

# Invoke the Python application directly. If you want, you could add a
# small shell script in between that invokes some other commands prior
# to starting the web server. Do note that Python is also a pretty good
# language for doing that kind of stuff...
CMD ["/bin/my_webserver"]
